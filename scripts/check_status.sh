source scripts/config.sh

if [ -x "$(command -v service)" ]; then
  echo "Services:"
  service --status-all | grep -e $REDIS_PENDING_SERVICE -e $REDIS_USER_SERVICE
  echo
fi

printf "PIDs:\n"
pids=`ps -fe | grep -e $MAIN_PROCESS -e $REDIS_PROCESS | grep -v grep`
if [ -n "$pids" ]; then
  echo "$pids"
else
  echo "No pids found."
fi
