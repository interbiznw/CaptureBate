FROM python:2-alpine3.7
RUN apk update \
 && apk add  git gcc musl-dev linux-headers libxslt-dev libxml2-dev --no-cache \
 && pip install streamlink \
 && git clone https://github.com/bzsklb/CaptureBate /root/capturebate \
 && cd /root/capturebate && pip install -r requirements.txt \
 && apk del git gcc musl-dev --no-cache \
 && rm -Rf /tmp/*
CMD cd /root/capturebate && python main.py
