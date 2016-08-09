#!/usr/bin/env bash

# should be called from run.sh in root of project
source scripts/config.sh

pid_redis=$(get_pid $REDIS_USER_SERVICE)
if [ ! -n "$pid_redis" ]; then
  nohup service $REDIS_USER_SERVICE start >$REDIS_USER_LOG_FILE 2>&1 &
else
  echo -e "${RED}redis-user already running. Try [kill -9 $pid_redis] first, then re-run.${NC}"
fi
