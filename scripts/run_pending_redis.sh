#!/usr/bin/env bash

# should be called from run.sh in root of project
source scripts/config.sh

pid_redis=$(get_pid $REDIS_PENDING_SERVICE)
if [ ! -n "$pid_redis" ]; then
  nohup service $REDIS_PENDING_SERVICE start >$REDIS_PENDING_LOG_FILE 2>&1 &
else
  echo -e "${RED}redis-pending already running. Try [kill -9 $pid_redis] first, then re-run.${NC}"
fi
