source scripts/config.sh

echo "PIDS:"
pids=`ps -afe | grep redis | grep -v grep`
if [ -n "$pids" ]; then
  echo $pids
else
  echo "No pids found."
fi
echo

redis_user="127.0.0.1:6379"
pid_redis_user=$(get_pid $redis_user)
if [ -n "$pid_redis_user" ]; then 
  read -p "Kill pid $pid_redis_user? [y/n]" -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    kill -9 $pid_redis_user
  fi
else
  echo "redis-user not running."
fi

redis_pending="127.0.0.1:6380"
pid_redis_pending=$(get_pid $redis_pending)
if [ -n "$pid_redis_pending" ]; then 
  read -p "Kill pid $pid_redis_pending? [y/n]" -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    kill -9 $pid_redis_pending
  fi
else
  echo "redis-pending not running."
fi

pid_main=$(get_pid main.py)
if [ -n "$pid_redis_pending" ]; then 
  read -p "Kill pid $pid_redis_pending? [y/n]" -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    kill -9 $pid_main
  fi
else
  echo "main.py not running."
fi
