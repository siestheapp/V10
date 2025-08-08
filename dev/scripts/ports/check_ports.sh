#!/bin/bash

# Port Status Checker - Simple Shell Version
# Quick and lightweight port checking script

echo "================================================================================"
echo "PORT STATUS CHECK - $(date)"
echo "================================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ports of interest for your project
PORTS_OF_INTEREST=(5001 5002)

echo -e "\n${BLUE}🎯 CHECKING PORTS OF INTEREST:${NC}"
echo "--------------------------------------------------------------------------------"

for port in "${PORTS_OF_INTEREST[@]}"; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Port $port: ACTIVE${NC}"
        echo "   Process details:"
        lsof -i :$port | grep LISTEN | while read line; do
            echo "   $line"
        done
    else
        echo -e "${RED}❌ Port $port: INACTIVE${NC}"
    fi
    echo
done

echo -e "\n${BLUE}📊 ALL ACTIVE LISTENING PORTS:${NC}"
echo "--------------------------------------------------------------------------------"
echo -e "${YELLOW}PORT     PROTOCOL  ADDRESS                    PROCESS${NC}"
echo "--------------------------------------------------------------------------------"

# Get all listening ports with process info
netstat -an | grep LISTEN | while read line; do
    # Extract port from netstat output
    port=$(echo "$line" | awk '{print $4}' | sed 's/.*\.//')
    protocol=$(echo "$line" | awk '{print $1}')
    address=$(echo "$line" | awk '{print $4}')
    
    # Get process info for this port
    process_info=$(lsof -i :$port 2>/dev/null | grep LISTEN | head -1 | awk '{print $1 " (PID:" $2 ")"}')
    
    # Highlight ports of interest
    if [[ " ${PORTS_OF_INTEREST[@]} " =~ " ${port} " ]]; then
        echo -e "${GREEN}🔥 $port     $protocol     $address     $process_info${NC}"
    else
        echo "$port     $protocol     $address     $process_info"
    fi
done | sort -n

echo -e "\n${BLUE}📋 QUICK SUMMARY:${NC}"
echo "--------------------------------------------------------------------------------"
total_ports=$(netstat -an | grep LISTEN | wc -l | tr -d ' ')
echo "Total listening ports: $total_ports"

echo -e "\n${BLUE}🔧 USEFUL COMMANDS:${NC}"
echo "--------------------------------------------------------------------------------"
echo "• Check specific port: lsof -i :PORT_NUMBER"
echo "• Kill process on port: kill -9 \$(lsof -t -i:PORT_NUMBER)"
echo "• Check all connections: netstat -an"
echo "• Monitor ports continuously: watch -n 2 'netstat -an | grep LISTEN'"

echo -e "\n🔥 = Ports of interest for your project"
echo "================================================================================"
