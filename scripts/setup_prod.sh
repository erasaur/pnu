#!/usr/bin/env bash

if [ "$(expr substr $(uname -s) 1 5)" != "Linux" ]; then
  echo -e "${RED}Sorry, only linux supported at this time.${NC}"
  return
fi

export PNU_ENV=prod

# need to run in root of project directory!
source scripts/config.sh
source scripts/setup_common.sh

# check if initial setup failed
if [[ $? -eq 1 ]]; then
  return
fi

# setup redis and redis logs
echo "Setting up redis services..."
cp $REDIS_PENDING_SERVICE_FILE /etc/init.d/
cp $REDIS_USER_SERVICE_FILE /etc/init.d/
update-rc.d $REDIS_PENDING_SERVICE defaults
update-rc.d $REDIS_USER_SERVICE defaults

echo -e "${GREEN}Prod environment set up.${NC}"
