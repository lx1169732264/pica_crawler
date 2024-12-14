# 项目简介

一个哔咔漫画的下载程序,基于python实现,欢迎各位绅士来捉虫
* 目前已实现按 排行榜/收藏夹/指定关键词 进行下载的功能
* 本项目是基于[AnkiKong大佬开源的项目](https://github.com/AnkiKong/picacomic)编写的,仅供技术研究使用,请勿用于其他用途,有问题可以提issue
* 麻烦给个star支持一下:heart:

## 下载的范围

### 排行榜
哔咔24小时排行榜内的所有漫画

### 收藏夹
收藏夹内的所有漫画,下载完成是否取消收藏取决于配置文件中的`CHANGE_FAVOURITE`, if ="True":自动取消收藏; elif ="False":不取消收藏

### 关键词订阅
`./config/config.ini`里的`subscribe_keyword`里配置若干个关键词,下载范围等同于在哔咔app里用关键词搜索到的所有漫画

### 部分漫画不会被下载的原因
排行榜/订阅的漫画会受到以下过滤逻辑的影响,**收藏夹则不会**(如果下载到本地后文件丢失了,可以通过放入收藏夹把它全量下载下来)

#### 过滤重复下载

`./data/downloaded.db`文件记录了已扫描过的漫画id, 并记录了成功下载过的漫画章节名和基本信息.
如果数据库文件中存在该漫画id, **则触发增量下载,跳过已下载的章节**, 否则触发全量下载.      
若采用GitHub Actions方式运行, 会将`./data/downloaded.db`文件提交到代码仓库以保存本次的运行结果. 若`GIT_TOKEN`配置错误则代码提交失败,从而导致漫画被重复下载和推送


#### 过滤分区
`config.ini`文件的``CATEGORIES``配置项可以配置0~n个哔咔的分区, 配置为空则代表不过滤

``CATEGORIES_RULE``可以配置为 INCLUDE: 包含任意一个分区就下载  EXCLUDE: 包含任意一个分区就不下载

> 部分漫画只打上了'短篇'/'长篇'这样单个分区,在配置为``INCLUDE``时,建议把比较常见的分区给填上,不然容易匹配不到漫画


#### 订阅的时间范围
对于订阅的漫画,如果 当天 - 订阅漫画的上传日 > `subscribe_days`,这本漫画将不再被下载


#### 检查日志文件
在文件夹`logs`下存储有运行日志文件，所有日志按天自动划分，自动删除超过`backup_count`天的日志。错误信息单独保存到`ERROR_*.log`中。

# 运行方式

## 本地运行
1. 参考`./config/config_backup.ini`构建个人配置文件`./config/config.ini`,缺少该文件项目将无法运行 
2. 开启科学上网 
3. 在项目根目录下运行`python ./src/main.py`. 漫画将被下载到`./comics`文件夹下, 同时将已下载的漫画维护进`./data/downloaded.db`文件中

## Docker 运行
> 因为`./config/config.ini`要配置的东西有点多, 推荐把项目clone下来, 改完配置后自行构建镜像

1. 参考`./config/config_backup.ini`构建个人配置文件`./config/config.ini`,缺少该文件项目将无法运行 
2. 修改`Dockerfile`文件中ENV环境变量的配置   
`PACKAGE_TYPE`: 参数为 True / False. 设置为True时, 会根据漫画名称压缩成zip包, 以供 Komga 等漫画库使用   
`DELETE_COMIC`: 参数为 True / False. 设置为True时, 会在压缩包生成后删除文件夹下的漫画( 避免docker容器占用过多硬盘 )
3. 在项目根目录下运行`docker build -t picacg-download:latest .`
4. 启动容器的脚本
```shell
docker run --name picacg-download-container -d 
    -v ./comics:/app/comics #挂载存放下载漫画图片的文件夹
    -v ./output:/app/output #挂载存放压缩包的文件夹(如果配置了需要打包)
    #-e 添加环境变量可以覆盖config.ini中的配置, 免去重新build的操作
    picacg-download:latest
```

## GitHub Actions运行

漫画将会以压缩包附件的形式推送到邮箱上,受限于邮件的附件大小限制,漫画会被打包为若干个压缩包,一次性可能会收到若干个邮件   
不同邮箱支持的最大邮件内容不同,qq/新浪是50mb,outlook是20mb,建议用大一点的,避免拆分的压缩包过多下载起来麻烦   
支持自动定时运行,无需搭建个人服务器,适合每天推送少量的漫画
1. fork本仓库
2. 新增Actions secrets

| Actions secrets          | 说明                                                         |
| --------------- | ------------------------------------------------------------ |
| PICA_SECRET_KEY | [AnkiKong提供的secret_key](https://zhuanlan.zhihu.com/p/547321040) |
| PICA_ACCOUNT    | 哔咔登录的账号                                               |
| PICA_PASSWORD   | 哔咔登录的密码                                               |
| EMAIL_ACCOUNT   | 接收漫画的邮箱                                               |
| EMAIL_AUTH_CODE | 邮箱的授权码,[参考qq邮箱的这篇文档](https://service.mail.qq.com/cgi-bin/help?subtype=1&&id=28&&no=1001256) |
| GIT_TOKEN       | [参考这篇文章](http://t.zoukankan.com/joe235-p-15152380.html),只勾选repo的权限,Expiration设置为No Expiration |

<img src="https://raw.githubusercontent.com/lx1169732264/Images/master/Actions%20secrets.png" width = "700" height = "350" alt="图片名称" align=center />

3. 参考`./config/config_backup.ini`调整个人配置文件`./config/config.ini`并上传至GitHub代码仓库(Actions secrets中已配置的内容空着不填即可)

4. 打开fork项目的workFlow开关

<img src="https://raw.githubusercontent.com/lx1169732264/Images/master/enableWorkFlow.png" width = "700" height = "350" alt="图片名称" align=center />

5. 修改`./.github/workflows/pica_crawler_actions.yml`配置文件. 如果需要邮箱推送,请修改`EMAIL_SERVER_HOST`等邮箱相关的配置

6. 手动触发一次,测试下能不能跑通

<img src="https://raw.githubusercontent.com/lx1169732264/Images/master/runWorkFlow.png" width = "500" height = "200" alt="图片名称" align=center />


**成功运行的截图:**   
<img src="https://raw.githubusercontent.com/lx1169732264/Images/master/%E6%88%90%E5%8A%9F%E8%BF%90%E8%A1%8C%E6%88%AA%E5%9B%BE.png" width = "700" height = "350" alt="图片名称" align=center />

7. 成功运行后,可以在这里下载到漫画的压缩包. 如果配置了邮箱推送功能,还可以查收邮件里的附件

<img src="https://raw.githubusercontent.com/lx1169732264/Images/master/pica-Artifacts.png" width = "700" height = "350" alt="图片名称" align=center />

* [我自己也fork了一份](https://github.com/PhantomStrikers/pica_crawler.git),每天都在自动运行的,可以通过这个项目的actions运行记录判断这个项目是否还能work


### 邮件压缩包的解压注意事项
1. 将所有邮件的压缩包下载至统一目录. (存在单个压缩包里可能只有半本漫画的情况),然后**全选**压缩包,右键**解压到当前文件夹**.  
2. 如果你在上个步骤选择右键**解压文件**,默认是以压缩包名创建一个新的文件夹,会出现漫画被拆散在不同文件夹的情况
3. 压缩包默认zip格式,无解压密码.遇到解不开的情况可能是下载时压缩包损坏了,尝试下重新下载


# 结尾
[清心寡欲在平时，坚守临期凛四知，鸩酒岂堪求止渴，光明正大好男儿:thumbsup:](https://tieba.baidu.com/f?kw=%E6%88%92%E8%89%B2&ie=utf-8)  

<img src="https://img0.baidu.com/it/u=3062059221,3960853354&fm=253&fmt=auto&app=138&f=JPEG?w=198&h=198" align=center />

# CHANGELOG

| 日期       | 说明                                                                                                                                                       |
| ---------- |----------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2024/12/01 | 感谢`Kingyum-Hou`提供的贡献.改用数据库来维护已下载的漫画,取代了之前用txt文件记录的方式. 可以通过`src/data_migration.py`脚本将txt中的历史数据迁移到数据库中.                                                          |
| 2024/09/26 | 调整了邮件推送的逻辑. qq邮箱抽风了, 循环发邮件前要重新调用一次smtplib的login方法,不然就报`SMTPSenderRefused`, 错误码`-1`. 不清楚qq那边对发信规则做了什么改动                                                   |
| 2024/05/15 | 增加了`INTERVAL_TIME`下载时间间隔参数, 修复了日志不会实时输出的问题                                                                                                               |
| 2023/10/02 | 1.补充了上次更新没写进去的运行时间的保存逻辑:laughing: 2.改用total_seconds()判断时间差,seconds算出来的结果有误 3.修复了分卷压缩函数KeyError的问题--创建的压缩包个数 = 文件总大小/压缩包的最大大小,但分卷压缩时每个包都不会被填满的,导致实际需要更多的包 |
| 2023/09/12 | 修复了漫画曾被下载一次后, 新增章节无法被下载的bug. 现在记录了上次运行的时间, 与漫画章节的上传时间进行比对, 有新章节时则触发增量下载                                                                                  |
| 2023/03/28 | 修复了调用分页获取章节接口时,只获取了第一页的bug,这会导致总章节数>40的漫画下载不全                                                                                                            |
| 2023/02/03 | 参考了[jiayaoO3O/18-comic-finder](https://github.com/jiayaoO3O/18-comic-finder),现在可以在GitHub Actions上下载到完整的压缩包                                                  |
| 2023/02/01 | 1.区分了GitHub Actions和本地运行两种运行方式 2.新增按关键词订阅功能 3.调整了邮箱的配置项,支持指定加密方式和端口 4.引入`狗屁不通文章`生成邮件正文的随机字符串                                                                |
| 2023/01/06 | 基于GitHub Actions重构了代码,并采用了邮件的形式推送漫画                                                                                                                         |
| 2022/12/08 | 启动项目时自动打卡                                                                                                                                                |
| 2022/11/27 | 实现按排行榜以及收藏夹进行下载的功能                                                                                                                                       |

