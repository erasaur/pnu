#!/bin/bash

source scripts/config.sh

echo "PIDS:"
pids=`ps -afe | grep redis | grep -v grep`
if [ -n "$pids" ]; then
  echo "$pids"
else
  echo "No pids found."
fi
echo

redis_user="$REDIS_USER_HOST:$REDIS_USER_PORT"
pid_redis_user=$(get_pid $redis_user)
if [ -n "$pid_redis_user" ]; then
  redis-cli -p $REDIS_USER_PORT save
  kill -2 $pid_redis_user
else
  echo "$redis_user not running"
fi

redis_pending="$REDIS_PENDING_HOST:$REDIS_PENDING_PORT"
pid_redis_pending=$(get_pid $redis_pending)
if [ -n "$pid_redis_pending" ]; then
  redis-cli -p $REDIS_PENDING_PORT save
  kill -2 $pid_redis_pending
else
  echo "$redis_pending not running"
fi

pid_main=$(get_pid $MAIN_PROCESS)
if [ -n "$pid_main" ]; then
  kill -9 $pid_main
else
  echo "$MAIN_PROCESS not running."
fi

if [ -x "$(command -v service)" ]; then
  echo "Killing redis procceses with service"
  service $REDIS_PROCESS stop
  service $REDIS_PENDING_SERVICE stop
  service $REDIS_USER_SERVICE stop
fi

source setup_prod.sh
./run.sh
./check_status.sh
