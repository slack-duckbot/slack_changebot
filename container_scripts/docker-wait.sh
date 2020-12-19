#!/bin/bash -e
#############################################################
# docker-wait.sh
# --------------
#
# Wait for a given port to be listening before proceeding to
# the command.
#############################################################
HOST="$1" ; shift
PORT="$1" ; shift
CMD="$@"
until $(timeout 1 bash -c "</dev/tcp/$HOST/$PORT")
do
	>&2 echo "Waiting for $HOST:$PORT to become available"
	sleep 0.5
done

>&2 echo "$HOST:$PORT is up - running: $CMD"
exec $CMD
