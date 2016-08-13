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
  read -p "Kill pid $pid_redis_user? [y/n]" -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Attempt to save first? [y/n]" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      redis-cli -p $REDIS_USER_PORT save
    fi
    kill -9 $pid_redis_user
  fi
else
  echo "redis-user not running."
fi

redis_pending="$REDIS_PENDING_HOST:$REDIS_PENDING_PORT"
pid_redis_pending=$(get_pid $redis_pending)
if [ -n "$pid_redis_pending" ]; then 
  read -p "Kill pid $pid_redis_pending? [y/n]" -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Attempt to save first? [y/n]" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      redis-cli -p $REDIS_PENDING_PORT save
    fi
    kill -9 $pid_redis_pending
  fi
else
  echo "redis-pending not running."
fi

pid_main=$(get_pid $MAIN_PROCESS)
if [ -n "$pid_main" ]; then 
  read -p "Kill pid $pid_main? [y/n]" -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    kill -9 $pid_main
  fi
else
  echo "$MAIN_PROCESS not running."
fi

if [ -x "$(command -v service)" ]; then
  read -p "Kill redis services? [y/n]" -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    service $REDIS_PROCESS stop
    service $REDIS_PENDING_SERVICE stop
    service $REDIS_USER_SERVICE stop
  fi
fi
