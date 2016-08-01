#!/usr/bin/env bash

# setup app logs
mkdir -p pnu/etc/logs
touch pnu/etc/logs/logging.out

# setup redis
mkdir -p db/user/logs db/pending/logs
touch db/user/logs/redis-server.log
touch db/pending/logs/redis-server.log
cp pnu/etc/redis/prod/user/redis-pnu-user-server /etc/init.d/
cp pnu/etc/redis/prod/pending/redis-pnu-pending-server /etc/init.d/
update-rc.d redis-pnu-user-server defaults
update-rc.d redis-pnu-pending-server defaults

# install requirements
# pip3.5 install -r requirements.txt
