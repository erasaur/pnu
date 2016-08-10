#!/usr/bin/env bash

source install_deps.sh

# if install deps failed, returns 1
if [[ $? -eq 1 ]]; then
  return 1
fi

if [ -f pnu/etc/config_template.json ]; then
  mkdir -p pnu/etc/private
  cp pnu/etc/config_template.json pnu/etc/private/config.json
else
  echo -e "${RED}Missing config.json file!${NC}"
  return 1
fi
