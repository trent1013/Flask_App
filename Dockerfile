FROM python:3.7.3

MAINTAINER Trent Taylor "trent.taylor@smartcloudforge.com"

#RUN whereis python

#apt-get install -y python3-pip python3-dev

RUN apt-get update && \
 pip install --upgrade pip
 
COPY . ./Flask_App
WORKDIR /Flask_App

#RUN whoami

RUN ls -asl ~

RUN ls ./.aws && cp -r ./.aws ~

RUN ls -asl ~

RUN pip install -r fa_requirements.txt && pip install boto3

EXPOSE 5000

CMD python quickstart_app.py 

