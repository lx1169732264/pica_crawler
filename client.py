import hashlib
import hmac
import io
import json
import os
import sys
from configparser import ConfigParser
from time import time
from urllib.parse import urlencode

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base = "https://picaapi.picacomic.com/"

class Pica:
    Order_Default = "ua"  # 默认
    Order_Latest = "dd"  # 新到旧
    Order_Oldest = "da"  # 旧到新
    Order_Loved = "ld"  # 最多爱心
    Order_Point = "vd"  # 最多指名

    def __init__(self) -> None:
        self.__s = requests.session()
        self.__s.verify = False
        parser = ConfigParser()
        parser.read('./config.ini', encoding='utf-8')
        self.headers = dict(parser.items('header'))

    def http_do(self, method, url, **kwargs):
        kwargs.setdefault("allow_redirects", True)
        header = self.headers.copy()
        ts = str(int(time()))
        raw = url.replace(base, "") + str(ts) + header["nonce"] + method + header["api-key"]
        hc = hmac.new(os.environ["PICA_SECRET_KEY"].encode(), digestmod=hashlib.sha256)
        hc.update(raw.lower().encode())
        header["signature"] = hc.hexdigest()
        header["time"] = ts
        kwargs.setdefault("headers", header)
        response = self.__s.request(method=method, url=url, verify=False, **kwargs)
        return response

    def login(self):
        url = base + "auth/sign-in"
        send = {"email": os.environ.get("PICA_ACCOUNT"), "password": os.environ.get("PICA_PASSWORD")}
        __a = self.http_do("POST", url=url, json=send).text
        print("----login response---------")
        print(__a)
        print("----login response---------")
        if json.loads(__a)["code"] != 200:
            raise Exception('PICA_ACCOUNT/PICA_PASSWORD ERROR')
        if 'token' not in __a:
            raise Exception('PICA_SECRET_KEY ERROR')
        self.headers["authorization"] = json.loads(__a)["data"]["token"]

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

    #排行榜
    def leaderboard(self) -> list:
        #tt的可选值: H24, D7, D30   分别代表每天/周/月
        args = [("tt", 'H24'), ("ct", 'VC')]
        params = urlencode(args)
        url = f"{base}comics/leaderboard?{params}"
        res = self.http_do("GET", url)
        return json.loads(res.content.decode("utf-8"))["data"]["comics"]

    #获取本子详细信息
    def comic_info(self, book_id):
        url = f"{base}comics/{book_id}"
        res = self.http_do("GET", url=url)
        return json.loads(res.content.decode())

    #获取本子的章节
    def episodes(self, book_id, page=1):
        url = f"{base}comics/{book_id}/eps?page={page}"
        return self.http_do("GET", url=url)

    #根据章节获取图片
    def picture(self, book_id, ep_id, page=1):
        url = f"{base}comics/{book_id}/order/{ep_id}/pages?page={page}"
        return self.http_do("GET", url=url)

    def search(self, keyword, sort=Order_Default, page=1):
        url = f"{base}comics/advanced-search?page={page}"
        return self.http_do("POST", url=url, json={"keyword": keyword, "sort": sort})

    def categories(self):
        url = f"{base}categories"
        return self.http_do("GET", url=url)

    #收藏/取消收藏本子
    def favourite(self, book_id):
        url = f"{base}comics/{book_id}/favourite"
        return self.http_do("POST", url=url)

    #获取收藏夹
    def my_favourite(self):
        url = f"{base}users/favourite"
        res = self.http_do("GET", url=url)
        return json.loads(res.content.decode())["data"]["comics"]["docs"]

    #打卡
    def punch_in(self):
        url = f"{base}/users/punch-in"
        res = self.http_do("POST", url=url)
        return json.loads(res.content.decode())

