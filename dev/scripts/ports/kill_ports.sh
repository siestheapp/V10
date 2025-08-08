#!/bin/bash

# Port Killer Script - Simple Shell Version
# Safely kills processes on specified ports

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project ports
PROJECT_PORTS=(5001 5002)

# Function to kill process on a specific port
kill_port() {
    local port=$1
    local force=$2
    
    # Check if port is active
    if ! lsof -i :$port > /dev/null 2>&1; then
        echo -e "${YELLOW}ℹ️  No process found on port $port${NC}"
        return 1
    fi
    
    # Get process info
    local process_info=$(lsof -i :$port | grep LISTEN | head -1)
    local pid=$(echo "$process_info" | awk '{print $2}')
    local process_name=$(echo "$process_info" | awk '{print $1}')
    local user=$(echo "$process_info" | awk '{print $3}')
    
    echo -e "\n${BLUE}🔍 Found process on port $port:${NC}"
    echo "   Process: $process_name"
    echo "   PID: $pid"
    echo "   User: $user"
    
    # Check if it's a project port
    if [[ " ${PROJECT_PORTS[@]} " =~ " ${port} " ]]; then
        echo -e "   ${YELLOW}⚠️  This is one of your project ports!${NC}"
    fi
    
    # Ask for confirmation unless force mode
    if [[ "$force" != "true" ]]; then
        echo -n -e "\nKill this process? [y/N]: "
        read -r response
        if [[ ! "$response" =~ ^[Yy]([Ee][Ss])?$ ]]; then
            echo -e "${YELLOW}⏭️  Skipped killing process on port $port${NC}"
            return 1
        fi
    fi
    
    # Try graceful termination first
    if kill "$pid" 2>/dev/null; then
        sleep 1
        # Check if process is still running
        if ! kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}✅ Gracefully terminated $process_name (PID: $pid) on port $port${NC}"
            return 0
        fi
    fi
    
    # Force kill if graceful termination failed
    if kill -9 "$pid" 2>/dev/null; then
        echo -e "${GREEN}⚡ Force killed $process_name (PID: $pid) on port $port${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to kill $process_name (PID: $pid) on port $port${NC}"
        return 1
    fi
}

# Function to kill project ports
kill_project_ports() {
    local force=$1
    echo -e "${BLUE}🎯 Killing processes on project ports...${NC}"
    
    local success=0
    local total=0
    
    for port in "${PROJECT_PORTS[@]}"; do
        ((total++))
        if kill_port "$port" "$force"; then
            ((success++))
        fi
    done
    
    echo -e "\n${BLUE}📊 Summary: $success/$total project processes killed${NC}"
}

# Function to kill all listening ports
kill_all_ports() {
    local force=$1
    
    if [[ "$force" != "true" ]]; then
        echo -e "${RED}⚠️  WARNING: This will attempt to kill ALL processes listening on ports!${NC}"
        echo "This includes system services and other applications."
        echo -n "Are you ABSOLUTELY sure? Type 'YES' to continue: "
        read -r response
        if [[ "$response" != "YES" ]]; then
            echo -e "${RED}❌ Aborted.${NC}"
            return 1
        fi
    fi
    
    # Get all listening ports
    local ports=($(netstat -an | grep LISTEN | awk '{print $4}' | sed 's/.*\.//' | sort -n | uniq))
    
    local success=0
    local total=0
    
    for port in "${ports[@]}"; do
        if [[ "$port" =~ ^[0-9]+$ ]]; then
            ((total++))
            if kill_port "$port" "true"; then  # Force mode for all ports
                ((success++))
            fi
        fi
    done
    
    echo -e "\n${BLUE}📊 Summary: $success/$total processes killed${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [PORTS...]"
    echo ""
    echo "Options:"
    echo "  --project, -p     Kill processes on project ports (5001, 5002)"
    echo "  --all, -a         Kill processes on ALL ports (DANGEROUS)"
    echo "  --force, -f       Force kill without confirmation prompts"
    echo "  --help, -h        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 8080           Kill process on port 8080"
    echo "  $0 5001 5002      Kill processes on ports 5001 and 5002"
    echo "  $0 --project      Kill processes on project ports"
    echo "  $0 --project -f   Force kill project ports without prompts"
    echo "  $0 --all -f       Force kill ALL port processes (DANGEROUS)"
}

# Main script
main() {
    echo "================================================================================"
    echo "PORT KILLER - $(date)"
    echo "================================================================================"
    
    local force="false"
    local project="false"
    local all_ports="false"
    local specific_ports=()
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --project|-p)
                project="true"
                shift
                ;;
            --all|-a)
                all_ports="true"
                shift
                ;;
            --force|-f)
                force="true"
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            -*)
                echo -e "${RED}Unknown option: $1${NC}"
                show_usage
                exit 1
                ;;
            *)
                if [[ "$1" =~ ^[0-9]+$ ]]; then
                    specific_ports+=("$1")
                else
                    echo -e "${RED}Invalid port number: $1${NC}"
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Execute based on options
    if [[ "$all_ports" == "true" ]]; then
        kill_all_ports "$force"
    elif [[ "$project" == "true" ]]; then
        kill_project_ports "$force"
    elif [[ ${#specific_ports[@]} -gt 0 ]]; then
        local success=0
        local total=${#specific_ports[@]}
        
        for port in "${specific_ports[@]}"; do
            if kill_port "$port" "$force"; then
                ((success++))
            fi
        done
        
        echo -e "\n${BLUE}📊 Summary: $success/$total processes killed${NC}"
    else
        # No arguments - show help and offer to kill project ports
        show_usage
        echo -e "\n${BLUE}💡 Quick options:${NC}"
        echo "   Kill project ports: $0 --project"
        echo "   Kill specific port: $0 8080"
        echo "   Force kill (no prompts): $0 --project --force"
        
        echo -n -e "\nWould you like to kill processes on your project ports (5001, 5002)? [y/N]: "
        read -r response
        if [[ "$response" =~ ^[Yy]([Ee][Ss])?$ ]]; then
            kill_project_ports "$force"
        fi
    fi
    
    echo -e "\n${YELLOW}💡 Tip: Use './scripts/check_ports.sh' to verify ports are now free${NC}"
    echo "================================================================================"
}

# Run main function
main "$@"
