echo "Services:"
service --status-all | grep redis-pnu
printf "\nPIDs:\n"
echo "`ps -fe | grep -e main.py -e redis-server | grep -v grep`"
