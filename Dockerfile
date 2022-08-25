FROM ubuntu:20.04

WORKDIR /selfreport

COPY . .

RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list &&\
    apt-get update &&\
    apt-get install -y python3.8 python3-pip &&\
    pip3 install -i https://mirrors.ustc.edu.cn/pypi/web/simple pip -U &&\
    pip3 config set global.index-url https://mirrors.ustc.edu.cn/pypi/web/simple &&\
    pip3 install -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["python3", "/selfreport/main.py"]
