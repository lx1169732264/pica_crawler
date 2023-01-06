import math
import os
import random
import zipfile
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


def filter_comics(comics) -> list:
    # 过滤掉已下载的本子
    ids = open('./downloaded.txt', 'r').read().split('\n')
    comics = [i for i in comics if i['_id'] not in ids]

    # 过滤掉指定分区的本子
    categories_rule = os.environ["CATEGORIES_RULE"]
    categories = os.environ["CATEGORIES"].split(',')
    if categories:
        if categories_rule == 'EXCLUDE':
            comics = [i for i in comics if len(set(i['categories']).intersection(set(categories))) == 0]
        else:
            comics = [i for i in comics if len(set(i['categories']).intersection(set(categories))) > 0]
    return comics


def list_partition(ls, size):
    return [ls[i:i + size] for i in range(0, len(ls), size)]


def download(self, name: str, i: int, url: str):
    path = './comics/' + convert_file_name(name) + '/' + str(i + 1).zfill(4) + '.jpg'
    if os.path.exists(path):
        return

    f = open(path, 'wb')
    f.write(self.http_do("GET", url=url).content)
    f.close()


def generate_random_str(str_length=16):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(str_length):
        random_str += base_str[random.randint(0, length)]
    return random_str


def zip_file(source_file, outputfile_path, block_size=49):
    if not os.path.exists(outputfile_path):
        os.mkdir(outputfile_path)
    size_Mbit = block_size * 1024 * 1024
    file_size_temp = 0
    for dir_path, dir_name, file_names in os.walk(source_file):
        # 要是不replace，就从根目录开始复制
        file_path = dir_path.replace(source_file, "")
        # 实现当前文件夹以及包含的所有文件
        file_path = file_path and file_path + os.sep or ''
        for file_name in file_names:
            file_size_temp += os.path.getsize(os.path.join(dir_path, file_name))
    count_sum = math.ceil(file_size_temp / size_Mbit)

    try:
        path_list = []
        createVar = locals()
        for i in range(1, (count_sum + 1)):
            zip = "f" + str(i) + ".zip"
            path_list.append(os.path.join(outputfile_path, zip))
            createVar['f' + str(i)] = zipfile.ZipFile(os.path.join(outputfile_path, zip), 'w', zipfile.ZIP_DEFLATED)
        count = 1
        file_size_temp = 0
        for dir_path, dir_name, file_names in os.walk(source_file):
            # 要是不replace，就从根目录开始复制
            file_path = dir_path.replace(source_file, "")
            # 实现当前文件夹以及包含的所有文件
            file_path = file_path and file_path + os.sep or ''
            for file_name in file_names:
                size = os.path.getsize(os.path.join(dir_path, file_name))
                if file_size_temp + size > size_Mbit:
                    count = count + 1
                    file_size_temp = size
                else:
                    file_size_temp += size
                createVar['f' + str(count)].write(os.path.join(dir_path, file_name), file_path + file_name)
        for i in range(1, (count_sum + 1)):
            createVar['f' + str(i)].close()
        return path_list
    finally:
        for i in range(1, (count_sum + 1)):
            createVar['f' + str(i)].close()
