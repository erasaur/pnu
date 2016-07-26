#!/bin/bash

REDIS_PROCESS=redis-server
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

get_pid_redis () {
  # returns the process id of the redis process
  echo `ps -fe | grep $REDIS_PROCESS | grep -v grep | tr -s " "| cut -d " " -f2`
}

# check if redis server is running or not
pid=$(get_pid_redis)
if [ -n "$pid" ]; then 
   echo -e "${GREEN}Redis is running with pid: $pid${NC}"
  ./main.py
else 
   echo -e "${RED}Please start redis with ./run_redis first.${NC}"
fi
