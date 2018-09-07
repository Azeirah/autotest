FROM debian:stretch-slim

RUN apt update
RUN apt install -qq -y php7.0
RUN apt install sqlite3
RUN apt install python3
