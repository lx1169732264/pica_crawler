# 项目简介

一个哔咔漫画的下载程序,基于python实现,欢迎各位绅士来捉虫
* 目前已实现按排行榜以及收藏夹进行下载的功能   
* 漫画将会以压缩包附件的形式推送到邮箱上,受限于邮件的附件大小,漫画会被打包为若干个压缩包,这也导致一次性可能会收到若干个邮件
* 本项目是基于[AnkiKong大佬开源的项目](https://github.com/AnkiKong/picacomic)编写的,仅供技术研究使用,请勿用于其他用途,有问题可以提issue
* 可以fork这个项目,根据[api文档](https://www.apifox.cn/apidoc/shared-44da213e-98f7-4587-a75e-db998ed067ad/doc-1034189)自行开发功能
* 麻烦给个star支持一下:heart:

# 运行

*  fork本仓库
*  新增Actions secrets

| secret          | 说明                                                         |
| --------------- | ------------------------------------------------------------ |
| PICA_SECRET_KEY | [AnkiKong提供的secret_key](https://zhuanlan.zhihu.com/p/547321040) |
| PICA_ACCOUNT    | 哔咔登录的账号                                               |
| PICA_PASSWORD   | 哔咔登录的密码                                               |
| EMAIL_ACCOUNT   | 接收漫画的邮箱                                               |
| EMAIL_AUTH_CODE | 邮箱的授权码,[参考qq邮箱的这篇文档](https://service.mail.qq.com/cgi-bin/help?subtype=1&&id=28&&no=1001256) |
| GIT_TOKEN       | [参考这篇文章](http://t.zoukankan.com/joe235-p-15152380.html),只勾选repo的权限,Expiration设置为No Expiration |

<img src="https://raw.githubusercontent.com/lx1169732264/Images/master/Actions%20secrets.png" width = "700" height = "350" alt="图片名称" align=center />



* 打开fork项目的workFlow开关

<img src="https://raw.githubusercontent.com/lx1169732264/Images/master/enableWorkFlow.png" width = "700" height = "350" alt="图片名称" align=center />

* 点击pica_crawler_actions.yml,编辑git actions. 修改红框所示的内容

<img src="https://raw.githubusercontent.com/lx1169732264/Images/master/gitActions.png" width = "700" height = "350" alt="图片名称" align=center />



* 手动触发一次,测试下能不能跑通

<img src="https://raw.githubusercontent.com/lx1169732264/Images/master/runWorkFlow.png" width = "500" height = "200" alt="图片名称" align=center />



**成功运行的截图:**   
<img src="https://raw.githubusercontent.com/lx1169732264/Images/master/%E6%88%90%E5%8A%9F%E8%BF%90%E8%A1%8C%E6%88%AA%E5%9B%BE.png" width = "700" height = "350" alt="图片名称" align=center />



# 部分漫画不会被下载的原因



### 过滤重复下载

downloaded.txt文件记录了已下载的漫画id. 在下载前手动插入id,可以跳过下载这个漫画



### 过滤分区

比如说不看WEBTOON分区,就在Git Actions的yml配置文件配置如下:   

CATEGORIES: WEBTOON   	多个分区之间用‘,’分隔   

只要漫画满足任意分区,就不会被下载






# 结尾
[清心寡欲在平时，坚守临期凛四知，鸩酒岂堪求止渴，光明正大好男儿:thumbsup:](https://tieba.baidu.com/f?kw=%E6%88%92%E8%89%B2&ie=utf-8)  

<img src="https://img0.baidu.com/it/u=3062059221,3960853354&fm=253&fmt=auto&app=138&f=JPEG?w=198&h=198" align=center />

# CHANGELOG

v1.2 2022/12/30
---------------
* 基于git actions重构了代码,并采用了邮件的形式推送漫画

v1.1    2022/12/08
---------------
* 启动项目时自动打卡


v1.0   2022/11/27
---------------
* 实现按排行榜以及收藏夹进行下载的功能



