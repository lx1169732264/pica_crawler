import os
from configparser import ConfigParser


def convert_file_name(name: str) -> str:
    # windows的文件夹不能带特殊字符,需要处理下文件夹名
    for i, j in ("/／", "\\＼", "?？", "|︱", "\"＂", "*＊", "<＜", ">＞", ":-"):
        name = name.replace(i, j)
    name = name.replace(" ", "")
    return name


def get_cfg(section: str, key: str):
    parser = ConfigParser()
    parser.read('./config.ini', encoding='utf-8')
    return dict(parser.items(section))[key]


def get_secret_cfg(key: str):
    parser = ConfigParser()
    parser.read('./secret-config.ini', encoding='utf-8')
    return dict(parser.items('system'))[key]


def filter_comics(comics) -> list:
    # 过滤掉已下载的本子
    ids = open('downloaded.txt', 'r').read().split('\n')
    res = [i for i in comics if i['_id'] not in ids]

    # 过滤掉指定分区的本子
    categories = get_cfg('filter', 'categories').split(',')
    if categories:
        res = [i for i in comics if len(set(i['categories']).intersection(set(categories))) == 0]

    for c in comics:
        if c not in res:
            print('%s:%s:skip,filtered---------------' % (c['title'], c['_id']))
    return res


def list_partition(ls, size):
    return [ls[i:i + size] for i in range(0, len(ls), size)]


def download(self, name: str, i: int, url: str):
    path = get_secret_cfg('save_path') + convert_file_name(name) + '\\' + str(i + 1).zfill(4) + '.jpg'
    if os.path.exists(path):
        return

    f = open(path, 'wb')
    f.write(self.http_do("GET", url=url).content)
    f.close()

