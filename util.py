import operator
import os
import random
import zipfile
from configparser import ConfigParser
from datetime import datetime


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


def get_latest_run_time():
    run_times = open('./run_time_history.txt', 'r').read().splitlines()
    #去掉空行
    run_times = [i for i in run_times if i]
    #最新一次记录的运行时间
    latest_run_time = run_times.pop()
    return datetime.strptime(latest_run_time, '%Y-%m-%d %H:%M:%S')


# 获取待下载的章节
def filter_comics(comic, episodes) -> list:
    ids = open('./downloaded.txt', 'r').read().split('\n')
    # 已下载过的漫画,执行增量更新
    if comic["_id"] in ids:
        episodes = [i for i in episodes if
                    (datetime.strptime(i['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ') - get_latest_run_time()).total_seconds() > 0]
    # 过滤掉指定分区的本子
    categories_rule = os.environ["CATEGORIES_RULE"]
    categories = os.environ["CATEGORIES"].split(',')
    # 漫画的分区和用户自定义分区的交集
    intersection = set(comic['categories']).intersection(set(categories))
    if categories:
        # INCLUDE: 包含任意一个分区就下载  EXCLUDE: 包含任意一个分区就不下载
        if (categories_rule == 'EXCLUDE' and len(intersection) == 0) or (
                categories_rule == 'INCLUDE' and len(intersection) > 0):
            return episodes
        else:
            return []
    return episodes


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


def zip_file(source_dir, target_dir, block_size=None):
    if not block_size:
        block_size = int(os.environ["EMAIL_ATTACH_SIZE"]) - 1
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    #单个压缩包的大小(MB)
    size_Mbit = block_size * 1024 * 1024
    count = 1
    createVar = locals()

    try:
        path_list = []
        file_size_temp = 0
        for dir_path, dir_name, file_names in os.walk(source_dir):
            # 要是不replace，就从根目录开始复制
            file_path = dir_path.replace(source_dir, "")
            # 实现当前文件夹以及包含的所有文件
            file_path = file_path and file_path + os.sep or ''
            for file_name in file_names:
                size = os.path.getsize(os.path.join(dir_path, file_name))
                #根据累计文件大小进行分卷压缩
                if file_size_temp + size > size_Mbit:
                    count = count + 1
                    file_size_temp = size
                else:
                    file_size_temp += size
                #var_index为压缩包文件名,左补零为了os.listdir这个函数能够正确地对数字进行排序
                var_index = str(count).zfill(2)
                #压缩包不存在则创建
                if not operator.contains(createVar, var_index):
                    createVar[var_index] = zipfile.ZipFile(os.path.join(target_dir, var_index + ".zip"), 'w', zipfile.ZIP_DEFLATED)
                #向压缩包写入文件
                createVar[var_index].write(os.path.join(dir_path, file_name), file_path + file_name)
        return path_list
    finally:
        for i in range(1, count):
            var_index = str(count).zfill(2)
            createVar[var_index].close()

def zip_subfolders(source_dir, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for folder_name in os.listdir(source_dir):
        folder_path = os.path.join(source_dir, folder_name)
        if os.path.isdir(folder_path):
            zip_path = os.path.join(target_dir, folder_name + '.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, source_dir))
