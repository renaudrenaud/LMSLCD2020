# Some info
# build: sudo docker build -t lcdslim .
# tag: docker tag lcdtainer renaudrenaud/lcdtainer:latest
# push: docker push renaudrenaud/lcdtainer:latest
# run: docker run -d --name lcdtainer -p 8080:8080 renaudrenaud/lcdtainer:latest
# python3 testLCD.py -d volume -v yes -s 192.168.1.120:9000
# On RASPBERRY I2C should be activated with sudo raspi-config
# then device has to be exposed 
# devices:  
#  - "/dev/i2c-1:/dev/i2c-1" 
# env:
# TZ=Asia/Shanghai

FROM python:3.11.0-slim-bullseye

LABEL maintainer="renaudrenaud"

RUN apt-get update -yq \ 
&& apt install -yq git \
&& apt install -yq python3 \
&& apt install -yq python3-pip

WORKDIR /home
RUN git clone https://github.com/renaudrenaud/LMSLCD2020.git

WORKDIR /home/LMSLCD2020

RUN python3 -m pip install -r requirements.txt

# RUN python3 testLCD.py -i 3 -l 0x27 -d volume -s 192.168.1.120:9000
CMD ["python3","testLCD.py","-i","1","-d","bitrate","-s","192.168.1.120:9000"]
# EXPOSE 8000
# CMD ["python3","-m", "http.server"]
