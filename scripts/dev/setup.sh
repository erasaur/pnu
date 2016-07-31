#!/usr/bin/env bash

# TODO set project root
# TODO automatically setup python env
# TODO automatically install requirements
# TODO install style if dev environment
# PROJECT_ROOT=/opt/pnu

# setup app logs
mkdir -p pnu/etc/logs
touch pnu/etc/logs/logging.out

# setup redis
mkdir -p db/user/logs db/pending/logs
touch db/user/logs/redis-server.log
touch db/pending/logs/redis-server.log
