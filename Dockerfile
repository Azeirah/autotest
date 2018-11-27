FROM debian:stretch-slim

RUN apt update

RUN apt install -yqq sqlite3
RUN apt install -yqq python3

COPY *.py /home/
COPY test-data/traces/ /home/traces/
COPY schema.sql /home/
COPY test-data/test-settings.py /home/settings.py

