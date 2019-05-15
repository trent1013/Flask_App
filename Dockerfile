FROM python:3.7-alpine

MAINTAINER Doug MacLeod "doug.macleod@smartcloudforge.com"

RUN apt-get update && apt-get install -y python-pip python-dev && \
 pip install --upgrade pip
 
COPY ./Flask_App
WORKDIR /Flask_App

RUN pip install -r fa_requirements.txt

ENTRYPOINT [ "python" ]

CMD [ "quickstart_app.py" ]

