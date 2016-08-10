#!/usr/bin/env bash

# needs to be run from project root!

if [ -z "$PNU_ENV" ]; then
    echo "Please run 'source setup_dev.sh' or 'source setup_prod.sh' first."
    exit
fi

if [[ $VIRTUAL_ENV != *"pnu"* ]]; then
    echo "Please start virtualenv with 'source $VIRTUALENV_DIR/bin/activate'."
    exit
fi

# start redis if not already running
pid_redis=$(get_pid $REDIS_PROCESS)
if [ -n "$pid_redis" ]; then 
  echo -e "${GREEN}Redis is running with pid: $pid_redis${NC}"
else 
  echo -e "Starting redis-pending..."
  source scripts/run_pending_redis.sh
  echo -e "Starting redis-user..."
  source scripts/run_user_redis.sh
fi

# start main app
pid_main=$(get_pid $MAIN_PROCESS)
if [ ! -n "$pid_main" ]; then
  nohup ./main.py >$MAIN_LOG_FILE 2>$MAIN_ERR_FILE &
  echo -e "${GREEN}App started.${NC}"
else
  echo -e "${RED}App is already running. Try [kill -9 $pid_main] first, then re-run.${NC}"
fi
