FROM python:3.7.3

MAINTAINER Trent Taylor "trent.taylor@smartcloudforge.com"

RUN apt-get update && \
 pip install --upgrade pip
 
COPY . ./Flask_App
WORKDIR /Flask_App

RUN mv -v ./.aws ~

RUN pip install -r fa_requirements.txt && pip install boto3

EXPOSE 5000

CMD python quickstart_app.py 

