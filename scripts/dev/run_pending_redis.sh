#!/usr/bin/env bash

REDIS_PROCESS="redis-server $PWD/pnu/etc/redis/dev/pending/redis-server.conf"
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

get_pid_redis () {
  # returns the process id of the redis process
  echo `
    ps -ef | # display processes with their pids
    grep 'pending/redis-server' | # get desired lines
    grep -v grep | # ignore lines with grep
    tr -s " " | # collapse spaces
    cut -d " " -f3 | # cut by spaces and grab pid column
    head -n 1 # get first line
  `
}

pid_redis=$(get_pid_redis)
if [ ! -n "$pid_redis" ]; then
  nohup $REDIS_PROCESS >/dev/null 2>&1 &
  echo -e "${GREEN}Started redis-pending.${NC}"
else
  echo -e "${RED}redis-pending already running. Try [kill -9 $pid_redis] first, then re-run.${NC}"
fi
