# picacomic

- **根据GitHub官方要求，删除所有密钥。风头过了再说。**或者可以来这里：https://www.zhihu.com/people/ankikong/posts
- 批评某位开发者，居然用这个来牟利，不怕被请去喝茶，而且态度还极端恶劣。
- 隔壁被pica查水表了，我整理一下api
- [点这里有python实现](pica/pic2.py)，可以直接使用，**不要再提issue问怎么用了，跑不了说明是你代码的问题，自行抓包对比**
- 这是[Golang](https://github.com/AnkiKong/gopica)实现，可以运行

## 验证

``` golang

// header:
header := map[string]string{
    "api-key":           "",
    "accept":            "application/vnd.picacomic.com.v1+json",
    "app-channel":       "2",
    "time":              strconv.FormatInt(time.Now().Unix(), 10),
    "nonce":             "",
    "signature":         "",
    "app-version":       "2.2.1.2.3.3",
    "app-uuid":          "defaultUuid",
    "app-platform":      "android",
    "app-build-version": "44",
    "Content-Type":      "application/json; charset=UTF-8",
    "User-Agent":        "okhttp/3.8.1",
    "authorization":     token,
    "image-quality":     "original",
}

func getSign(header map[string]string, url string, method string) map[string]string {
    var nonce = ""
    var apiKey = ""
    var raw = strings.Replace(url, "https://picaapi.picacomic.com/",    "", 1) + header["time"] + nonce + method + apiKey
    raw = strings.ToLower(raw)
    h := hmac.New(sha256.New, []byte(""))
    h.Write([]byte(raw))
    header["signature"] = hex.EncodeToString(h.Sum(nil))
    return header
}
```

## Login 登陆

``` python
url: "https://picaapi.picacomic.com/auth/sign-in"
method: POST
body: {"email":"account","password":"password"}
response:
{
  "code": 200,
  "message": "success",
  "data": {
    "token": " " # 这个token放在headers的authorization就可以访问pica了
  }
}
```

## categories 主目录

``` python
url: "https://picaapi.picacomic.com/categories"
method: GET
response:
{
  "code": 200,
  "message": "success",
  "data": {
    "categories": [
      {
        "title": "援助嗶咔",
        "thumb": {
          "originalName": "help.jpg",
          "path": "help.jpg",
          "fileServer": "https://oc.woyeahgo.cf/static/"
        },
        "isWeb": true,
        "active": true,
        "link": "https://donate.woyeahgo.cf"
      },
      {
        "title": "嗶咔女皇總選",
        "thumb": {
          "originalName": "final-vote.jpeg",
          "path": "final-vote.jpeg",
          "fileServer": "https://oc.woyeahgo.cf/static/"
        },
        "isWeb": true,
        "active": true,
        "link": "https://final-vote.woyeahgo.cf"
      },
      {
        "title": "大家都在看",
        "thumb": {
          "originalName": "every-see.jpg",
          "path": "every-see.jpg",
          "fileServer": "https://oc.woyeahgo.cf/static/"
        },
        "isWeb": false,
        "active": true
      },
      {
        "_id": "5821859b5f6b9a4f93dbf6e9",
        "title": "嗶咔漢化", # 这个填进block的blockName，就可以获取对应分区的漫画
        "description": "未知",
        "thumb": {
          "originalName": "translate.png",
          "path": "f541d9aa-e4fd-411d-9e76-c912ffc514d1.png",
          "fileServer": "https://storage1.picacomic.com"
        }
      },

      ....
    ]
  }
}

```

## Comics

``` python
url: "https://picaapi.picacomic.com/comics"
method: GET
params:
  page: 分页，从1开始
  c: 分区名字，categories里面的title，如"嗶咔漢化"
  t: 标签的名字，由info返回数据里面的"tags"获得
  s: 排序依据
      ua: 默认
      dd: 新到旧
      da: 旧到新
      ld: 最多爱心
      vd: 最多指名
response
{
  "code": 200,
  "message": "success",
  "data": {
    "comics": {
      "docs": [
        {
          "_id": "5d56e4370bcf57397e60576b", #漫画id
          "title": "(C94)  ホカホカJS温泉 [中国翻訳]",
          "author": "アカタマ (桜吹雪ねる)",
          "pagesCount": 26,
          "epsCount": 1,
          "finished": true,
          "categories": [
            "短篇",
            "妹妹系"
          ],
          "thumb": {
            "originalName": "01.jpg",
            "path": "tobeimg/IrEYXQ_4J8Iq7JRpV9kMOYEqfhk15lxR7i9LmEbeU6U/fill/300/400/sm/0/aHR0cHM6Ly9zdG9yYWdlMS5waWNhY29taWMuY29tL3N0YXRpYy8xZDFkYjBhMC04NzY0LTQ5ZWEtYmUwYS0zMTRiZWUyYzQ1ZDcuanBn.jpg",
            "fileServer": "https://storage1.picacomic.com"
          },
          "id": "5d56e4370bcf57397e60576b",
          "likesCount": 310
        },
        ....
      ],
      "total": 29878,
      "limit": 20,
      "page": 1,
      "pages": 1494
    }
  }
}
```

## info 漫画详细信息

``` python
url: "https://picaapi.picacomic.com/comics/{bookId}"
method: GET
params:
  bookId: 漫画的id
response：
{
  "code": 200,
  "message": "success",
  "data": {
    "comic": {
      "_id": "5d56e4370bcf57397e60576b",
      "_creator": {
        "_id": "593019d53f532059f297efa7",
        "gender": "m",
        "name": "黎欧",
        "slogan": "emmm。。。二八七六八七八三九二（QQ代传邮箱）",
        "title": "萌新",
        "verified": false,
        "exp": 465280,
        "level": 68,
        "characters": [
          "knight"
        ],
        "role": "knight",
        "avatar": {
          "fileServer": "https://storage1.picacomic.com",
          "path": "bf30b2bc-5127-4144-86f0-b496b102c6d3.jpg",
          "originalName": "avatar.jpg"
        },
        "character": "https://www.picacomic.com/characters/frame_knight_1000.png?r=3"
      },
      "title": "(C94)  ホカホカJS温泉 [中国翻訳]",
      "description": "这猥琐大叔",
      "thumb": {
        "originalName": "01.jpg",
        "path": "tobeimg/IrEYXQ_4J8Iq7JRpV9kMOYEqfhk15lxR7i9LmEbeU6U/fill/300/400/sm/0/aHR0cHM6Ly9zdG9yYWdlMS5waWNhY29taWMuY29tL3N0YXRpYy8xZDFkYjBhMC04NzY0LTQ5ZWEtYmUwYS0zMTRiZWUyYzQ1ZDcuanBn.jpg",
        "fileServer": "https://storage1.picacomic.com"
      },
      "author": "アカタマ (桜吹雪ねる)",
      "chineseTeam": "D.E練習漢化",
      "categories": [
        "短篇",
        "妹妹系"
      ],
      "tags": [
      ],
      "pagesCount": 26,
      "epsCount": 1,
      "finished": true,
      "updated_at": "2019-08-16T17:13:27.191Z",
      "created_at": "2019-08-16T16:52:17.433Z",
      "allowDownload": true,
      "viewsCount": 31020,
      "likesCount": 316,
      "isFavourite": false,
      "isLiked": false,
      "commentsCount": 31
    }
  }
}
```

## episodes 漫画的分话

``` python
url: "https://picaapi.picacomic.com/comics/{bookId}/eps?page={page:1}"
method: GET
params:
  bookId: 漫画id
  page：分页，从1开始
response：
{
  "code": 200,
  "message": "success",
  "data": {
    "eps": {
      "docs": [
        {
          "_id": "5d56e4370bcf57397e60576c",
          "title": "第1話",
          "order": 1, #此话的id，epsId
          "updated_at": "2019-08-16T16:56:04.516Z",
          "id": "5d56e4370bcf57397e60576c"
        }
      ],
      "total": 1,
      "limit": 40,
      "page": 1,
      "pages": 1
    }
  }
}
```

## picture 漫画本体

``` python
url: "https://picaapi.picacomic.com/comics/5d56e4370bcf57397e60576b/order/{epsId}/pages?page={page:1}"
method: GET
params:
  epsId: 由api：episodes获得
  page：分页
response：
{
  "code": 200,
  "message": "success",
  "data": {
    "pages": {
      "docs": [
        {
          "_id": "5d56e4370bcf57397e60576d",
          "media": {
            "originalName": "01.jpg",
            "path": "7c73edbf-6aeb-4e3d-9b99-eef6644db92a.jpg",
            "fileServer": "https://storage1.picacomic.com"
          },
          "id": "5d56e4370bcf57397e60576d"
        },
        {
          "_id": "5d56e4370bcf57397e60576e",
          "media": {
            "originalName": "02.jpg",
            "path": "653cc9e0-1548-4cc3-bba0-d6e2e1bd9c18.jpg",
            "fileServer": "https://storage1.picacomic.com"
          },
          "id": "5d56e4370bcf57397e60576e"
        },
        ...
      ],
      "total": 26, # 总共由多少张图片
      "limit": 40, # 每页最多多少张图
      "page": 1,   # 第几页
      "pages": 1   # 总共有几页
    },
    "ep": {
      "_id": "5d56e4370bcf57397e60576c",
      "title": "第1話"
    }
  }
}

```

> 关于图片链接，由fileServer + "/static/" + path构成  
> 如"https://storage1.picacomic.com/static/653cc9e0-1548-4cc3-bba0-d6e2e1bd9c18.jpg"  

## recommend “看了這本子的人也在看”

``` python
url: "https://picaapi.picacomic.com/comics/{bookId}/recommendation"
method: GET
params:
  bookId: 漫画id
response：
{
  "code": 200,
  "message": "success",
  "data": {
    "comics": [
      {
        "_id": "5d09f7701edbf52f24b2819d",
        "title": "【明日方舟】凛冬の拘束调教（上篇）",
        "author": "大阿卡纳XIV",
        "pagesCount": 18,
        "epsCount": 1,
        "finished": false,
        "categories": [

        ],
        "thumb": {
          "originalName": "00封面_结果.jpg",
          "path": "tobeimg/Vm9AZXmlGOU42UBMCrcr5Qcmun-3zJ6lH9qwNFgBN8Q/fill/300/400/sm/0/aHR0cHM6Ly9zdG9yYWdlMS5waWNhY29taWMuY29tL3N0YXRpYy80YjEzZDhlOC03NzBlLTQ5ZjQtOTJhYS04NDA1OWNmOWZiMWMuanBn.jpg",
          "fileServer": "https://storage1.picacomic.com"
        },
        "likesCount": 4779
      },
      ...
    ]
  }
}
```

## keyword “大家都在搜”

``` python
url: "https://picaapi.picacomic.com/keywords"
method: GET
response:
{
  "code": 200,
  "message": "success",
  "data": {
    "keywords": [
      "C96",
      "嗶咔團長推薦",
      "肥宅",
      "老師",
      "校園",
      "校服",
      "廁所",
      "水平線",
      "冰菓",
      "一拳超人",
      "遊戲王",
      "小梅けいと",
      "40010",
      "ホムンクルス"
    ]
  }
}
```

## search 搜索

``` python
url: "https://picaapi.picacomic.com/comics/advanced-search?page={page:1}"
method: POST
PostData:
{
    "categories": ["長篇"], # 限定的分区，可以不加
    "keyword": "校服"， # 必选参数，搜索的关键词
    "sort": "" # 可选参数，与block里面的type一样
}
response：和block返回数据结构一样
```

## like 标记(不)喜欢此漫画

> 居然是标记一次就是like，标记第二次就是unlike。。。。  

``` python
url: "https://picaapi.picacomic.com/comics/{bookId}/like"
method: POST
PostData: None
response:
{
  "code": 200,
  "message": "success",
  "data": {
    "action": "like" # or “unlike”
  }
}
```

## comments 漫画的评论

``` python
url: "https://picaapi.picacomic.com/comics/{bookId}/comments?page={page:1}"
method: GET
params:
  bookId: id
  page: 分页
response:
{
  "code": 200,
  "message": "success",
  "data": {
    "comments": {
      "docs": [
        {
          "_id": "5d57e00b645b632d6f1cb3c8",
          "content": "看的我键盘侠想把她妈大腿塞那男的马眼里",
          "_user": {
            "_id": "5a1115cce1aa7c0729482566",
            "gender": "m",
            "name": "LittleMA",
            "title": "萌新",
            "verified": false,
            "exp": 390,
            "level": 2,
            "characters": [],
            "role": "member",
            "avatar": {
              "originalName": "avatar.jpg",
              "path": "fca509a6-7858-4cb1-aa8b-08dad24969de.jpg",
              "fileServer": "https://storage1.picacomic.com"
            }
          },
          "_comic": "5d57ddce1c04073986ea472d",
          "isTop": false,
          "hide": false,
          "created_at": "2019-08-17T11:07:55.671Z",
          "likesCount": 0,
          "commentsCount": 0,
          "isLiked": false
        }
      ],
      "total": 1,
      "limit": 20,
      "page": "1",
      "pages": 1
    },
    "topComments": []
  }
}
```

## post comment 发表评论

``` python
url: "https://picaapi.picacomic.com/comics/{bookId}/comments"
method: POST
PostData:
{
    "content": "......" # 评论的话
}
response:
# 测试用的账号等级太低了，无法评论，所以这是失败了的返回
{
    "code": 400,
    "error": "1019",
    "message": "cannot comment",
    "detail": ":( 07"
}

```

## favourite (取消)收藏

> 同样的，一次就收藏，第二次就是取消收藏

``` python
url: "https://picaapi.picacomic.com/comics/5d57de2c6f1d2a397190d81f/favourite"
method: POST
PostData: None
response:
{
  "code": 200,
  "message": "success",
  "data": {
    "action": "favourite" # or "un_favourite"
  }
}
```

## game 游戏区

``` python
url: "https://picaapi.picacomic.com/games?page={page:1}"
method: GET
response:
{
  "code": 200,
  "message": "success",
  "data": {
    "games": {
      "docs": [
        {
          "_id": "58296dee1cc00b5d50b1b5fe", # 游戏id gameId
          "title": "機動戰隊",
          "version": "2.1",
          "publisher": "即时弹道运算引擎打造热血像素机甲格斗手游",
          "suggest": true,
          "adult": false,
          "android": true,
          "ios": false,
          "icon": {
            "originalName": "0608_1.jpg",
            "path": "a7fe934b-a0c3-466e-8d38-4345c1ecf559.jpg",
            "fileServer": "https://storage1.picacomic.com"
          },
          "likesCount": 16036
        },
        {
          "_id": "5d511f6779f8d4028e63c0a7",
          "title": "戀花綻放櫻飛時",
          "version": "1.0.0",
          "publisher": "ぱれっと",
          "suggest": false,
          "adult": true,
          "android": true,
          "ios": true,
          "icon": {
            "originalName": "snap001.jpg",
            "path": "ef6137dc-fabd-4085-9743-a1763a284aac.jpg",
            "fileServer": "https://storage1.picacomic.com"
          },
          "likesCount": 858
        },
      ],
      "total": 67,
      "limit": 100,
      "page": 1,
      "pages": 1
    }
  }
}
```

## gameInfo 游戏信息

``` python
url: "https://picaapi.picacomic.com/games/{gameId}"
method: GET
params:
  gameId: 游戏id
response：
{
  "code": 200,
  "message": "success",
  "data": {
    "game": {
      "_id": "5d354f5b30dda25b3b542dbb",
      "title": "CLANNAD",
      "description": "-----\n【Key 20th Anniversary】\n【本游戲需要 ONS 模擬器游玩】\n【本游戲無 H 內容，全線所需時間大約為 40 小時以上，請斟酌後再進行下載】\n-----\n在某個小鎮，岡崎朋也因為家庭的因素而喪失了生活在這個地方的希望；與春原陽平為朋友，在光阪高等學校過著潦倒的生活，盼望終有一天能夠離開所在的小鎮。\n在高三的一個早晨，通往學校的坡道前發現了一個止步不前的女孩，在朋也認識了這個名為“古河渚”的女孩後，他的生活開始有了重大的變化。\n-----\nCLANNAD 在整個 ACGN 圈都是有名的游戲/動畫，它代表著人與小鎮，以及小鎮所代表的、人們聚集在一起互相支持著生活的“家族”。該作是 Key 的裡程碑之一。\n如果你覺得游戲流程過長，可前去觀看京阿尼出品的動畫。但南裡裡建議游玩游戲全線以獲得良好的催淚體驗。\n視頻所截取的是動畫第二季第 22 集中的片段，片中的歌名為“小さなてのひら”（小小的手心），也是游戲 TRUE END 的 ED 曲。\n\n謹以此次上傳紀念 Key 社 20 周年。",
      "version": "1.0.0",
      "icon": {
        "originalName": "0a7c125f-4f8e-4922-b9ab-275bc9e94e52.jpg",
        "path": "5d8d36d0-f0f7-4935-a9d7-1f9a0dd26fb7.jpg",
        "fileServer": "https://storage1.picacomic.com"
      },
      "publisher": "Key",
      "ios": true,
      "iosLinks": [
        "https://game.eroge.xyz/hhh.php?id=95" # 这就是下载链接
      ],
      "android": true,
      "androidLinks": [
        "https://game.eroge.xyz/hhh.php?id=95"
      ],
      "adult": false,
      "suggest": false,
      "downloadsCount": 0,
      "screenshots": [
        {
          "originalName": "0d20c59f-0b4e-4578-b1ff-d84106db4d1d.jpg",
          "path": "ec29f500-ddad-4dbd-99b8-fc39d0cc2f23.jpg",
          "fileServer": "https://storage1.picacomic.com"
        },
        {
          "originalName": "17f35358-ed6e-488c-a7a6-d51b5fe8c840.jpg",
          "path": "6557ade1-74b7-4089-82b8-d2e86d0304d1.jpg",
          "fileServer": "https://storage1.picacomic.com"
        },
        {
          "originalName": "3851ba34-d63a-42ac-a670-b8db61c32bfb.jpg",
          "path": "93292827-0ab3-4814-a195-eb8290a605ec.jpg",
          "fileServer": "https://storage1.picacomic.com"
        },
        {
          "originalName": "f5be85e6-8af4-4420-8dda-3d1c023332d6.jpg",
          "path": "7567ed74-f2e6-4c96-bf87-257061ab857a.jpg",
          "fileServer": "https://storage1.picacomic.com"
        }
      ],
      "androidSize": 763,
      "iosSize": 763,
      "updateContent": "在本游戲即將上傳的前夕，2019 年 7 月 18 日上午，京都動畫第一工作室遭到汽油縱火殺人襲擊，截至本游戲上傳時，事件已造成 34 人死亡，35 人受傷，且建築物全部損毀。\n\n京都動畫第一工作室是京都動畫動畫制作業務的核心所在。京阿尼向來以精細、扎實聞名。《涼宮春日的憂郁》《K-ON!》《紫羅蘭永恆花園》《冰菓》等作品，以及本次上傳的《CLANNAD》的 TV 動畫，均出自京阿尼之手，為觀眾們",
      "videoLink": "https://game.eroge.xyz/cl.mp4",
      "updated_at": "2019-08-07T19:36:41.991Z",
      "created_at": "2019-07-22T05:53:31.536Z",
      "likesCount": 2205,
      "isLiked": false,
      "commentsCount": 258
    }
  }
}
```

## person Info 个人信息

``` python
# 查看信息
url: "https://picaapi.picacomic.com/users/profile"
method: GET
response:
{
  "code": 200,
  "message": "success",
  "data": {
    "user": {
      "_id": "", # 你的id
      "birthday": "", # 填写的生日
      "email": "", # 注册邮箱
      "gender": "bot",
      "name": "", # 你的昵称
      "title": "萌新",
      "verified": false, # 是否验证，未验证的话没法评论
      "exp": 0,
      "level": 1,
      "characters": [],
      "created_at": "", # 注册时间
      "isPunched": false
    }
  }
}
# 更新自我介绍
method: PUT
PutData:
{
    "slogan": "" # 填这里
}
response：
{
  "code": 200,
  "message": "success"
}
```

## favourite 已收藏漫画

``` python
url: "https://picaapi.picacomic.com/users/favourite?s=dd&page={page:1}"
method: GET
response:
  和block返回的数据结构一样
```

## my comment 我的评论

``` python
url: "https://picaapi.picacomic.com/users/my-comments?page={page:1}"
method: GET
response:
{
  "code": 200,
  "message": "success",
  "data": {
    "comments": {
      "docs": [
        # 这里数据结构长什么样子我也不知道
      ],
      "total": 0,
      "limit": 20,
      "page": "1",
      "pages": 1
    }
  }
}
```

## change password 修改密码

``` python
url: "https://picaapi.picacomic.com/users/password"
method: PUT
PutData:
{
    "new_password": "",
    "old_password": ""
}
response:
{
  "code": 200,
  "message": "success"
}
```
