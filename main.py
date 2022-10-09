import json
import threading

import win32api

from client import Pica
from util import *
import time


def get_comic_pics(cid: int, p: Pica) -> []:
    res = []
    episodes = list(p.episodes(cid).json()["data"]["eps"]["docs"])
    episodes.reverse()
    for eid in episodes:
        page = 1
        while True:
            docs = json.loads(p.picture(cid, eid["order"], page).content)["data"]["pages"]["docs"]
            page += 1
            if docs:
                res.extend(docs)
            else:
                break
    return list(map(doc_to_pic_url, res))


def download_comic(comic):
    cid = comic["_id"]
    title = comic["title"]
    print('第%d本:%s:%s:downloading---------------------' % (index, title, cid))
    pics = get_comic_pics(cid, p)

    # todo pica服务器抽风了,没返回图片回来,有知道原因的大佬麻烦联系下我
    if not pics:
        print('第%d本:%s:%s:failed,图片数量为0?---------------------' % (index, title, cid))
        return

    path = get_secret_cfg('save_path') + convert_file_name(title) + '\\'
    if not os.path.exists(path):
        os.makedirs(path)
    pics_part = list_partition(pics, int(get_cfg('crawl', 'concurrency')))
    for part in pics_part:
        threads = []
        for pic in part:
            t = threading.Thread(target=p.download, args=(title, pics.index(pic), pic))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        last = pics.index(part[-1]) + 1
        print("%s:已下载:%d,总共:%d,进度:%s%%" % (title, last, len(pics), int(last / len(pics) * 100)))
    save_comic_id(cid)


win32api.ShellExecute(0, 'open', get_secret_cfg('proxy_soft_ware_path'), '', '', 1)
### 打开代理软件后需要让子弹飞一会儿,等它设置好代理的配置
time.sleep(3)

p = Pica()
p.login()

comics = filter_comics(p.leaderboard()) + p.my_favourite()
for index in range(len(comics)):
    try:
        download_comic(comics[index])
        info = p.comic_info(comics[index]['_id'])
        if info["data"]['comic']['isFavourite']:
            p.favourite(comics[index]["_id"])
    except KeyError:
        print('download failed,' + str(index))
        continue

process_exit()
