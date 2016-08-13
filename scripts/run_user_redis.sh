#!/usr/bin/env bash

# should be called from run.sh in root of project
source scripts/config.sh

redis_service="$REDIS_USER_HOST:$REDIS_USER_PORT"
pid_redis=$(get_pid $redis_service)
if [ ! -n "$pid_redis" ]; then
  if [[ $PNU_ENV == "prod" ]]; then
    nohup service $REDIS_USER_SERVICE start >$REDIS_USER_LOG_FILE 2>&1 &
  else
    nohup redis-server $REDIS_USER_CONF_FILE >$REDIS_USER_LOG_FILE 2>&1 &
  fi
else
  echo -e "${RED}redis-user already running. Try [kill -9 $pid_redis] first, then re-run.${NC}"
fi
