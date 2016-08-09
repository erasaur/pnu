#!/usr/bin/env bash

export PNU_ENV=dev

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

MISSING_MSG="Missing dependency"
DOWNLOAD_MSG="Download now? [y/n]"
EXITING_MSG="Exiting"

VIRTUALENV_DIR=.venv

# need pip to be installed
if [ -x "$(command -v pip)" ]; then
  echo -e "${GREEN}pip is installed${NC}"
else
  echo -e "${RED}$MISSING_MSG: pip${NC}"
  exit
fi

# need virtualenv to be installed
if [ -x "$(command -v virtualenv)" ]; then
  echo -e "${GREEN}virtualenv is installed${NC}"
else
  echo -e "${RED}$MISSING_MSG: virtualenv${NC}"
  read -p "$DOWNLOAD_MSG" -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install virtualenv
  else
    echo "$EXITING_MSG"
    exit
  fi
fi

# need python3.5
if [ -x "$(command -v python3.5)" ]; then
  echo -e "${GREEN}python3.5 is installed${NC}"
else
  echo -e "${RED}$MISSING_MSG: python3.5${NC}"
  exit
fi

# setup virtualenv
if [ -d "$VIRTUALENV_DIR" ]; then
  echo -e "${GREEN}virtualenv is set up${NC}"
else
  echo "Setting up virtualenv..."
  virtualenv -p python3.5 $VIRTUALENV_DIR
fi

echo "Setting up logs..."
mkdir -p pnu/etc/logs
touch pnu/etc/logs/logging.out

echo "Setting up redis..."
mkdir -p db/user/logs db/pending/logs
touch db/user/logs/redis-server.log
touch db/pending/logs/redis-server.log

echo "Activating virtualenv..."
source .venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo -e "${GREEN}All done!${NC}"
