#!/usr/bin/env bash

# check script arguments

ARGS=1         # Script requires 3 arguments.

if [ $# -ne "$ARGS" ]
then
    echo "Usage: $0 [filename]"
    exit 1
fi

FILE=$1
DIRECTORY=`dirname $FILE`

# check that filename exists

if [ -f "$FILE" ]; then
    # need to set parent directory to sticky bit to prevent users from deleting
    chmod +t $DIRECTORY || { echo "$0: chmod +t $DIRECTORY failed"; exit 1; }
    # change owner of files parent directory because if the user owns the directory they can 
    # delete the file, even with sticky bit set
    chown shotgun $DIRECTORY || { echo "$0: chown shotgun $DIRECTORY failed"; exit 1; }
    # set file read only
    chmod 0444 $FILE || { echo "$0: chmod 0444 $FILE failed"; exit 1; }
    # change owner of file as they can still delete their own files
    chown shotgun $FILE || { echo "$0: chown shotgun $FILE failed"; exit 1; }
else 
    echo "$0: $FILE does not exist."
    exit 1
fi
