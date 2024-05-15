# 使用官方 Python 3 基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PICA_SECRET_KEY="" \
    PICA_ACCOUNT="" \
    PICA_PASSWORD="" \
    CATEGORIES="CG雜圖,生肉,耽美花園,偽娘哲學,扶他樂園,性轉換,SAO 刀劍神域,WEBTOON,Cosplay" \
    CATEGORIES_RULE="EXCLUDE" \
    SUBSCRIBE_KEYWORD="" \
    SUBSCRIBE_DAYS="7" \
    REQUEST_PROXY="" \
    PACKAGE_TYPE="False" \
    BARK_URL="" \
    INTERVAL_TIME="5"

# 将当前目录内容复制到工作目录中
COPY . /app

# 安装依赖项
RUN pip install --no-cache-dir requests urllib3

# 指定容器启动时执行的命令
CMD ["python", "main.py"]
