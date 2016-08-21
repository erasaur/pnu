#!/bin/bash
# tail the most recently written to log file
tail -f $(find . -name "logging.*" -type f -printf '%T@ %P\n' | sort -n | tail -1 | cut -f2 -d ' ')
