if [ -x "$(command -v service)" ]; then
  echo "Services:"
  service --status-all | grep redis-pnu
  echo
fi

printf "PIDs:\n"
echo "`ps -fe | grep -e main.py -e redis-server | grep -v grep`"
