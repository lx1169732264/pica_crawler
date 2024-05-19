# encoding: utf-8
import io
import json
import sys
import threading
import time
import traceback
import shutil
import requests

from client import Pica
from util import *

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

# only_latest: true增量下载    false全量下载
def download_comic(comic, only_latest):
    cid = comic["_id"]
    title = comic["title"]
    author = comic["author"]
    categories = comic["categories"]
    episodes = p.episodes_all(cid)
    # 增量更新
    if only_latest:
        episodes = filter_comics(comic, episodes)
    if episodes:
        print('%s | %s | %s | %s | %s:downloading---------------------' % (cid, title, author, categories,only_latest), flush=True)
    else:
        return

    pics = []
    for eid in episodes:
        page = 1
        while True:
            docs = json.loads(p.picture(cid, eid["order"], page).content)["data"]["pages"]["docs"]
            page += 1
            if docs:
                pics.extend(list(map(lambda i: i['media']['fileServer'] + '/static/' + i['media']['path'], docs)))
            else:
                break

    # todo pica服务器抽风了,没返回图片回来,有知道原因的大佬麻烦联系下我
    if not pics:
        return

    path = './comics/' + convert_file_name(title) + '/'
    if not os.path.exists(path):
        os.makedirs(path)
    pics_part = list_partition(pics, int(get_cfg('crawl', 'concurrency')))
    for part in pics_part:
        threads = []
        for pic in part:
            t = threading.Thread(target=download, args=(p, title, pics.index(pic), pic))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        last = pics.index(part[-1]) + 1
        print("downloaded:%d,total:%d,progress:%s%%" % (last, len(pics), int(last / len(pics) * 100)), flush=True)
    # 记录已下载过的id
    f = open('./downloaded.txt', 'ab')
    f.write((str(cid) + '\n').encode())
    f.close()
    # 下载每本漫画的间隔时间
    if os.environ.get("INTERVAL_TIME"):
        time.sleep(int(os.environ.get("INTERVAL_TIME")))


# 登录并打卡
p = Pica()
p.login()
p.punch_in()

# 排行榜的漫画
comics = p.leaderboard()

# 关键词订阅的漫画
keywords = os.environ.get("SUBSCRIBE_KEYWORD", "").split(',')
for keyword in keywords:
    subscribe_comics = p.search_all(keyword)
    print('关键词%s : 订阅了%d本漫画' % (keyword, len(subscribe_comics)), flush=True)
    comics += subscribe_comics

# 收藏夹的漫画
favourites = p.my_favourite_all()
print('收藏夹共计%d本漫画' % (len(favourites)), flush=True)
print('id | 本子 | 画师 | 分区', flush=True)

for comic in favourites + comics:
    try:
        # 收藏夹:全量下载  其余:增量下载
        download_comic(comic, comic not in favourites)
        info = p.comic_info(comic['_id'])
        # 收藏夹中的漫画被下载后,自动取消收藏,避免下次运行时重复下载
        if info["data"]['comic']['isFavourite']:
            p.favourite(comic["_id"])
    except:
        print('download failed,{},{},{}', comic['_id'], comic["title"], traceback.format_exc(), flush=True)
        continue

# 记录上次运行时间
f = open('./run_time_history.txt', 'ab')
f.write((str(datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')) + '\n').encode())
f.close()

# 打包成zip文件, 并删除旧数据 , 删除comics文件夹会导致docker挂载报错
if os.environ.get("PACKAGE_TYPE", "False") == "True":
    zip_subfolders('./comics', './output')
    for filename in os.listdir('./comics'):
        file_path = os.path.join('./comics', filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

# 发送消息通知
if os.environ.get("BARK_URL"):
    requests.get(os.environ.get("BARK_URL"))