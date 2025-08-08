#!/usr/bin/env python3
"""
Port Killer Script
Safely kills processes running on specified ports with confirmation prompts.
"""

import subprocess
import sys
import argparse
from typing import List, Dict, Optional
from datetime import datetime

class PortKiller:
    def __init__(self, force: bool = False, quiet: bool = False):
        self.force = force
        self.quiet = quiet
        self.project_ports = [5001, 5002]  # Your project-specific ports
        
    def get_process_on_port(self, port: int) -> Optional[Dict]:
        """Get process information for a specific port"""
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip() and 'LISTEN' in line:
                        parts = line.split()
                        if len(parts) >= 9:
                            return {
                                'port': port,
                                'process_name': parts[0],
                                'pid': parts[1],
                                'user': parts[2],
                                'command': ' '.join(parts[8:]) if len(parts) > 8 else 'unknown'
                            }
            return None
        except Exception as e:
            if not self.quiet:
                print(f"Error checking port {port}: {e}")
            return None
    
    def kill_process(self, pid: str, process_name: str, port: int) -> bool:
        """Kill a process by PID"""
        try:
            # First try graceful termination (SIGTERM)
            result = subprocess.run(['kill', pid], capture_output=True, text=True)
            if result.returncode == 0:
                if not self.quiet:
                    print(f"✅ Gracefully terminated {process_name} (PID: {pid}) on port {port}")
                return True
            else:
                # If graceful termination fails, try force kill (SIGKILL)
                result = subprocess.run(['kill', '-9', pid], capture_output=True, text=True)
                if result.returncode == 0:
                    if not self.quiet:
                        print(f"⚡ Force killed {process_name} (PID: {pid}) on port {port}")
                    return True
                else:
                    if not self.quiet:
                        print(f"❌ Failed to kill {process_name} (PID: {pid}) on port {port}")
                        print(f"   Error: {result.stderr}")
                    return False
        except Exception as e:
            if not self.quiet:
                print(f"❌ Error killing process {pid}: {e}")
            return False
    
    def confirm_kill(self, process_info: Dict) -> bool:
        """Ask user for confirmation before killing a process"""
        if self.force:
            return True
            
        port = process_info['port']
        process_name = process_info['process_name']
        pid = process_info['pid']
        user = process_info['user']
        
        print(f"\n🔍 Found process on port {port}:")
        print(f"   Process: {process_name}")
        print(f"   PID: {pid}")
        print(f"   User: {user}")
        
        # Special handling for project ports
        if port in self.project_ports:
            print(f"   ⚠️  This is one of your project ports!")
        
        while True:
            response = input(f"\nKill this process? [y/N]: ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no")
    
    def kill_port(self, port: int) -> bool:
        """Kill process on a specific port"""
        process_info = self.get_process_on_port(port)
        
        if not process_info:
            if not self.quiet:
                print(f"ℹ️  No process found listening on port {port}")
            return False
        
        if self.confirm_kill(process_info):
            return self.kill_process(process_info['pid'], process_info['process_name'], port)
        else:
            if not self.quiet:
                print(f"⏭️  Skipped killing process on port {port}")
            return False
    
    def kill_project_ports(self) -> List[bool]:
        """Kill processes on project-specific ports"""
        if not self.quiet:
            print("🎯 Killing processes on project ports...")
        
        results = []
        for port in self.project_ports:
            results.append(self.kill_port(port))
        
        return results
    
    def kill_all_ports(self) -> List[bool]:
        """Kill processes on all listening ports (DANGEROUS - requires confirmation)"""
        if not self.force:
            print("⚠️  WARNING: This will attempt to kill ALL processes listening on ports!")
            print("This includes system services and other applications.")
            response = input("Are you ABSOLUTELY sure? Type 'YES' to continue: ")
            if response != 'YES':
                print("❌ Aborted.")
                return []
        
        # Get all listening ports
        try:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            ports = []
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'LISTEN' in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            address = parts[3]
                            if '.' in address:
                                try:
                                    port = int(address.split('.')[-1])
                                    if port not in ports:
                                        ports.append(port)
                                except ValueError:
                                    continue
            
            results = []
            for port in sorted(ports):
                results.append(self.kill_port(port))
            
            return results
            
        except Exception as e:
            if not self.quiet:
                print(f"Error getting port list: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Kill processes on specified ports')
    parser.add_argument('ports', nargs='*', type=int, help='Port numbers to kill processes on')
    parser.add_argument('--project', action='store_true', help='Kill processes on project ports (5001, 5002)')
    parser.add_argument('--all', action='store_true', help='Kill processes on ALL ports (DANGEROUS)')
    parser.add_argument('--force', '-f', action='store_true', help='Force kill without confirmation')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode - minimal output')
    
    args = parser.parse_args()
    
    killer = PortKiller(force=args.force, quiet=args.quiet)
    
    if not args.quiet:
        print("=" * 80)
        print(f"PORT KILLER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    success_count = 0
    total_count = 0
    
    if args.all:
        # Kill all ports
        results = killer.kill_all_ports()
        total_count = len(results)
        success_count = sum(results)
    elif args.project:
        # Kill project ports
        results = killer.kill_project_ports()
        total_count = len(results)
        success_count = sum(results)
    elif args.ports:
        # Kill specific ports
        results = []
        for port in args.ports:
            results.append(killer.kill_port(port))
        total_count = len(results)
        success_count = sum(results)
    else:
        # No arguments - show help and offer to kill project ports
        parser.print_help()
        print(f"\n💡 Quick options:")
        print(f"   Kill project ports: python3 {sys.argv[0]} --project")
        print(f"   Kill specific port: python3 {sys.argv[0]} 8080")
        print(f"   Force kill (no prompts): python3 {sys.argv[0]} --project --force")
        
        response = input(f"\nWould you like to kill processes on your project ports (5001, 5002)? [y/N]: ")
        if response.strip().lower() in ['y', 'yes']:
            results = killer.kill_project_ports()
            total_count = len(results)
            success_count = sum(results)
    
    if total_count > 0 and not args.quiet:
        print(f"\n📊 Summary: {success_count}/{total_count} processes killed successfully")
        if success_count < total_count:
            print("⚠️  Some processes could not be killed. They may require sudo privileges.")

if __name__ == "__main__":
    main()
