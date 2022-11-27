# 项目简介

* 目前已实现按排行榜以及收藏夹进行下载的功能
    * [本项目是基于AnkiKong大佬开源的项目编写的](https://github.com/AnkiKong/picacomic)
    * [目前pica的api目录](https://www.apifox.cn/apidoc/shared-44da213e-98f7-4587-a75e-db998ed067ad/doc-1034189),
* 运行环境: python3.10
* 运行前需要安装的模块
```python
pip install pywin32
```
* 运行方式:
```python
python main.py
```

# config.ini

基础配置文件,不改这个文件项目也能跑
[filter]支持在下载时按分区进行过滤

# secret-config.ini

运行前填写完这里的所有配置项   
[email][password]是pica的账号密码   
[proxy_soft_ware]是代理程序的路径,允许时会帮你自动启动代理程序,并支持在下载完毕后自动关闭代理   
[secret_key可以按AnkiKong的这篇文章进行配置](https://zhuanlan.zhihu.com/p/547321040)   

# main.py

程序运行的入口,每次运行只会爬取一次,不会周期性地执行   
运行前需要开启代理程序,不然无法访问pica的服务器会报错   

* 运行时会在项目根目录自动生成downloaded.txt文件,记录了下载的本子的id,避免重复下载
  * 在下载前手动插入id,可以跳过下载这个本子
  * **需要再次下载时, 则需要手动移除id**

## 如何实现定时执行
利用windows的任务计划程序,支持在每天/每周等固定的时间点自动执行main.py文件   
这个我会考虑出个视频教学如何配置   

## 如何避免重复下载
运行时会在项目根目录自动生成downloaded.txt文件,记录了下载的本子的id   
可以在运行前手动插入id,实现跳过下载   

# client.py

对pica接口的封装


# mergeComic.py

可以将多个文件夹的漫画合并到一个文件夹
1. 填写[merge_path]配置项
2. 将多个本子移动到merge目录下(文件夹名按ASCII的升序排列,或者是直接按1,2,3...这样的数字命名)
3. 运行mergeComic.py, 在命令行输入目标文件夹名,这个文件夹将在merge目录下自动创建,并自动移动进其他文件夹的所有图片,移动后的图片顺序与文件夹的顺序一致

 


