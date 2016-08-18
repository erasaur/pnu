#!/usr/bin/env bash

# include config variables. this file is run from setup scripts, run those
# instead of running this script directly!
source scripts/config.sh

MISSING_MSG="Missing dependency"
DOWNLOAD_MSG="Download now? [y/n]"
EXITING_MSG="${RED}Exiting${NC}"

printf '%s ' 'Are you running from root of project dir? [y/n]'
read REPLY
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo -e $EXITING_MSG
  return 1
fi

# need python3.5
if [ -x "$(command -v python3.5)" ]; then
  echo -e "${GREEN}python3.5 is installed${NC}"
else
  echo -e "${RED}$MISSING_MSG: python3.5${NC}"
  return 1
fi

# need protobuf to be installed
if [ -x "$(command -v protoc)" ] && [[ $(protoc --version) == *3* ]]; then
  echo -e "${GREEN}protobuf3 is installed${NC}"
else
  echo -e "${RED}$MISSING_MSG: protobuf3${NC}"
  # mac os
  if [[ `uname -s` == *"Darwin"* ]]; then
    # only attempt to download for them if brew is installed
    if [ -x "$(command -v brew)" ]; then
      read -p "$DOWNLOAD_MSG" -n 1 -r
      echo
      if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew update && brew install --devel protobuf
      else
        echo -e $EXITING_MSG
        return
      fi
    else
      echo -e $EXITING_MSG
      return 1
    fi

  # linux
  elif [[ `uname -s` == *"Linux"* ]]; then
    read -p "$DOWNLOAD_MSG" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      sudo apt-get update
      sudo apt-get upgrade
      sudo apt-get install autoconf automake libtool curl make g++ unzip
      git clone git://github.com/google/protobuf.git
      cd protobuf
      ./autogen.sh
      ./configure
      make
      make check
      sudo make install
      sudo ldconfig
      cd .. && rm -rf protobuf
    else
      echo -e $EXITING_MSG
      return 1
    fi
  else
    echo -e $EXITING_MSG
    return 1
  fi
fi

# need redis to be installed
if [ -x "$(command -v redis-server)" ]; then
  echo -e "${GREEN}redis is installed${NC}"
else
  echo -e "${RED}$MISSING_MSG: redis${NC}"
  # mac os
  if [[ `uname -s` == *"Darwin"* ]]; then
    # only attempt to download for them if brew is installed
    if [ -x "$(command -v brew)" ]; then
      read -p "$DOWNLOAD_MSG" -n 1 -r
      echo
      if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew update && brew install redis
      else
        echo -e $EXITING_MSG
        return
      fi
    else
      echo -e $EXITING_MSG
      return 1
    fi

  # linux
  elif [[ `uname -s` == *"Linux"* ]]; then
    read -p "$DOWNLOAD_MSG" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      sudo apt-get update
      sudo apt-get install redis-server
    else
      echo -e $EXITING_MSG
      return 1
    fi
  else
    echo -e $EXITING_MSG
    return 1
  fi
fi

# need pip to be installed
if [ -x "$(command -v pip3)" ]; then
  echo -e "${GREEN}pip3.5 is installed${NC}"
else
  echo -e "${RED}$MISSING_MSG: pip3.5${NC}"
  # mac os
  if [[ `uname -s` == *"Darwin"* ]]; then
    # only attempt to download for them if brew is installed
    if [ -x "$(command -v brew)" ]; then
      read -p "$DOWNLOAD_MSG" -n 1 -r
      echo
      if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew update && brew install python3
      else
        echo -e $EXITING_MSG
        return
      fi
    else
      echo -e $EXITING_MSG
      return 1
    fi

  # linux
  elif [[ `uname -s` == *"Linux"* ]]; then
    read -p "$DOWNLOAD_MSG" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      sudo apt-get update
      sudo apt-get install python3-pip
    else
      echo -e $EXITING_MSG
      return 1
    fi
  else
    echo -e $EXITING_MSG
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
    pip3 install virtualenv
  else
    echo -e $EXITING_MSG
    return 1
  fi
fi

# setup virtualenv
if [ -d "$VIRTUALENV_DIR" ]; then
  echo -e "${GREEN}virtualenv is set up${NC}"
else
  echo -e "${GREEN}Setting up virtualenv...${NC}"
  virtualenv -p python3.5 $VIRTUALENV_DIR
fi

echo -e "${GREEN}Activating virtualenv...${NC}"
source $VIRTUALENV_DIR/bin/activate

# need to add python headers to path for xxhash
if [[ `uname -s` == *"Linux"* ]]; then
  echo "Including python headers to path..."
  sudo apt-get install python3-dev
  export C_INCLUDE_PATH=/usr/include/python3.4
fi

echo "Installing requirements..."
pip install -r requirements.txt

echo -e "${GREEN}Dependencies have been installed!${NC}"
