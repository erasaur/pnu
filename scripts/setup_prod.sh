#!/usr/bin/env bash

if [ "$(expr substr $(uname -s) 1 5)" != "Linux" ]; then
  echo -e "${RED}Sorry, only linux supported at this time.${NC}"
  exit
fi

export PNU_ENV=prod

# require running as sudo
if [ $EUID != 0 ]; then
  echo -e "${RED}Please re-run as sudo.${NC}"
  exit
fi

# need to run in root of project directory!
source scripts/config.sh
source scripts/install_deps.sh

# setup app logs
mkdir -p $APP_LOG_DIR
touch $APP_LOG_FILE

# setup redis and redis logs
mkdir -p $REDIS_RUN_PENDING_DIR $REDIS_RUN_USER_DIR
sudo chmod +w $REDIS_RUN_DIR
touch $REDIS_PENDING_LOG_FILE
touch $REDIS_USER_LOG_FILE
sudo chmod +w $REDIS_PENDING_LOG_FILE
sudo chmod +w $REDIS_USER_LOG_FILE
cp $REDIS_PENDING_SERVICE_CONF /etc/init.d/
cp $REDIS_USER_SERVICE_CONF /etc/init.d/
update-rc.d $REDIS_PENDING_SERVICE defaults
update-rc.d $REDIS_USER_SERVICE defaults

echo -e "${GREEN}Prod environment set up.${NC}"
