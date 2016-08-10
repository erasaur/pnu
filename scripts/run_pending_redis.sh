#!/usr/bin/env bash

# should be called from run.sh in root of project
source scripts/config.sh

if [[ $PNU_ENV == "prod" ]]; then
  redis_service=$REDIS_PENDING_SERVICE
else
  redis_service=redis-server
fi

pid_redis=$(get_pid $redis_service)
if [ ! -n "$pid_redis" ]; then
  if [[ $PNU_ENV == "prod" ]]; then
    nohup service $REDIS_PENDING_SERVICE start >$REDIS_PENDING_LOG_FILE 2>&1 &
  else
    nohup redis-server $REDIS_PENDING_CONF_FILE >$REDIS_PENDING_LOG_FILE 2>&1 &
  fi
else
  echo -e "${RED}redis-pending already running. Try [kill -9 $pid_redis] first, then re-run.${NC}"
fi
