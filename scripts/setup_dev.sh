#!/usr/bin/env bash

export PNU_ENV=dev

# need to run in root of project directory!
source scripts/config.sh
source scripts/setup_common.sh

# check if initial setup failed
if [[ $? -eq 1 ]]; then
  return
fi

echo -e "${GREEN}Dev environment set up.${NC}"
