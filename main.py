# encoding: utf-8
import io
import json
import sys
import threading

from client import Pica
from util import *

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')


def download_comic(comic):
    cid = comic["_id"]
    title = comic["title"]
    author = comic["author"]
    categories = comic["categories"]
    print('%s | %s | %s | %s:downloading---------------------' % (cid, title, author, categories))
    res = []
    episodes = p.episodes_all(cid)
    for eid in episodes:
        page = 1
        while True:
            docs = json.loads(p.picture(cid, eid["order"], page).content)["data"]["pages"]["docs"]
            page += 1
            if docs:
                res.extend(docs)
            else:
                break
    pics = list(map(lambda i: i['media']['fileServer'] + '/static/' + i['media']['path'], res))

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
        print("downloaded:%d,total:%d,progress:%s%%" % (last, len(pics), int(last / len(pics) * 100)))
    # 记录已下载过的id
    f = open('./downloaded.txt', 'ab')
    f.write((str(cid) + '\n').encode())
    f.close()


p = Pica()
p.login()
p.punch_in()

# 排行榜/收藏夹的漫画
comics = filter_comics(p.leaderboard()) + p.my_favourite()

# 关键词订阅的漫画
keywords = os.environ["SUBSCRIBE_KEYWORD"].split(',')
for keyword in keywords:
    subscribe_comics = filter_comics(p.search_all(keyword))
    print('关键词%s : 订阅了%d本漫画' % (keyword, len(subscribe_comics)))
    comics += subscribe_comics

print('id | 本子 | 画师 | 分区')
for index in range(len(comics)):
    try:
        download_comic(comics[index])
        info = p.comic_info(comics[index]['_id'])
        if info["data"]['comic']['isFavourite']:
            p.favourite(comics[index]["_id"])
    except KeyError:
        print('download failed,' + str(index))
        continue

if not os.path.exists("./comics"):
    os.mkdir('./comics')
if not os.path.exists("./zips"):
    os.mkdir('./zips')
zip_file("./comics", "./zip", sys.maxsize)
