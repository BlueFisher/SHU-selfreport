FROM ubuntu:20.04

WORKDIR /selfreport

COPY . .

RUN apt-get update &&\
    apt-get install -y python3.8 python3-pip &&\
    pip3 install -r requirements.txt

CMD ["python3", "/selfreport/main.py"]