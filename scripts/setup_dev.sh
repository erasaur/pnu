#!/usr/bin/env bash

export PNU_ENV=dev

# need to run in root of project directory!
source scripts/config.sh
source scripts/setup_common.sh

# check if initial setup failed
if (( $? == 1 )); then
  exit
fi

echo -e "${GREEN}Dev environment set up.${NC}"
