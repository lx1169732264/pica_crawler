import os
import winreg
from configparser import ConfigParser


# windows的文件夹不能带特殊字符,需要处理下文件夹名
def convert_file_name(name: str) -> str:
    for i, j in ("/／", "\\＼", "?？", "|︱", "\"＂", "*＊", "<＜", ">＞", ":-"):
        name = name.replace(i, j)
    name = name.replace("[中国翻訳]", "")
    name = name.replace("[DL版]", "")
    name = name.replace(" ", "")
    return name


def get_header():
    parser = ConfigParser()
    parser.read('./config.ini', encoding='utf-8')
    return dict(parser.items('header'))


def get_cfg(section: str, key: str):
    parser = ConfigParser()
    parser.read('./config.ini', encoding='utf-8')
    return dict(parser.items(section))[key]


def get_secret_cfg(key: str):
    parser = ConfigParser()
    parser.read('./secret-config.ini', encoding='utf-8')
    return dict(parser.items('system'))[key]


def filter_by_added(comics: list) -> list:
    f = open('downloaded.txt', 'r')
    ids = f.read().split('\n')
    return [i for i in comics if i['_id'] not in ids]


def save_comic_id(id: int):
    f = open('downloaded.txt', 'ab')
    f.write((str(id) + '\n').encode())
    f.close()


def save_comic_ids(ids: list):
    f = open('downloaded.txt', 'ab')
    if ids:
        f.write(('\n'.join(ids)).encode())
    f.close()


# 过滤掉指定分区的本子
def filter_by_categorie(comics: list) -> list:
    categories = get_cfg('filter', 'categories').split(',')
    return [i for i in comics if len(set(i['categories']).intersection(set(categories))) == 0]


def filter_comics(comics) -> list:
    res = filter_by_added(comics)
    res = filter_by_categorie(res)
    for c in comics:
        if c not in res:
            print('%s:%s:skip,filtered---------------' % (c['title'], c['_id']))
    return res


def doc_to_pic_url(i):
    return i['media']['fileServer'] + '/static/' + i['media']['path']


def list_partition(ls, size):
    return [ls[i:i + size] for i in range(0, len(ls), size)]


def process_exit():
    str = "taskkill /F /IM " + get_secret_cfg('proxy_soft_ware')
    os.system(str)

    # 如果从来没有开过代理 有可能健不存在 会报错
    INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                       r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                                       0, winreg.KEY_ALL_ACCESS)
    _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, 'ProxyEnable')
    winreg.SetValueEx(INTERNET_SETTINGS, 'ProxyEnable', 0, reg_type, 0)
