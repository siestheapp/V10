#!/bin/bash

echo "Killing all processes on ports 8080 and above..."

# Kill processes on ports 8080-8099
for port in {8080..8099}; do
    pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "Killing process $pid on port $port"
        kill -9 $pid
    fi
done

# Also kill any remaining expo/metro processes
pkill -f "expo"
pkill -f "metro"

echo "Done! All processes on ports 8080+ have been killed."
