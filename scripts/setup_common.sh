#!/usr/bin/env bash

source scripts/install_deps.sh

# if install deps failed, returns 1
if (( $? == 1 )); then
  return 1
fi

mkdir -p pnu/etc/private
if [ -f pnu/etc/private_config.json ] && [ ! -f pnu/etc/private/config.json ]; then
  cp pnu/etc/private_config.json pnu/etc/private/config.json
else
  echo -e "${RED}Missing private_config.json file!${NC}"
  return 1
fi

echo "Setting up app logs..."
mkdir -p $APP_LOG_DIR
touch $APP_LOG_FILE

echo "Creating redis dump directories..."
mkdir -p $REDIS_USER_DUMP_DIR $REDIS_PENDING_DUMP_DIR
echo "Setting up redis logs..."
mkdir -p $REDIS_RUN_PENDING_DIR $REDIS_RUN_USER_DIR
touch $REDIS_PENDING_LOG_FILE
touch $REDIS_USER_LOG_FILE

if [ $(grep -q -E "^redis:" /etc/group) ]; then
  echo "Setting permissions for redis..."
  sudo chown -R redis:redis $REDIS_USER_DUMP_DIR $REDIS_PENDING_DUMP_DIR
  sudo chown -R redis:redis $REDIS_RUN_DIR $REDIS_RUN_PENDING_DIR $REDIS_RUN_USER_DIR
  sudo chown redis:redis $REDIS_PENDING_LOG_FILE
  sudo chown redis:redis $REDIS_USER_LOG_FILE
fi
