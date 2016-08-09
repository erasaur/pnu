#!/usr/bin/env bash

export PNU_ENV=prod

# should match service name in redis conf files
PENDING_SERVICE=redis-pnu-pending-server
USER_SERVICE=redis-pnu-user-server

# should match rundir in redis service files
RUNDIR=/var/run/redis
PENDING_LOGFILE=$RUNDIR/$PENDING_SERVICE.log
USER_LOGFILE=$RUNDIR/$USER_SERVICE.log

# setup app logs
mkdir -p pnu/etc/logs
touch pnu/etc/logs/logging.out

# setup redis and redis logs
mkdir -p db/pending db/user # redis dump files
sudo chown -R redis:redis db
mkdir -p $RUNDIR
touch $PENDING_LOGFILE
touch $USER_LOGFILE
sudo chown redis:redis $PENDING_LOGFILE
sudo chown redis:redis $USER_LOGFILE
cp pnu/etc/redis/prod/user/$USER_SERVICE /etc/init.d/
cp pnu/etc/redis/prod/pending/$PENDING_SERVICE /etc/init.d/
update-rc.d $USER_SERVICE defaults
update-rc.d $PENDING_SERVICE defaults

# install requirements
# sudo apt-get install python3-dev
# export C_INCLUDE_PATH=/usr/include/python3.5
# pip3.5 install -r requirements.txt
