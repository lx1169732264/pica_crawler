from client import Pica
from util import *

pica_server = Pica()
pica_server.login()
pica_server.punch_in()

# 数据库
db_path = os.path.join('.', 'data', 'downloaded.db')
init_db(db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取数据库中已下载章节id
cursor.execute('SELECT comic_id FROM downloaded_comics')
result = cursor.fetchall()
db_ids = [o[0] for o in result]

# 获取downloaded.txt文件中历史已下载的漫画id
with open('downloaded.txt', 'r') as file:
    history_ids = [o.strip() for o in file.readlines()]
    # 通过差集得到没维护进数据库的漫画
    cids = list(set(history_ids) - set(db_ids))

total = len(cids)
for i in range(total):
    cid = cids[i]
    print(f'进度: {i + 1}/{total},{cid}')
    if cid:
        comic_info = pica_server.comic_info(cid)
        if 'data' in comic_info:
            comic = comic_info["data"]['comic']
            title = comic["title"]
            author = comic["author"]
            episodes = pica_server.episodes_all(cid, title)
            if episodes:
                mark_comic_as_downloaded(cid, title)
                for episode in episodes:
                    update_downloaded_episodes(cid, episode["title"], db_path)
                update_comic_data(comic, db_path)
        else:
            print(f'该漫画可能已被删除,{cid}')
