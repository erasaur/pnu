#!/usr/bin/env bash

export PNU_ENV=dev

# need to run in root of project directory!
source scripts/config.sh
source install_deps.sh

# if install deps failed, returns 1
if [[ $? -eq 1 ]]; then
  return
fi

echo "Setting up logs..."
mkdir -p $APP_LOG_DIR
touch $APP_LOG_FILE

echo "Setting up redis..."
mkdir -p $REDIS_RUN_PENDING_DIR $REDIS_RUN_USER_DIR
touch $REDIS_PENDING_LOG_FILE
touch $REDIS_USER_LOG_FILE

echo -e "${GREEN}Dev environment set up.${NC}"
