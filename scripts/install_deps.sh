#!/usr/bin/env bash

# include config variables. this file is run from setup scripts, run those
# instead of running this script directly!
source scripts/config.sh

MISSING_MSG="Missing dependency"
DOWNLOAD_MSG="Download now? [y/n]"
EXITING_MSG="Exiting"

read -p "Are you running from root of project dir? [y/n]" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "$EXITING_MSG"
  return 1
fi

# need pip to be installed
if [ -x "$(command -v pip)" ]; then
  echo -e "${GREEN}pip is installed${NC}"
else
  echo -e "${RED}$MISSING_MSG: pip${NC}"
  return 1
fi

# need protobuf to be installed
if [ -x "$(command -v protoc)" ]; then
  if [[ $(protoc --version) == *3* ]]; then
    echo -e "${GREEN}protobuf3 is installed${NC}"
  else
    echo -e "${RED}$MISSING_MSG: protobuf needs to be >= 3.0.0${NC}"
    return 1
  fi
else
  echo -e "${RED}$MISSING_MSG: protobuf3${NC}"
  return 1
fi

# need redis to be installed
if [ -x "$(command -v redis-server)" ]; then
  echo -e "${GREEN}redis is installed${NC}"
else
  echo -e "${RED}$MISSING_MSG: redis${NC}"

  # mac os
  if [ "$(uname)" == "Darwin" ]; then
    # only attempt to download for them if brew is installed
    if [ -x "$(command -v brew)" ]; then
      read -p "$DOWNLOAD_MSG" -n 1 -r
      echo
      if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install redis
      else
        echo $EXITING
        return
      fi
    else
      echo $EXITING
      return 1
    fi

  # linux
  elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    read -p "$DOWNLOAD_MSG" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      sudo apt-get update
      sudo apt-get install redis-server
    else
      echo $EXITING
      return 1
    fi
  else
    echo $EXITING
    return 1
  fi
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
    return 1
  fi
fi

# need python3.5
if [ -x "$(command -v python3.5)" ]; then
  echo -e "${GREEN}python3.5 is installed${NC}"
else
  echo -e "${RED}$MISSING_MSG: python3.5${NC}"
  return 1
fi

# setup virtualenv
if [ -d "$VIRTUALENV_DIR" ]; then
  echo -e "${GREEN}virtualenv is set up${NC}"
else
  echo "Setting up virtualenv..."
  virtualenv -p python3.5 $VIRTUALENV_DIR
fi

echo "Activating virtualenv..."
source $VIRTUALENV_DIR/bin/activate

# need to add python headers to path for xxhash
if [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  echo "Including python headers to path..."
  sudo apt-get install python3-dev
  export C_INCLUDE_PATH=/usr/include/python3.4
fi

echo "Installing requirements..."
pip install -r requirements.txt

echo -e "${GREEN}Dependencies have been installed!${NC}"
