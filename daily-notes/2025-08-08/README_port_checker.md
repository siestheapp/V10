# Port Management Scripts

Complete port management toolkit with scripts to monitor and control port status on your system, with special attention to your project ports (5001 and 5002).

## Scripts Available

### 📊 Port Status Checkers

#### 1. Shell Script (Quick & Simple)
```bash
./scripts/check_ports.sh
```
- **Fast execution** - Uses native shell commands
- **Colorized output** - Easy to read with visual indicators
- **Lightweight** - No dependencies beyond standard Unix tools
- **Best for:** Quick checks and monitoring

#### 2. Python Script (Detailed & Flexible)
```bash
python3 scripts/check_ports.py
```
- **Detailed information** - More comprehensive port analysis
- **Structured output** - Well-formatted tables
- **Extensible** - Easy to modify and enhance
- **Best for:** Detailed analysis and scripting integration

### ⚡ Port Killers

#### 3. Shell Port Killer (Fast & Interactive)
```bash
./scripts/kill_ports.sh
```
- **Interactive prompts** - Confirms before killing processes
- **Safety features** - Special warnings for project ports
- **Colorized output** - Clear visual feedback
- **Best for:** Safe, interactive port management

#### 4. Python Port Killer (Advanced & Scriptable)
```bash
python3 scripts/kill_ports.py
```
- **Advanced options** - Quiet mode, force mode, selective killing
- **Graceful termination** - Tries SIGTERM before SIGKILL
- **Detailed logging** - Comprehensive process information
- **Best for:** Automation and advanced use cases

## Usage Examples

### 📊 Checking Port Status
```bash
# Quick check with shell script
./scripts/check_ports.sh

# Detailed check with Python script
python3 scripts/check_ports.py

# Check only specific ports
python3 scripts/check_ports.py 5001 5002 8080
```

### ⚡ Killing Port Processes

#### Safe Interactive Killing
```bash
# Kill project ports with prompts
./scripts/kill_ports.sh --project

# Kill specific port with confirmation
./scripts/kill_ports.sh 8080

# Kill multiple ports
./scripts/kill_ports.sh 5001 5002 8080
```

#### Advanced Killing Options
```bash
# Force kill project ports (no prompts)
python3 scripts/kill_ports.py --project --force

# Quiet mode (minimal output)
python3 scripts/kill_ports.py --project --quiet

# Kill specific ports
python3 scripts/kill_ports.py 8080 3000 9000

# DANGEROUS: Kill ALL port processes (requires confirmation)
./scripts/kill_ports.sh --all
```

## Output Features

Both scripts provide:
- ✅ **Status of your project ports** (5001, 5002) - highlighted with 🔥
- 📊 **Complete list of all active listening ports**
- 🔧 **Process information** (name, PID, user)
- 📋 **Summary statistics**
- 💡 **Helpful commands** for port management

## Your Project Ports

The scripts are pre-configured to monitor:
- **Port 5001** - Your first service
- **Port 5002** - Your second service

These ports are highlighted in the output for easy identification.

## Useful Commands Included

The scripts also provide quick reference for:
- `lsof -i :PORT` - Check specific port
- `kill -9 $(lsof -t -i:PORT)` - Kill process on port
- `netstat -an` - Check all connections
- `watch -n 2 'netstat -an | grep LISTEN'` - Monitor continuously

## Integration Tips

### Add to PATH for global access
```bash
# Add to your ~/.zshrc or ~/.bashrc
export PATH="$PATH:/Users/seandavey/projects/V10/scripts"

# Then use from anywhere:
check_ports.sh
```

### Create aliases
```bash
# Add to your shell profile
alias ports='cd /Users/seandavey/projects/V10 && ./scripts/check_ports.sh'
alias ports-detail='cd /Users/seandavey/projects/V10 && python3 scripts/check_ports.py'
alias kill-ports='cd /Users/seandavey/projects/V10 && ./scripts/kill_ports.sh'
alias kill-project='cd /Users/seandavey/projects/V10 && ./scripts/kill_ports.sh --project'
```

### Monitoring with watch
```bash
# Continuous monitoring
watch -n 5 './scripts/check_ports.sh'
```

## Current Status

Based on the last run, your services are:
- ✅ **Port 5001: ACTIVE** (Python process)
- ✅ **Port 5002: ACTIVE** (Python process)

Both services are running correctly! 🎉
