# encoding: utf-8
import io
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from client import Pica
from util import *

#校验config.ini文件是否存在
config_dir = './config/config.ini'
if not os.path.isfile('./config/config.ini'):
    raise Exception(f"配置文件`{config_dir}`不存在,请参考`./config/config_backup.ini`进行配置")

# 配置日志
log_folder = './logs'
os.makedirs(log_folder, exist_ok=True)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 自定义生成日志文件名的函数
def get_log_filename(name):
    return os.path.join(log_folder, f'{name}_{datetime.now().strftime("%Y-%m-%d")}.log')

# create a new TimedRotatingFileHandler
log_handler = TimedRotatingFileHandler(
    get_log_filename('runing'),
    when='midnight',                                   # 每天轮转一次
    interval=1,                                        # 轮转周期为1天
    backupCount=int(get_cfg('crawl', 'backup_count', 30))  # 保留最近?天的日志文件
)
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(log_formatter)
log_handler.addFilter(InfoWarningFilter())

# create a new ERROR TimedRotatingFileHandler, only logs ERROR level and above! 
error_log_handler = TimedRotatingFileHandler(
    get_log_filename('ERROR'),
    when='midnight',                                   # 每天轮转一次
    interval=1,                                        # 轮转周期为1天
    backupCount=int(get_cfg('crawl', 'backup_count', 30))  # 保留最近?天的日志文件
)
error_log_handler.setLevel(logging.ERROR)  # 只记录 ERROR 级别及以上的日志
error_log_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler, error_log_handler]
)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
sys.stdout = LoggerRedirect(sys.stdout)


# only_latest: true增量下载    false全量下载
def download_comic(comic, db_path, only_latest, executor: ThreadPoolExecutor):
    cid        = comic["_id"]
    title      = comic["title"]
    author     = comic["author"]
    categories = comic["categories"]
    episodes   = pica_server.episodes_all(cid, title)
    is_detail  = get_cfg("crawl", "detail", "True") == "True"
    num_pages  = comic["pagesCount"] if "pagesCount" in comic else -1
    # 增量更新
    if only_latest:
        episodes = filter_comics(comic, episodes, db_path)
    if episodes:
        print(
            'downloading:[%s]-[%s]-[%s]-[is_favo:%s]-[total_pages:%d]' % 
            (title, author, categories, not only_latest, num_pages), 
            flush=True
        )
    else:
        return
    # 记录已下载过的id
    mark_comic_as_downloaded(cid, db_path)

    comic_path = os.path.join(".",
                              "comics",
                              f"{convert_file_name(author)}",
                              f"{convert_file_name(title)}"
                            )
    comic_path = ensure_valid_path(comic_path)

    for episode in episodes:
        chapter_title = convert_file_name(episode["title"])
        chapter_path  = os.path.join(comic_path, chapter_title)
        chapter_path  = Path(chapter_path)
        chapter_path.mkdir(parents=True, exist_ok=True)
        image_urls = []
        current_page = 1
        while True:
            page_data = json.loads(
                pica_server.picture(cid, episode["order"], current_page).content
            )["data"]["pages"]["docs"]
            current_page += 1
            if page_data:
                image_urls.extend(list(map(
                    lambda i: i['media']['fileServer'] + '/static/' + i['media']['path'],
                    page_data
                )))
            else:
                break
        if not image_urls:
            logging.error(f"No images found of chapter:{chapter_title} in comic:{title}")
            continue

        downloaded_count = 0
        futures = {
            executor.submit(download,
                pica_server, chapter_path,
                image_urls.index(image_url), image_url
            ): image_url
            for image_url in image_urls
        }
        for future in as_completed(futures):
            image_url = futures[future]
            try:
                future.result()
                downloaded_count += 1
            except Exception as e:
                current_image = image_urls.index(image_url) + 1
                episode_title = episode["title"]
                logging.error(f"Error downloading the {current_image}-th image"
                              f"in episode:{episode_title}"
                              f"in comic:{title}"
                              f"Exception:{e}")
                continue
        if is_detail:
            episode_title = episode["title"]
            print(
                f"[episode:{episode_title:<10}] "
                f"downloaded:{downloaded_count:>6}, "
                f"total:{len(image_urls):>4}, "
                f"progress:{int(downloaded_count / len(image_urls) * 100):>3}%",
                flush=True
            )
        if downloaded_count == len(image_urls):
            update_downloaded_episodes(cid, episode["title"], db_path)
        else:
            episode_title = episode["title"]
            logging.error(
                f"Failed to download the episodes:{episode_title} "
                f"of comic:{title}. "
                f"Currently, {downloaded_count} images(total_images:{len(image_urls)}) "
                "from this episode have been downloaded"
            )
    # 下载完成后,根据配置对漫画章节进行合并
    if get_cfg("param", "merge_episodes", "False") == "True":
        merge_episodes(comic_path)
    # 下载每本漫画的间隔时间
    time.sleep(int(get_cfg('crawl', "interval_time", 1)))


# 登录并打卡
pica_server = Pica()
pica_server.login()
pica_server.punch_in()

# 数据库
db_path = os.path.join('.', 'data', 'downloaded.db')
init_db(db_path)

# 排行榜的漫画
ranked_comics = pica_server.leaderboard()

# 关键词订阅的漫画
searched_comics = []
keywords = get_cfg('filter', 'subscribe_keyword').split(',')
for keyword in keywords:
    searched_comics_ = pica_server.search_all(keyword)
    print('关键词%s: 检索到%d本漫画' % (keyword, len(searched_comics_)), flush=True)
    searched_comics += searched_comics_

# 收藏夹的漫画
favourited_comics = pica_server.my_favourite_all()
print('已下载共计%d本漫画' % get_downloaded_comic_count(db_path), flush=True)
print('收藏夹共计%d本漫画' % (len(favourited_comics)), flush=True)
isChangeFavo = get_cfg("param", "change_favourite", "True") == "True"

concurrency = int(get_cfg('crawl', 'concurrency', 5))
# 创建线程池的代码不要放for循环里面
with ThreadPoolExecutor(max_workers=concurrency) as executor:
    for comic in (ranked_comics + favourited_comics + searched_comics):
        try:
            # 收藏夹:全量下载  其余:增量下载
            download_comic(comic, db_path, comic not in favourited_comics, executor)
            info = pica_server.comic_info(comic['_id'])
            # 在收藏夹的漫画下载完成后,根据配置决定是否需要自动取消收藏,避免下次运行时重复下载
            if info["data"]['comic']['isFavourite'] and isChangeFavo:
                pica_server.favourite(comic["_id"])
            update_comic_data(comic, db_path)
        except Exception as e:
            logging.error(
                'Download failed for {}, with Exception:{}'.format(comic["title"], e)
            )
            continue


# 打包成zip文件, 并删除旧数据 , 删除comics文件夹会导致docker挂载报错
if os.environ.get("PACKAGE_TYPE", "False") == "True":
    for folderName in os.listdir('./comics'):
        print(f"The comic [{folderName}] is being packaged")
        folder_path = os.path.join('./comics', folderName)
        if os.path.isdir(folder_path):
            for chapter_folder in os.listdir(folder_path):
                chapter_path = os.path.join(folder_path, chapter_folder)
                output_path  = os.path.join('./output', folderName, chapter_folder)
            if os.path.isdir(chapter_path):
                os.makedirs(output_path, exist_ok=True)
                zip_subfolders(chapter_path, output_path)

    # delete folders in comics
    if os.environ.get("DELETE_COMIC", "True") == "True":
        for fileName in os.listdir('./comics'):
            print(f"The comic [{fileName}] is being deleted")
            file_path = os.path.join('./comics', fileName)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)


# 发送消息通知
bark_url = get_cfg("param", "bark_url")
if bark_url:
    requests.get(
        bark_url + " " +
        f"排行榜漫画共计{len(ranked_comics)}" +
        f"关键词漫画共计{len(searched_comics)}" +
        f"收藏夹漫画共计{len(favourited_comics)}"
    )
print("RUN COMPLETED!")
