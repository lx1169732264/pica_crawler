# 使用官方 Python 3 基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
#RUN apt-get update && apt-get install -y build-essential

# 设置环境变量
ENV PACKAGE_TYPE="False" \
    DELETE_COMIC="True"

# 将当前目录内容复制到工作目录中
COPY . /app

# 安装依赖项
RUN pip install --progress-bar off requests urllib3

# 指定容器启动时执行的命令
CMD ["python", "./src/main.py"]
