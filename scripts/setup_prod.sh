#!/usr/bin/env bash

if [[ `uname -s` != *"Linux"* ]]; then
  echo -e "${RED}Sorry, only linux supported at this time.${NC}"
  exit
fi

export PNU_ENV=prod

# need to run in root of project directory!
source scripts/config.sh
source scripts/setup_common.sh

# check if initial setup failed
if (( $? != 1 )); then
  # setup redis and redis logs
  echo "Setting up redis services..."
  cp $REDIS_PENDING_SERVICE_FILE /etc/init.d/
  cp $REDIS_USER_SERVICE_FILE /etc/init.d/
  update-rc.d $REDIS_PENDING_SERVICE defaults
  update-rc.d $REDIS_USER_SERVICE defaults

  # stop redis-server
  pid_redis=$(get_pid redis-server)
  if [ -n "$pid_redis" ]; then
    service redis-server stop
  fi

  echo -e "${GREEN}Prod environment set up.${NC}"
fi
