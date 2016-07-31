#!/bin/bash

REDIS_PROCESS=redis-server

redis-server pnu/etc/user_redis.conf
# returns the process id of the redis process
echo "`
  ps -f | # display processes with their pids
  grep $REDIS_PROCESS # get lines with redis-server
`"
