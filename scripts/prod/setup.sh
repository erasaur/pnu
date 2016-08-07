#!/usr/bin/env bash

# setup app logs
mkdir -p pnu/etc/logs
touch pnu/etc/logs/logging.out

# setup redis
mkdir -p db/user db/pending
cp pnu/etc/redis/prod/user/redis-pnu-user-server /etc/init.d/
cp pnu/etc/redis/prod/pending/redis-pnu-pending-server /etc/init.d/
update-rc.d redis-pnu-user-server defaults
update-rc.d redis-pnu-pending-server defaults

# install requirements
# sudo apt-get install python3-dev
# export C_INCLUDE_PATH=/usr/include/python3.4
# pip3.5 install -r requirements.txt
