# 项目简介

一个哔咔漫画的下载程序,基于python实现,欢迎各位绅士来捉虫
* 目前已实现按排行榜以及收藏夹进行下载的功能
* 本项目是基于[AnkiKong大佬开源的项目](https://github.com/AnkiKong/picacomic)编写的,仅供技术研究使用,请勿用于其他用途,有问题可以提issue
* 可以fork这个项目,根据[api文档](https://www.apifox.cn/apidoc/shared-44da213e-98f7-4587-a75e-db998ed067ad/doc-1034189)自行开发功能
* 麻烦给个star支持一下:heart:

# 运行环境

* python3.10
* 安装模块
* 安装依赖
```python
pip install pywin32
pip install urllib3
pip install requests
```
* 运行方式:
```python
python main.py
```

# 运行前配置
## config.ini

基础配置文件,不改这个文件项目也能跑
[filter]支持在下载时按分区进行过滤

## secret-config.ini

运行前填写完这里的所有配置项   
[email],[password]是pica的账号密码   
[proxy_soft_ware]是代理程序的路径,允许时会帮你自动启动代理程序,并支持在下载完毕后自动关闭代理   
[proxy_soft_ware]是代理程序的路径,运行main.py时会帮你自动启动代理,并在下载完毕后自动关闭代理   
[secret_key]按[AnkiKong的文章](https://zhuanlan.zhihu.com/p/547321040)配置即可   

# 项目文件介绍
## main.py

程序运行的入口,每次运行只会爬取一次,不会周期性地执行   
将爬取是哔咔的 每日排行榜 和 收藏夹 里的所有漫画   
运行前需要确保你的代理是可用的,不然报错无法访问pica服务器   

**成功运行的截图:**   
<img src="https://raw.githubusercontent.com/lx1169732264/Images/master/%E8%BF%90%E8%A1%8C%E6%88%AA%E5%9B%BE.png" width = "700" height = "350" alt="图片名称" align=center />

### 如何定时执行

利用windows的任务计划程序,支持在每天/每周等固定的时间点自动执行main.py文件.百度上也有计划任务的配置教学的   

1. 进入控制面板-系统和安全-计划任务   
   <img src="https://raw.githubusercontent.com/lx1169732264/Images/master/%E6%8E%A7%E5%88%B6%E9%9D%A2%E6%9D%BF.png" width = "700" height = "350" alt="图片名称" align=center />
2. 添加一个任务,并新建一个触发器,设置它的运行周期   
   <img src="https://raw.githubusercontent.com/lx1169732264/Images/master/%E8%A7%A6%E5%8F%91%E5%99%A8%E8%AE%BE%E7%BD%AE.png" width = "700" height = "350" alt="图片名称" align=center />
3. 设置触发器的操作   
   <img src="https://raw.githubusercontent.com/lx1169732264/Images/master/%E8%A7%A6%E5%8F%91%E5%99%A8%E6%93%8D%E4%BD%9C.png" width = "700" height = "350" alt="图片名称" align=center />
4. 保存这个任务计划后,就能在终端自动运行这个脚本了.代理软件也是自动打开关闭的,全流程不需要人工介入.只需要确保那个时间点电脑是开着的就行

### 如何跳过某本漫画的下载

* 运行时会在项目根目录自动生成downloaded.txt文件,记录了下载的漫画的id,避免重复下载
  * 在下载前手动插入id,可以跳过下载这个漫画
  * **需要再次下载时, 则手动移除id**

## client.py

对pica接口的封装

## mergeComic.py

可以将多个文件夹的漫画合并到一个文件夹
可以将多个文件夹的漫画合并到一个文件夹(比如说有些漫画是有好多话的,就用这个脚本)
1. 填写[merge_path]配置项
2. 将多个漫画移动到merge目录下(文件夹名按ASCII的升序排列,或者是直接按1,2,3...这样的数字命名)
3. 运行mergeComic.py, 在命令行输入目标文件夹名,这个文件夹将在merge目录下自动创建,并自动移动进其他文件夹的所有图片,移动后的图片顺序与文件夹的顺序一致

 
# 结尾
[清心寡欲在平时，坚守临期凛四知，鸩酒岂堪求止渴，光明正大好男儿:thumbsup:](https://tieba.baidu.com/f?kw=%E6%88%92%E8%89%B2&ie=utf-8)  

<img src="https://img0.baidu.com/it/u=3062059221,3960853354&fm=253&fmt=auto&app=138&f=JPEG?w=198&h=198" align=center />






