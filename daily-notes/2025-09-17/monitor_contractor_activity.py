#!/usr/bin/env python3
"""
Monitor contractor's GitHub activity on the V10 repository.
Run daily to track changes and ensure security.
"""

import subprocess
import json
from datetime import datetime, timedelta
import sys
import re

class ContractorMonitor:
    def __init__(self, contractor_email=None, contractor_github=None):
        """Initialize monitor with contractor details."""
        self.contractor_email = contractor_email or "contractor@example.com"
        self.contractor_github = contractor_github or "contractor-username"
        self.branch_name = "contractor-ios-performance-2025-09"
        self.base_branch = "revert-to-a42786"
        self.report_file = f"contractor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
    def run_git_command(self, cmd):
        """Run a git command and return output."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return None
            
    def get_recent_commits(self, days=7):
        """Get contractor's commits from the last N days."""
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Try to fetch latest from contractor branch
        self.run_git_command(f"git fetch origin {self.branch_name} 2>/dev/null")
        
        # Get commits
        cmd = f"git log origin/{self.branch_name} --since={since_date} --pretty=format:'%h|%ad|%s|%an|%ae' --date=short"
        output = self.run_git_command(cmd)
        
        commits = []
        if output:
            for line in output.split('\n'):
                if line and '|' in line:
                    parts = line.strip("'").split('|')
                    if len(parts) >= 5:
                        commits.append({
                            'hash': parts[0],
                            'date': parts[1],
                            'message': parts[2],
                            'author': parts[3],
                            'email': parts[4]
                        })
        return commits
    
    def get_changed_files(self):
        """Get all files changed in contractor branch vs base branch."""
        cmd = f"git diff --name-only {self.base_branch}..origin/{self.branch_name} 2>/dev/null"
        output = self.run_git_command(cmd)
        
        if output:
            return [f for f in output.split('\n') if f]
        return []
    
    def check_suspicious_patterns(self):
        """Check for suspicious patterns in the changes."""
        suspicious_files = []
        security_concerns = []
        
        # Check changed files
        changed_files = self.get_changed_files()
        
        # Patterns that should NOT be accessed
        forbidden_patterns = [
            (r'db_config\.py$', 'Database configuration accessed'),
            (r'\.env', 'Environment variables accessed'),
            (r'Backend/(body_measurement|multi_dimensional|unified)', 'Proprietary algorithms accessed'),
            (r'\.sql$', 'SQL files accessed'),
            (r'dump.*\.json$', 'Data dumps accessed'),
            (r'daily-notes/', 'Private notes accessed'),
            (r'database_exports/', 'Database exports accessed'),
            (r'scrapers/', 'Scraper logic accessed'),
        ]
        
        for file in changed_files:
            for pattern, description in forbidden_patterns:
                if re.search(pattern, file):
                    suspicious_files.append(f"🚨 {file}: {description}")
                    break
        
        # Check actual code changes for concerning patterns
        diff_output = self.run_git_command(f"git diff {self.base_branch}..origin/{self.branch_name} 2>/dev/null")
        
        if diff_output:
            code_patterns = [
                (r'baseURL\s*=\s*"http', 'Attempting to change API endpoint'),
                (r'production|PRODUCTION', 'Reference to production environment'),
                (r'supabase|SUPABASE', 'Attempting to access Supabase'),
                (r'DELETE FROM|DROP TABLE|TRUNCATE', 'Database modification attempt'),
                (r'api[_-]key|API[_-]KEY', 'API key reference'),
                (r'password|PASSWORD', 'Password reference'),
                (r'eval\(|exec\(', 'Dangerous code execution'),
                (r'URLSession|Alamofire|AF\.request', 'Making network requests'),
                (r'subprocess|os\.system', 'System command execution'),
            ]
            
            for pattern, description in code_patterns:
                if re.search(pattern, diff_output, re.IGNORECASE):
                    security_concerns.append(f"⚠️ {description}")
        
        return suspicious_files, security_concerns
    
    def check_ios_only_changes(self):
        """Verify that only iOS files were modified."""
        changed_files = self.get_changed_files()
        non_ios_files = []
        
        for file in changed_files:
            # These are the ONLY acceptable paths for changes
            acceptable_paths = [
                r'^src/ios_app/V10/.*\.swift$',
                r'^src/ios_app/V10\.xcodeproj/',
                r'^src/ios_app/.*\.storyboard$',
                r'^src/ios_app/.*\.xcassets/',
                r'^CONTRACTOR_README\.md$',
                r'^PERFORMANCE_BASELINE\.md$',
            ]
            
            is_acceptable = False
            for pattern in acceptable_paths:
                if re.match(pattern, file):
                    is_acceptable = True
                    break
            
            if not is_acceptable:
                non_ios_files.append(file)
        
        return non_ios_files
    
    def analyze_performance_improvements(self):
        """Look for evidence of performance improvements in commit messages."""
        commits = self.get_recent_commits()
        improvements = []
        
        performance_keywords = [
            'optimize', 'performance', 'faster', 'speed',
            'lag', 'fps', 'memory', 'cache', 'lazy',
            'reduce', 'improve', 'fix slow', 'responsive'
        ]
        
        for commit in commits:
            msg_lower = commit['message'].lower()
            for keyword in performance_keywords:
                if keyword in msg_lower:
                    improvements.append(f"✅ {commit['hash']}: {commit['message']}")
                    break
        
        return improvements
    
    def generate_report(self):
        """Generate comprehensive monitoring report."""
        report = []
        report.append("# 📊 Contractor Activity Monitoring Report")
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Contractor Branch**: {self.branch_name}")
        report.append(f"**Base Branch**: {self.base_branch}")
        report.append("")
        
        # Get recent commits
        commits = self.get_recent_commits()
        report.append(f"## Recent Activity (Last 7 Days)")
        
        if not commits:
            report.append("✅ No commits found in the last 7 days")
        else:
            report.append(f"Found {len(commits)} commits:")
            report.append("")
            for commit in commits[:10]:  # Show max 10 recent commits
                report.append(f"- `{commit['hash']}` {commit['date']} - {commit['message']}")
                report.append(f"  Author: {commit['author']} ({commit['email']})")
            if len(commits) > 10:
                report.append(f"... and {len(commits)-10} more")
        
        report.append("")
        
        # Check for suspicious activity
        report.append("## 🔍 Security Analysis")
        
        suspicious_files, security_concerns = self.check_suspicious_patterns()
        
        if suspicious_files:
            report.append("### ⚠️ SUSPICIOUS FILE ACCESS DETECTED")
            for item in suspicious_files:
                report.append(f"- {item}")
            report.append("")
        
        if security_concerns:
            report.append("### 🚨 SECURITY CONCERNS IN CODE")
            for concern in security_concerns:
                report.append(f"- {concern}")
            report.append("")
        
        if not suspicious_files and not security_concerns:
            report.append("✅ No security concerns detected")
        
        report.append("")
        
        # Check iOS-only modifications
        report.append("## 📱 iOS-Only Verification")
        
        non_ios_files = self.check_ios_only_changes()
        if non_ios_files:
            report.append("### ⚠️ Non-iOS Files Modified")
            for file in non_ios_files:
                report.append(f"- {file}")
            report.append("")
            report.append("**Action Required**: Review these changes carefully!")
        else:
            report.append("✅ All changes are within iOS scope")
        
        report.append("")
        
        # Check for performance improvements
        report.append("## 🚀 Performance Work")
        
        improvements = self.analyze_performance_improvements()
        if improvements:
            report.append("Performance-related commits found:")
            for improvement in improvements:
                report.append(f"- {improvement}")
        else:
            report.append("⚠️ No clear performance-related commits found")
        
        report.append("")
        
        # Summary and recommendations
        report.append("## 📋 Summary & Recommendations")
        
        risk_level = "LOW"
        if suspicious_files or security_concerns:
            risk_level = "HIGH"
        elif non_ios_files:
            risk_level = "MEDIUM"
        
        report.append(f"**Risk Level**: {risk_level}")
        report.append("")
        
        if risk_level == "HIGH":
            report.append("### 🚨 IMMEDIATE ACTIONS REQUIRED:")
            report.append("1. Review all flagged files and code immediately")
            report.append("2. Consider revoking repository access")
            report.append("3. Audit for any data exfiltration attempts")
            report.append("4. Do NOT merge any changes without thorough review")
        elif risk_level == "MEDIUM":
            report.append("### ⚠️ ACTIONS REQUIRED:")
            report.append("1. Review non-iOS file modifications")
            report.append("2. Ask contractor to explain out-of-scope changes")
            report.append("3. Carefully test all changes before merging")
        else:
            report.append("### ✅ ALL CLEAR:")
            report.append("1. Contractor is working within expected scope")
            report.append("2. Continue normal review process")
            report.append("3. Test performance improvements before merging")
        
        report.append("")
        report.append("## 📊 Files Changed Summary")
        changed_files = self.get_changed_files()
        if changed_files:
            report.append(f"Total files changed: {len(changed_files)}")
            report.append("")
            report.append("```")
            for file in changed_files[:20]:  # Show max 20 files
                report.append(file)
            if len(changed_files) > 20:
                report.append(f"... and {len(changed_files)-20} more files")
            report.append("```")
        
        return "\n".join(report)
    
    def save_report(self):
        """Save report to file and display summary."""
        report_content = self.generate_report()
        
        # Save to file
        with open(self.report_file, 'w') as f:
            f.write(report_content)
        
        print(f"✅ Report saved to: {self.report_file}")
        print("")
        print("="*60)
        
        # Display summary
        lines = report_content.split('\n')
        
        # Find and display risk level
        for line in lines:
            if "Risk Level" in line:
                print(line)
                break
        
        print("")
        
        # Show security concerns if any
        if "SUSPICIOUS FILE ACCESS DETECTED" in report_content:
            print("🚨 SUSPICIOUS ACTIVITY DETECTED - Review report immediately!")
        elif "SECURITY CONCERNS IN CODE" in report_content:
            print("⚠️ Security concerns found - Review report")
        elif "Non-iOS Files Modified" in report_content:
            print("⚠️ Out-of-scope changes detected")
        else:
            print("✅ No security issues detected")
        
        print("="*60)
        print(f"\nFull report: {self.report_file}")

def main():
    """Main entry point."""
    print("🔍 V10 Contractor Activity Monitor")
    print("="*60)
    
    # You can pass contractor details as arguments or update here
    if len(sys.argv) > 1:
        contractor_email = sys.argv[1]
        contractor_github = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        # Default values - UPDATE THESE when you hire someone
        contractor_email = "contractor@example.com"
        contractor_github = "contractor-github-username"
        print("ℹ️  Using default contractor info. Pass email as argument to customize.")
        print(f"   Usage: python {sys.argv[0]} contractor@email.com github-username")
    
    print(f"Monitoring contractor: {contractor_email}")
    print("")
    
    monitor = ContractorMonitor(contractor_email, contractor_github)
    monitor.save_report()

if __name__ == "__main__":
    main()
