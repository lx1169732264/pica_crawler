import json
import threading
import time
import winreg

import win32api

from client import Pica
from util import *


def download_comic(comic):
    cid = comic["_id"]
    title = comic["title"]
    print('第%d本:%s:%s:downloading---------------------' % (index, title, cid))
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
    pics = list(map(lambda i: i['media']['fileServer'] + '/static/' + i['media']['path'], res))

    # todo pica服务器抽风了,没返回图片回来,有知道原因的大佬麻烦联系下我
    if not pics:
        print('第%d本:%s:%s:failed,图片数量为0---------------------' % (index, title, cid))
        return

    path = get_secret_cfg('save_path') + convert_file_name(title) + '\\'
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
        print("%s:已下载:%d,总共:%d,进度:%s%%" % (title, last, len(pics), int(last / len(pics) * 100)))
    # 记录已下载过的id
    f = open('downloaded.txt', 'ab')
    f.write((str(id) + '\n').encode())
    f.close()


win32api.ShellExecute(0, 'open', get_secret_cfg('proxy_soft_ware_path'), '', '', 1)
### 打开代理软件后需要让子弹飞一会儿,确保代理配置完毕
time.sleep(3)

p = Pica()
p.login()
p.punch_in()

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

# 关闭代理软件
os.system("taskkill /F /IM " + get_secret_cfg('proxy_soft_ware'))
# 清除系统的代理
INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                                   0, winreg.KEY_ALL_ACCESS)
_, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, 'ProxyEnable')
winreg.SetValueEx(INTERNET_SETTINGS, 'ProxyEnable', 0, reg_type, 0)
