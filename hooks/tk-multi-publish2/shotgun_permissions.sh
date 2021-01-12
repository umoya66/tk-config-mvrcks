#!/usr/bin/env bash

# check script arguments

ARGS=1         # Script requires 3 arguments.

if [ $# -ne "$ARGS" ]
then
    echo "Usage: `basename $0` filename"
    exit 1
fi

FILE=$1

# check that filename exists

if [ -f "$FILE" ]; then
        chmod 0444 $FILE
        chown shotgun $FILE
    else 
        echo "$FILE does not exist."
        exit 1
fi
