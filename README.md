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

# 解压注意事项
1. 将所有邮件的压缩包下载至统一目录. (存在单个压缩包里可能只有半本漫画的情况),然后**全选**压缩包,右键**解压到当前文件夹**.  
2. 如果你在上个步骤选择右键解压文件,默认是以压缩包名创建一个新的文件夹,会出现漫画拆散在不同文件夹的情况
3. 压缩包默认zip格式,无解压密码.遇到解不开的情况可能是下载时压缩包损坏了,尝试下重新下载




# 部分漫画不会被下载的原因
排行榜的漫画会收到以下过滤逻辑的影响,收藏夹则不会


### 过滤重复下载

downloaded.txt文件记录了已下载的漫画id. 每次运行代码后,都会通过git actions的指令提交代码,保存本次的运行结果   
在下载前手动插入id,可以跳过对应漫画的下载   



### 过滤分区

支持通过分区自定义下载逻辑. 

git actions配置文件的``CATEGORIES``配置项可以配置0~n个哔咔的分区, 配置为空则代表不过滤  

``CATEGORIES_RULE``可以配置为 INCLUDE: 包含任意一个分区就下载  EXCLUDE: 包含任意一个分区就不下载

> 部分漫画只打上了'短篇'/'长篇'这样单个分区,在配置为``INCLUDE``时,建议把比较常见的分区给填上,不然容易匹配不到漫画



# 结尾
[清心寡欲在平时，坚守临期凛四知，鸩酒岂堪求止渴，光明正大好男儿:thumbsup:](https://tieba.baidu.com/f?kw=%E6%88%92%E8%89%B2&ie=utf-8)  

<img src="https://img0.baidu.com/it/u=3062059221,3960853354&fm=253&fmt=auto&app=138&f=JPEG?w=198&h=198" align=center />

# CHANGELOG

v1.2 fix 2023/01/06
---------------
* 邮箱有发信规则, 短时间内发太多邮件容易封一段时间的账号导致发邮件失败, 尝试下在邮件正文写点随机字符串绕过检测

v1.2 2022/12/30
---------------
* 基于git actions重构了代码,并采用了邮件的形式推送漫画

v1.1    2022/12/08
---------------
* 启动项目时自动打卡


v1.0   2022/11/27
---------------
* 实现按排行榜以及收藏夹进行下载的功能



