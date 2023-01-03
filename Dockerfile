# Some info
# build: sudo docker build -t lcdtainer .
# tag: sudo docker tag lcdtainer renaudrenaud/lcdtainer:latest
# add user to the docker group sudo usermod -aG docker $USER and exit session
# login: docker login
# push: docker push renaudrenaud/lcdtainer:latest
# run: docker run -d --name lcdtainer -p 8080:8080 renaudrenaud/lcdtainer:latest
# python3 testLCD.py -d volume -v yes -s 192.168.1.120:9000
# On RASPBERRY I2C should be activated with sudo raspi-config
# then device has to be exposed 
# devices:  
#  - "/dev/i2c-1:/dev/i2c-1" 
# env:
# TZ=Asia/Shanghai
# LMS_LCD=0x3F
# LMS_I2C_PORT=1
# LMS_VIRTUAL_LCD=no
# LMS_DISPLAY_MODE=cpu
# LMS_PLAYER_NAME=
# LMS_SERVER=192.168.1.120:9000

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
# CMD ["python3","testLCD.py","-i","1","-d","bitrate","-s","192.168.1.120:9000"]
CMD ["python3","testLCD.py"]
# EXPOSE 8000
# CMD ["python3","-m", "http.server"]
