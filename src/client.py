import hashlib
import hmac
import json
import os
from configparser import ConfigParser
from datetime import datetime
from time import time
from urllib.parse import urlencode
import logging

import requests
import urllib3
from util import get_cfg

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base = "https://picaapi.picacomic.com/"


class Pica:
    Order_Default = "ua"  # 默认
    Order_Latest  = "dd"  # 新到旧
    Order_Oldest  = "da"  # 旧到新
    Order_Loved   = "ld"  # 最多爱心
    Order_Point   = "vd"  # 最多指名

    def __init__(self) -> None:
        self.__s = requests.session()
        self.__s.verify = False
        parser = ConfigParser()
        parser.read('./config/config.ini', encoding='utf-8')
        self.headers = dict(parser.items('header'))
        self.timeout = int(get_cfg("crawl", "request_time_out", 10))

    def http_do(self, method, url, **kwargs):
        kwargs.setdefault("allow_redirects", True)
        header = self.headers.copy()
        ts = str(int(time()))
        raw = url.replace(base, "") + str(ts) + header["nonce"] + method + header["api-key"]
        hc = hmac.new(get_cfg("param", "pica_secret_key").encode(), digestmod=hashlib.sha256)
        hc.update(raw.lower().encode())
        header["signature"] = hc.hexdigest()
        header["time"] = ts
        kwargs.setdefault("headers", header)
        proxy = get_cfg("param", "request_proxy")
        if proxy:
            proxies = {'http': proxy, 'https': proxy}
        else:
            proxies = None
        response = self.__s.request(
            method=method, url=url, verify=False, 
            proxies=proxies, timeout=self.timeout, **kwargs
        )
        return response

    def login(self):
        url = base + "auth/sign-in"
        send = {
            "email": get_cfg('param', 'pica_account'), 
            "password": get_cfg('param', 'pica_password')
        }
        response = self.http_do("POST", url=url, json=send).text
        print("login response:{}".format(response), flush=True)
        if json.loads(response)["code"] != 200:
            raise Exception('PICA_ACCOUNT/PICA_PASSWORD ERROR')
        if 'token' not in response:
            raise Exception('PICA_SECRET_KEY ERROR')
        self.headers["authorization"] = json.loads(response)["data"]["token"]

    def comics(self, block="", tag="", order="", page=1):
        args = []
        if len(block) > 0:
            args.append(("c", block))
        if len(tag) > 0:
            args.append(("t", tag))
        if len(order) > 0:
            args.append(("s", order))
        if page > 0:
            args.append(("page", str(page)))
        params = urlencode(args)
        url = f"{base}comics?{params}"
        return self.http_do("GET", url).json()

    # 排行榜
    def leaderboard(self) -> list:
        # tt的可选值: H24, D7, D30   分别代表每天/周/月
        args = [("tt", 'H24'), ("ct", 'VC')]
        params = urlencode(args)
        url = f"{base}comics/leaderboard?{params}"
        res = self.http_do("GET", url)
        return json.loads(res.content.decode("utf-8"))["data"]["comics"]

    # 获取本子详细信息
    def comic_info(self, book_id):
        url = f"{base}comics/{book_id}"
        res = self.http_do("GET", url=url)
        return json.loads(res.content.decode())

    # 获取本子的章节 一页最大40条
    def episodes(self, book_id, current_page):
        url = f"{base}comics/{book_id}/eps?page={current_page}"
        return self.http_do("GET", url=url)

    # 获取本子的全部章节
    def episodes_all(self, book_id, title: str) -> list:
        try:
            first_page_data = self.episodes(book_id, current_page=1).json()
            if 'data' not in first_page_data:
                logging.info(f'Chapter information missing, this comic may have been deleted, {title}, {book_id}')
                return []

            # 'total' represents the total number of chapters in the comic, 
            # while 'pages' indicates the number of pages needed to paginate the chapter data.
            total_pages    = first_page_data["data"]["eps"]["pages"]
            total_episodes = first_page_data["data"]["eps"]["total"]
            episode_list  = list(first_page_data["data"]["eps"]["docs"])
            while total_pages > 1:
                additional_episodes = self.episodes(book_id, total_pages).json()["data"]["eps"]["docs"]
                episode_list.extend(list(additional_episodes))
                total_pages -= 1
            episode_list = sorted(episode_list, key=lambda x: x['order'])
            if len(episode_list) != total_episodes:
                raise Exception('wrong number of episodes,expect:' + 
                    total_episodes + ',actual:' + len(episode_list)
                )
        except KeyError as e:
            logging.error(f"Comic {title} has been MISSING. KeyError: {e}")
        except Exception as e:
            logging.error(f"An error occurred while fetching episodes for comic {title}. Error: {e}")
        return episode_list

    # 根据章节获取图片
    def picture(self, book_id, ep_id, page=1):
        url = f"{base}comics/{book_id}/order/{ep_id}/pages?page={page}"
        return self.http_do("GET", url=url)

    def search(self, keyword, page=1, sort=Order_Latest):
        url = f"{base}comics/advanced-search?page={page}"
        res = self.http_do("POST", url=url, json={"keyword": keyword, "sort": sort})
        return json.loads(res.content.decode("utf-8"))["data"]["comics"]

    def search_all(self, keyword):
        subscribed_comics = []
        if keyword:
            total_pages_num = self.search(keyword)["pages"]
            for current_page in range(1, total_pages_num + 1):
                page_docs = self.search(keyword, current_page)["docs"]

                # Filter comics based on subscription date
                recent_comics = [comic for comic in page_docs if
                    (
                        (
                            datetime.now() - 
                            datetime.strptime(comic["updated_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
                        ).days
                    ) <= int(get_cfg('filter', 'subscribe_days'))]
                subscribed_comics += recent_comics

                # Check if any comics in the current page exceed the subscribe time limit.
                # If there are any comics that do not meet the time criteria, it is assumed
                # that subsequent pages will also contain outdated comics, so the search
                # is stopped early to save unnecessary requests.
                if len(page_docs) != len(recent_comics):
                    break

        return subscribed_comics

    def categories(self):
        url = f"{base}categories"
        return self.http_do("GET", url=url)

    # 收藏/取消收藏本子
    def favourite(self, book_id):
        url = f"{base}comics/{book_id}/favourite"
        return self.http_do("POST", url=url)

    # 获取收藏夹-分页
    def my_favourite(self, page=1):
        url = f"{base}users/favourite?page={page}"
        res = self.http_do("GET", url=url)
        return json.loads(res.content.decode())["data"]["comics"]

    # 获取收藏夹-全部
    def my_favourite_all(self):
        comics = []
        pages = self.my_favourite()["pages"]
        for page in range(1, pages + 1):
            comics += self.my_favourite(page)["docs"]
        return comics

    # 打卡
    def punch_in(self):
        url = f"{base}/users/punch-in"
        res = self.http_do("POST", url=url)
        return json.loads(res.content.decode())
