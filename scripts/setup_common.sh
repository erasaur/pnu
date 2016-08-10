#!/usr/bin/env bash

source scripts/install_deps.sh

# if install deps failed, returns 1
if [[ $? -eq 1 ]]; then
  return 1
fi

if [ -f pnu/etc/private_config.json ]; then
  mkdir -p pnu/etc/private
  cp pnu/etc/private_config.json pnu/etc/private/config.json
else
  echo -e "${RED}Missing config.json file!${NC}"
  return 1
fi

mkdir -p $REDIS_USER_DUMP_DIR $REDIS_PENDING_DUMP_DIR
