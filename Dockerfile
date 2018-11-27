FROM pypy:3

RUN apt update

RUN apt install -yqq sqlite3
RUN apt install -yqq python3

COPY test-data/traces/ /home/traces/
COPY schema.sql /home/
COPY *.py /home/
COPY test-data/test-settings.py /home/settings.py

