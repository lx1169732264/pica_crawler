import operator
import os
import random
import shutil
import zipfile
from configparser import ConfigParser
from datetime import datetime
import sqlite3
import json
import logging
import requests


def convert_file_name(name: str) -> str:
    if isinstance(name, list):
        name = "&".join(map(str, name))
    # 处理文件夹名中的特殊字符
    for i, j in ("/／", "\\＼", "?？", "|︱", "\"＂", "*＊", "<＜", ">＞", ":-"):
        name = name.replace(i, j)
    name = name.replace(" ", "")
    # 操作系统对文件夹名最大长度有限制,这里对超长部分进行截断,避免file name too long报错
    # linux是255字节,windows更大一些
    name = truncate_string_by_bytes(name, 255)
    return name

# 该方法的配置读取优先级为 环境变量 > config.ini > default_value默认值
# docker方式部署时, 只需配置环境变量, 无需重新构建镜像
# GitHub Actions方式部署时, 部分敏感信息不适合填进config.ini文件并上传至代码仓库, 也请配置进环境变量中
def get_cfg(section: str, key: str, default_value = ''):
    # 项目中用到的环境变量名统一是大写的, 这里对入参key做了大写转换
    config_value = os.environ.get(key.upper())
    if config_value:
        return config_value

    # 因为ConfigParser限制变量名是小写的, 在读取config.ini的配置,对入参key做了小写转换
    parser = ConfigParser()
    parser.read('./config/config.ini', encoding='utf-8')
    config_value = dict(parser.items(section))[key.lower()]
    if config_value:
        return config_value

    # 最后取默认值作为兜底
    return default_value


def get_latest_run_time():
    run_times = open('./run_time_history.txt', 'r').read().splitlines()
    #去掉空行
    run_times = [i for i in run_times if i]
    #最新一次记录的运行时间
    latest_run_time = run_times.pop()
    return datetime.strptime(latest_run_time, '%Y-%m-%d %H:%M:%S')


# 获取待下载的章节
def filter_comics(comic, episodes, db_path) -> list:
    # 已下载过的漫画,执行增量更新
    if is_comic_downloaded(comic["_id"], db_path):
        episodes = [episode for episode in episodes
            if not is_episode_downloaded(comic["_id"], episode["title"], db_path)]
    # 过滤掉指定分区的本子
    categories_rule = get_cfg('filter', 'categories_rule')
    categories = get_cfg('filter', 'categories').split(',')
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


def download(pica_server, folder_path: str, i: int, url: str, retries=3):
    for attempt in range(retries):
        path = os.path.join(folder_path, (str(i + 1).zfill(4)+'.jpg'))
        try:
            if os.path.exists(path):
                return
            response = pica_server.http_do("GET", url=url)
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(response.content)
                return
            else:
                print(f"Attempt {attempt + 1} failed for {url}, status code: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt+1} timeout for {url}", flush=True)
        except Exception as e:
            print(f"Attempt {attempt+1} error for {url}: {e}", flush=True)
    raise Exception(f"Failed to download {url} after {retries} attempts.")

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
                    createVar[var_index] = zipfile.ZipFile(
                        os.path.join(target_dir, var_index + ".zip"), 
                        'w', 
                        zipfile.ZIP_DEFLATED
                    )
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


def init_db(db_path='./downloaded.db'):
    """
    初始化数据库，创建表格用于存储已下载的漫画 ID。
    """
    #创建数据库文件的父目录
    dir_path = os.path.dirname(db_path)
    os.makedirs(dir_path, exist_ok=True)

    conn = sqlite3.connect(db_path)  # 连接到 SQLite 数据库，如果文件不存在，会自动创建
    cursor = conn.cursor()  # 获取一个游标对象
    
    # 创建一个表格（如果不存在）来存储已下载的漫画 ID
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS downloaded_comics (
        comic_id TEXT PRIMARY KEY,         -- comic_id 是主键，唯一标识每个漫画
        title TEXT,                        -- 漫画的标题
        author TEXT,                       -- 漫画的作者
        total_views INTEGER,               -- 漫画的总浏览量
        total_likes INTEGER,               -- 漫画的总点赞数
        pages_count INTEGER,               -- 漫画的总页数
        eps_count INTEGER,                 -- 漫画的章节数量
        finished BOOLEAN,                  -- 漫画是否完结
        categories TEXT,                   -- 漫画的分类，保存为字符串
        downloaded_episodes TEXT           -- 已下载章节的列表, json字符串
    )
    ''')
    
    conn.commit()
    conn.close()


def is_comic_downloaded(cid, db_path='./downloaded.db'):
    """
    检查漫画 ID 是否已经下载过。
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询数据库中是否存在该 comic_id
    cursor.execute('SELECT 1 FROM downloaded_comics WHERE comic_id = ?', (cid,))
    result = cursor.fetchone()
    
    conn.close()
    return result is not None  # 如果结果不为空，则表示已下载


def mark_comic_as_downloaded(cid, db_path='./downloaded.db'):
    """
    标记漫画为已下载，在数据库中插入该 comic_id。
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查是否已经存在这个 comic_id
    cursor.execute('SELECT comic_id FROM downloaded_comics WHERE comic_id = ?', (cid,))
    result = cursor.fetchone()

    # 如果 comic_id 不存在，插入到数据库 
    if not result:
        cursor.execute('INSERT OR IGNORE INTO downloaded_comics (comic_id) VALUES (?)', (cid,))
    
    conn.commit()
    conn.close()

def update_comic_data(comic, db_path='./downloaded.db'):
    """
    记录漫画信息
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查是否已经存在 comic_id
    cursor.execute('SELECT comic_id FROM downloaded_comics WHERE comic_id = ?', (comic['_id'],))
    result = cursor.fetchone()

    if result:
        cursor.execute('''
        UPDATE downloaded_comics
        SET
            title = ?, 
            author = ?, 
            total_views = ?, 
            total_likes = ?, 
            pages_count = ?, 
            eps_count = ?, 
            finished = ?, 
            categories = ?
        WHERE comic_id = ?
        ''', (
            comic['title'],                            # title
            comic['author'],                           # author
            comic['totalViews'],                       # total_views
            comic['totalLikes'],                       # total_likes
            comic['pagesCount'],                       # pages_count
            comic['epsCount'],                         # eps_count
            comic['finished'],                         # finished
            ','.join(comic['categories']),             # categories
            comic['_id']                               # comic_id
        ))

    conn.commit()
    conn.close()


def get_downloaded_comic_count(db_path='./downloaded.db'):
    """
    获取已下载漫画的数量。
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM downloaded_comics')
    count = cursor.fetchone()[0]  # 获取查询结果中的第一个值

    conn.close()
    return count


def update_downloaded_episodes(comic_id, episode_title, db_path='./downloaded.db'):
    """
    更新数据库中的已下载章节列表。
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取当前已下载章节信息
    cursor.execute('SELECT downloaded_episodes FROM downloaded_comics WHERE comic_id = ?', (comic_id,))
    result = cursor.fetchone()

    # 如果该漫画已存在，获取已下载章节列表
    if result and result[0]:
        downloaded_episodes = json.loads(result[0])
    else:
        downloaded_episodes = []

    # 添加新的已下载章节
    downloaded_episodes.append(episode_title)

    # 更新数据库中的章节列表
    cursor.execute('''
    UPDATE downloaded_comics 
    SET downloaded_episodes = ? 
    WHERE comic_id = ?
    ''', (json.dumps(downloaded_episodes), comic_id))
    
    conn.commit()
    conn.close()


def is_episode_downloaded(comic_id, episode_title, db_path='./downloaded.db') -> bool:
    """
    判断漫画的指定章节是否已下载。
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT downloaded_episodes FROM downloaded_comics WHERE comic_id = ?', (comic_id,))
    result = cursor.fetchone()

    # 如果该漫画的章节信息存在，检查是否已下载
    if result and result[0]:
        downloaded_episodes = json.loads(result[0])
        return episode_title in downloaded_episodes

    return False


class LoggerRedirect:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout

    def write(self, message):
        if message != '\n':
            logging.info(message.strip())
        self.original_stdout.write(message)
        self.flush()

    def flush(self):
        self.original_stdout.flush()


# 创建过滤器来只允许 INFO 和 WARNING 级别的日志
class InfoWarningFilter(logging.Filter):
    def filter(self, record):
        # 只允许 INFO 和 WARNING 级别的日志
        return record.levelno in [logging.INFO, logging.WARNING]

max_path_length = 110  # bibu bibu bibu
def ensure_valid_path(path):
    if len(path) > (max_path_length):
        print(f"Path too long, truncating: {path}")
        path = path[:(max_path_length)]  # 截断路径
    return path

def truncate_string_by_bytes(s, max_bytes):
    """
    截断字符串，使其字节长度不超过max_bytes。

    参数:
    s (str): 要截断的字符串。
    max_bytes (int): 字符串的最大字节长度。

    返回:
    str: 截断后的字符串。
    """
    # 将字符串编码为字节串（默认使用utf-8编码）
    encoded_str = s.encode('utf-8')

    # 检查字节串的长度
    if len(encoded_str) > max_bytes:
        # 截断字节串
        truncated_bytes = encoded_str[:max_bytes]

        # 确保截断后的字节串是一个有效的UTF-8编码（可能需要移除最后一个字节以形成完整的字符）
        # 这通过解码然后重新编码来实现，可能会丢失最后一个字符的一部分
        truncated_str = truncated_bytes.decode('utf-8', 'ignore').encode('utf-8')

        # 返回截断后的字符串（以字节形式编码然后解码回字符串）
        return truncated_str.decode('utf-8')
    else:
        # 如果不需要截断，则返回原始字符串
        return s

def merge_episodes(dir):
    """
    将漫画从各个章节子文件夹中提取出来, 合并到同一目录, 方便连续阅读
    合并前的目录结构: ./comics/漫画标题/章节名/图片
    合并后的目录结构: ./comics/漫画标题/图片

    参数:
    dir (str): 漫画所在文件夹
    """

    # 获取目标目录下的所有子文件夹(章节信息),按章节名排序
    subdirs = sorted([d for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))])

    # 存储每个子文件夹中的文件数量
    counts = []

    # 存储所有文件的完整路径，以便后续处理
    all_files = []

    # 遍历子文件夹，计算文件数量并收集文件路径
    for subdir in subdirs:
        subdir_path = os.path.join(dir, subdir)
        count = len([f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))])
        counts.append(count)

        # 获取章节下的所有图片,按图片名排序
        pics = os.listdir(subdir_path)
        pics.sort(key=lambda x: str(x.split('.')[0]))
        for filename in pics:
            if os.path.isfile(os.path.join(subdir_path, filename)):
                all_files.append((os.path.join(subdir_path, filename), subdir, count))

    # 确定最大文件数量，用于确定文件名填充宽度
    max_count = sum(counts) if counts else 0
    width = len(str(max_count))
    # 初始化全局文件计数器
    global_counter = 1

    # 遍历所有文件，复制并重命名
    for src_file, subdir, count in all_files:
        # 生成新的文件名，使用宽度进行零填充
        new_filename = f"{global_counter:0{width}d}{os.path.splitext(src_file)[1]}"

        # 复制文件到目标目录（这里直接复制到dir）
        shutil.copy2(src_file, os.path.join(dir, new_filename))

        # 更新全局计数器
        global_counter += 1

    # 删除各个章节的文件夹
    for subdir in subdirs:
        shutil.rmtree(os.path.join(dir,subdir))

    print(f"{dir}合并章节完成，共处理了 {global_counter - 1} 个文件")