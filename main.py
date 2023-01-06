# encoding: utf-8
import io
import json
import shutil
import smtplib
import sys
import threading
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from client import Pica
from util import *

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')


def download_comic(comic):
    cid = comic["_id"]
    title = comic["title"]
    print('%s | %s:downloading---------------------' % (title, cid))
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

if not os.path.exists("./comics"):
    os.mkdir('./comics')
if not os.path.exists("./zips"):
    os.mkdir('./zips')
zip_file("./comics", "./zips")

email_account = os.environ["EMAIL_ACCOUNT"]
smtpObj = smtplib.SMTP()
smtpObj.connect(os.environ["EMAIL_SERVER_HOST"])
smtpObj.login(email_account, os.environ["EMAIL_AUTH_CODE"])

for zipFile in os.listdir('./zips'):
    msg = MIMEMultipart()
    msg['From'] = Header(email_account)
    msg['Subject'] = Header('pica comics' + generate_random_str(), 'utf-8')
    att = MIMEText(open('./zips/' + zipFile, 'rb').read(), 'base64', 'utf-8')
    att["Content-Type"] = 'application/octet-stream'
    att["Content-Disposition"] = 'attachment; filename="' + zipFile + '"'
    msg.attach(att)
    msg.attach(MIMEText('今天夜间到明天白天，多云间阴天，有雷阵雨，局部雨势较大，气温度，吹偏南风级。' + generate_random_str(), 'html', 'utf-8'))
    smtpObj.sendmail(email_account, email_account, msg.as_string())
    # 短时间频繁发邮件容易被邮件服务器检测到, 给个较长的间隔时间
    time.sleep(20)
smtpObj.quit()

shutil.rmtree('./zips')
shutil.rmtree('./comics')
