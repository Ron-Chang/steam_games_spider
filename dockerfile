# docker.ziliplay.com/python:3.7-alpine
# --------
# Install default packages
# RUN apk add --no-cache vim gcc g++ supervisor bash libffi-dev libressl-dev
# Setting Env
# RUN echo "set ts=4" >> /etc/vim/vimrc
# RUN echo "set sw=4" >> /etc/vim/vimrc
# RUN echo "set expandtab" >> /etc/vim/vimrc
# RUN echo "set hls" >> /etc/vim/vimrc
# --------

# Container/Image name
FROM docker.ziliplay.com/python:3.7-alpine
LABEL maintainer="Ron Chang<highlupin@gmail.com>"

# Prepare packages
ARG PRODUCT_NAME="app"
ENV ENV="/root/.bashrc"
RUN mkdir -p /${PRODUCT_NAME}
RUN mkdir -p /etc/supervisor.d/
WORKDIR /${PRODUCT_NAME}
COPY src .
COPY requirements.txt .

# Add alias
RUN echo 'alias ll="ls -al"' >> /root/.profile
RUN echo 'alias run="python start_scraping_steam.py"' >> /root/.profile
RUN echo 'alias test="python test.py"' >> /root/.profile

# # Install apk
RUN apk add --no-cache vim gcc g++ supervisor bash libffi-dev libressl-dev libxslt-dev
RUN apk add --no-cache jpeg-dev zlib-dev

# # Install requirement
RUN pip --no-cache-dir install -r requirements.txt

# # Startup service
# CMD ["supervisord", "-n"]
