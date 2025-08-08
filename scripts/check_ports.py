#!/usr/bin/env python3
"""
Port Status Checker Script
Checks the status of all active ports on the system and highlights specific ports of interest.
"""

import subprocess
import sys
import re
from typing import List, Dict, Tuple
from datetime import datetime

class PortChecker:
    def __init__(self):
        self.ports_of_interest = [5001, 5002]  # Your project-specific ports
        
    def get_active_ports(self) -> List[Dict]:
        """Get all active ports using netstat and lsof"""
        active_ports = []
        
        try:
            # Use netstat to get listening ports
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'LISTEN' in line:
                        # Parse netstat output
                        parts = line.split()
                        if len(parts) >= 4:
                            address = parts[3]
                            if '.' in address:
                                try:
                                    port = int(address.split('.')[-1])
                                    protocol = parts[0].lower()
                                    active_ports.append({
                                        'port': port,
                                        'protocol': protocol,
                                        'address': address,
                                        'status': 'LISTEN',
                                        'process': None
                                    })
                                except ValueError:
                                    continue
        except Exception as e:
            print(f"Error running netstat: {e}")
        
        # Enhance with lsof data to get process information
        self._enhance_with_process_info(active_ports)
        
        return active_ports
    
    def _enhance_with_process_info(self, ports: List[Dict]):
        """Enhance port information with process details using lsof"""
        try:
            result = subprocess.run(['lsof', '-i', '-P', '-n'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')[1:]  # Skip header
                for line in lines:
                    if 'LISTEN' in line:
                        parts = line.split()
                        if len(parts) >= 9:
                            process_name = parts[0]
                            pid = parts[1]
                            user = parts[2]
                            node_info = parts[8]
                            
                            # Extract port from node info (format: *:port or ip:port)
                            port_match = re.search(r':(\d+)$', node_info)
                            if port_match:
                                port_num = int(port_match.group(1))
                                
                                # Find matching port in our list and update
                                for port_info in ports:
                                    if port_info['port'] == port_num and not port_info['process']:
                                        port_info['process'] = {
                                            'name': process_name,
                                            'pid': pid,
                                            'user': user
                                        }
                                        break
        except Exception as e:
            print(f"Error running lsof: {e}")
    
    def check_specific_port(self, port: int) -> Dict:
        """Check if a specific port is active"""
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 9:
                            return {
                                'port': port,
                                'active': True,
                                'process': {
                                    'name': parts[0],
                                    'pid': parts[1],
                                    'user': parts[2]
                                },
                                'status': 'LISTEN' if 'LISTEN' in line else 'ESTABLISHED'
                            }
            return {'port': port, 'active': False}
        except Exception as e:
            return {'port': port, 'active': False, 'error': str(e)}
    
    def format_output(self, ports: List[Dict]):
        """Format and display the port information"""
        print("=" * 80)
        print(f"PORT STATUS CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Check specific ports of interest first
        print("\n🎯 PORTS OF INTEREST:")
        print("-" * 40)
        for port in self.ports_of_interest:
            port_info = self.check_specific_port(port)
            if port_info['active']:
                process = port_info.get('process', {})
                print(f"✅ Port {port}: ACTIVE")
                print(f"   Process: {process.get('name', 'Unknown')} (PID: {process.get('pid', 'Unknown')})")
                print(f"   User: {process.get('user', 'Unknown')}")
                print(f"   Status: {port_info.get('status', 'Unknown')}")
            else:
                print(f"❌ Port {port}: INACTIVE")
                if 'error' in port_info:
                    print(f"   Error: {port_info['error']}")
            print()
        
        # Display all active ports
        print("\n📊 ALL ACTIVE PORTS:")
        print("-" * 80)
        print(f"{'PORT':<8} {'PROTOCOL':<10} {'ADDRESS':<25} {'PROCESS':<20} {'PID':<8} {'USER':<12}")
        print("-" * 80)
        
        # Sort ports by port number
        sorted_ports = sorted(ports, key=lambda x: x['port'])
        
        for port_info in sorted_ports:
            port = port_info['port']
            protocol = port_info.get('protocol', 'unknown')
            address = port_info.get('address', 'unknown')
            process = port_info.get('process')
            
            if process:
                process_name = process.get('name', 'unknown')[:19]
                pid = process.get('pid', 'unknown')
                user = process.get('user', 'unknown')[:11]
            else:
                process_name = 'unknown'
                pid = 'unknown'
                user = 'unknown'
            
            # Highlight ports of interest
            marker = "🔥" if port in self.ports_of_interest else "  "
            
            print(f"{marker}{port:<6} {protocol:<10} {address:<25} {process_name:<20} {pid:<8} {user:<12}")
        
        print("\n" + "=" * 80)
        print(f"Total active ports: {len(sorted_ports)}")
        print("🔥 = Ports of interest for your project")
    
    def run(self):
        """Main execution method"""
        print("Checking port status...")
        active_ports = self.get_active_ports()
        self.format_output(active_ports)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # If port numbers are provided as arguments, check only those
        try:
            specific_ports = [int(arg) for arg in sys.argv[1:]]
            checker = PortChecker()
            checker.ports_of_interest = specific_ports
            checker.run()
        except ValueError:
            print("Error: Please provide valid port numbers as arguments")
            sys.exit(1)
    else:
        # Check all ports
        checker = PortChecker()
        checker.run()

if __name__ == "__main__":
    main()
