#!/usr/bin/env bash

REDIS_PROCESS=redis-server
MAIN_PROCESS=main.py
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
ENV=dev

# # require running as sudo
# if (( $EUID != 0 )); then
#   echo -e "${RED}Please re-run as sudo.${NC}"
#   exit
# fi

get_pid_redis () {
  # returns the process id of the redis process
  echo `
    ps -ef | # display processes with their pids
    grep $REDIS_PROCESS | # get lines with redis-server
    grep -v grep | # ignore lines with grep
    tr -s " " | # collapse spaces
    cut -d " " -f2 | # cut by spaces and grab pid column
    head -n 1 # get first line
  `
}

get_pid_main () {
  echo `
    ps -ef | # display processes with their pids
    grep $MAIN_PROCESS | # get lines with main.py
    grep -v grep | # ignore lines with grep
    tr -s " " | # collapse spaces
    cut -d " " -f2 | # cut by spaces and grab pid column
    head -n 1 # get first line
  `
}

# start redis if not already running
pid_redis=$(get_pid_redis)

if [ -n "$pid_redis" ]; then 
  echo -e "${GREEN}Redis is running with pid: $pid_redis${NC}"
else 
  echo -e "Starting redis-pending..."
  ./scripts/$ENV/run_pending_redis.sh
  echo -e "Starting redis-user..."
  ./scripts/$ENV/run_user_redis.sh
fi

# start main app
pid_main=$(get_pid_main)

if [ ! -n "$pid_main" ]; then
  nohup ./main.py >./pnu/etc/logs/main.out 2>./pnu/etc/logs/main.err &
  echo -e "${GREEN}App started.${NC}"
else
  echo -e "${RED}App is already running. Try [kill -9 $pid_main] first, then re-run.${NC}"
fi
