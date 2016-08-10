# bash script config variables
# including script needs to be run in root of project dir!

function get_pid {
  # returns the process id of the redis process
  echo `
    ps -ef | # display processes with their pids
    grep $1 | # get desired lines
    grep -v grep | # ignore lines with grep
    tr -s " " | # collapse spaces
    cut -d " " -f2 | # cut by spaces and grab pid column
    head -n 1 # get first line
  `
}

MAIN_PROCESS=main.py
REDIS_PROCESS=redis-server

# general
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# app config
APP_LOG_DIR=pnu/etc/logs
APP_LOG_FILE="$APP_LOG_DIR/logging.out"
VIRTUALENV_DIR=.venv

MAIN_LOG_FILE="$APP_LOG_DIR/main.out"
MAIN_ERR_FILE="$APP_LOG_DIR/main.err"

REDIS_USER_DUMP_DIR=db/user
REDIS_PENDING_DUMP_DIR=db/pending

# run dir is where dumpfiles will go
# service dir is where config files are read from
# run dir should match with the run dir specified in redis service files
if [ $PNU_ENV = "prod" ]; then
  REDIS_RUN_DIR=/var/run/redis
  REDIS_SERVICE_DIR=pnu/etc/redis/prod
  REDIS_PENDING_SERVICE=redis-pnu-pending-server
  REDIS_USER_SERVICE=redis-pnu-user-server
else
  REDIS_RUN_DIR=db
  REDIS_SERVICE_DIR=pnu/etc/redis/dev
  REDIS_PENDING_SERVICE=redis-server
  REDIS_USER_SERVICE=redis-server
fi

REDIS_RUN_PENDING_DIR=$REDIS_RUN_DIR
REDIS_RUN_USER_DIR=$REDIS_RUN_DIR

# these should match up with the paths specified in redis config files
REDIS_PENDING_LOG_FILE="$REDIS_RUN_PENDING_DIR/$REDIS_PENDING_SERVICE.log"
REDIS_USER_LOG_FILE="$REDIS_RUN_USER_DIR/$REDIS_USER_SERVICE.log"

# redis service file paths
REDIS_PENDING_SERVICE_FILE="$REDIS_SERVICE_DIR/$REDIS_PENDING_SERVICE"
REDIS_USER_SERVICE_FILE="$REDIS_SERVICE_DIR/$REDIS_USER_SERVICE"
