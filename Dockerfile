FROM debian:stretch-slim

RUN apt update

RUN apt install -yqq php7.0
RUN apt install -yqq php-pear
RUN apt install -yqq php-dev
RUN pecl install xdebug

RUN apt install sqlite3
RUN apt install python3
