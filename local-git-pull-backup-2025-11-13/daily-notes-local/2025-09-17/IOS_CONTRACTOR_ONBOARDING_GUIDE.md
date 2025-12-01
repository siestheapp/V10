# iOS Performance Contractor Onboarding Guide
> Created: 2025-09-17
> Base Branch: revert-to-a42786  
> Purpose: Secure onboarding for iOS performance optimization

## 🔐 Security Architecture

### Repository Structure
```
Your Actual Work: revert-to-a42786 branch (keep private)
     ↓ (create from this)
Contractor Branch: contractor-ios-performance-2025-09 (sanitized)
     ↓ (contractor forks)
Contractor Fork: Their own GitHub repo
     ↓ (they submit PRs)
Your Review: Merge approved changes back to revert-to-a42786
```

## 📋 Pre-Onboarding Steps

### 1. Post Job on Upwork

**Job Title**: iOS SwiftUI Performance Optimization - Fix UI Lag

**Job Description**:
```
Looking for an experienced iOS developer to optimize our SwiftUI app's performance.

Current Issues:
- Tab switching takes 450ms (need <200ms)
- List scrolling at 20 FPS (need 55+ FPS)
- Button response delays of 350ms (need <100ms)

Requirements:
- 3+ years SwiftUI experience
- Expert with Instruments profiling
- Own a Mac with Xcode 15+
- Available for 2-week project
- Daily progress updates

Deliverables:
- Performance audit with Instruments analysis
- Optimized code with measured improvements
- Documentation of all changes

Budget: $[X] fixed price
Timeline: 2 weeks
```

### 2. Screen Candidates

Ask these questions:
1. "Describe a SwiftUI performance issue you've solved"
2. "What Instruments tools do you use for iOS profiling?"
3. "How would you optimize a SwiftUI list with 1000+ items?"
4. "What causes tab switching lag in SwiftUI?"

### 3. Legal Setup

- Use Upwork's standard NDA
- Set up milestone payments:
  - 25%: Performance audit complete
  - 50%: Initial optimizations implemented
  - 25%: Final fixes and documentation

## 🚀 Day 0: Preparation

### Create Contractor Branch

```bash
# From your V10 directory
cd /Users/seandavey/projects/V10

# Run the preparation script
chmod +x daily-notes/2025-09-17/prepare_contractor_branch.sh
./daily-notes/2025-09-17/prepare_contractor_branch.sh

# This will:
# 1. Create contractor-ios-performance-2025-09 from revert-to-a42786
# 2. Remove all sensitive files
# 3. Configure iOS app for mock mode
# 4. Return you to revert-to-a42786
```

### Verify Sanitization

```bash
# Switch to contractor branch to verify
git checkout contractor-ios-performance-2025-09

# Check no sensitive files exist
ls db_config.py  # Should not exist (only mock version)
ls .env*         # Should not exist
ls -la src/ios_app/Backend/  # Should be mostly empty
ls daily-notes/  # Should not exist

# Return to your branch
git checkout revert-to-a42786
```

## 📧 Day 1: Contractor Onboarding

### Initial Message Template

```
Subject: V10 iOS Performance Project - Getting Started

Hi [Name],

Welcome to the V10 iOS performance optimization project!

**Repository Access**:
- GitHub: [your-repo-url]
- Branch: contractor-ios-performance-2025-09
- Please fork the repository and work from your fork

**Setup Instructions**:
1. Fork the repository
2. Clone your fork locally
3. Check out the contractor-ios-performance-2025-09 branch
4. Open src/ios_app/V10.xcodeproj in Xcode
5. Build and run on iPhone 15 Pro simulator
6. The app will use mock data (no backend needed)

**Documentation**:
- Read CONTRACTOR_README.md for project overview
- Review PERFORMANCE_BASELINE.md for current metrics

**First Tasks**:
1. Run the app and observe the lag issues
2. Profile with Instruments (Cmd+I in Xcode)
3. Send initial findings by end of day

Let's have a 15-minute call at [time] to review the performance issues.

Best regards,
[Your name]
```

### GitHub Setup

1. **Add as Outside Collaborator**:
   - Go to Settings → Manage access
   - Click "Invite a collaborator"
   - Add contractor's GitHub username
   - Grant READ access only initially

2. **Configure Branch Protection**:
   - Settings → Branches
   - Add rule for `contractor-ios-performance-2025-09`
   - Require pull request reviews
   - Dismiss stale reviews
   - Restrict who can push

3. **Contractor Workflow**:
   ```
   They fork → Make changes → Submit PR → You review → Merge to contractor branch
   Later: You cherry-pick approved changes to revert-to-a42786
   ```

## 📊 Daily Management

### Morning Routine (5 min)

1. **Check GitHub Activity**:
   ```bash
   cd /Users/seandavey/projects/V10
   # See what files they've accessed
   git fetch origin
   git log origin/contractor-ios-performance-2025-09 --oneline -10
   ```

2. **Review Any PRs**:
   - Check only iOS files were modified
   - Verify no Config.swift URL changes
   - Look for suspicious patterns

3. **Send Morning Check-in**:
   ```
   "Good morning! What's the focus for today?"
   ```

### Evening Routine (10 min)

1. **Request Status Update**:
   ```
   "Hi [Name], please share:
   - What you investigated today
   - Any bottlenecks found (with measurements)
   - Tomorrow's plan
   - Any blockers?"
   ```

2. **Review Their Commits**:
   ```bash
   # If they have push access to their fork
   git remote add contractor https://github.com/[their-username]/V10.git
   git fetch contractor
   git diff contractor-ios-performance-2025-09 contractor/[their-branch]
   ```

## 🔍 Monitoring Script

Create this monitoring script:

```bash:daily-notes/2025-09-17/monitor_contractor.sh
#!/bin/bash

echo "📊 Contractor Activity Report"
echo "Date: $(date)"
echo "Branch: contractor-ios-performance-2025-09"
echo ""

# Fetch latest
git fetch origin contractor-ios-performance-2025-09

# Show recent commits
echo "Recent Commits:"
git log origin/contractor-ios-performance-2025-09 --author="[contractor-email]" --oneline -10

# Check for suspicious file access
echo ""
echo "Files Modified:"
git diff --name-only revert-to-a42786..origin/contractor-ios-performance-2025-09

# Look for concerning patterns
echo ""
echo "Checking for security concerns..."
git diff revert-to-a42786..origin/contractor-ios-performance-2025-09 | grep -E "(password|api_key|token|SECRET|\.env|db_config|Backend/)" || echo "✅ No concerns found"
```

## ⚠️ Red Flags & Responses

### They Ask For Database Access
**Red Flag**: "I need to see the database to understand the data flow"
**Response**: "The performance issues are purely in the iOS UI layer. The mock data provider gives you the same data structure and volume for testing."

### They Want Backend Access
**Red Flag**: "The lag might be from API calls"
**Response**: "We've already profiled that. The lag persists even with instant mock responses. Please focus on UI rendering optimization."

### They Try to Add Analytics
**Red Flag**: PR includes Firebase, Amplitude, or tracking code
**Response**: "Please remove analytics code. We only need performance improvements, not tracking."

### They Modify Config.swift URLs
**Red Flag**: Changes to baseURL or attempts to connect to external servers
**Response**: "Please revert Config.swift changes. The app must remain in mock mode."

## ✅ Accepting Their Work

### PR Review Checklist

```markdown
- [ ] Only iOS files modified
- [ ] No new external dependencies
- [ ] Config.swift unchanged
- [ ] No network requests added
- [ ] Performance improvements verified
- [ ] Code is readable and documented
- [ ] No binary files or obfuscated code
```

### Merging Process

```bash
# 1. Review their PR on GitHub
# 2. Test locally
git fetch origin
git checkout contractor-ios-performance-2025-09
git pull origin contractor-ios-performance-2025-09

# 3. Build and test in Xcode
cd src/ios_app
open V10.xcodeproj
# Run and verify improvements

# 4. Merge to your working branch
git checkout revert-to-a42786
git cherry-pick [specific-commits]  # Only take what you need
# OR
git merge contractor-ios-performance-2025-09 --squash
git commit -m "iOS performance optimizations from contractor"
```

## 🏁 Project Completion

### Final Steps

1. **Get Deliverables**:
   - Performance improvement report
   - Instruments trace files
   - Documentation of changes
   - List of any remaining issues

2. **Release Payment**:
   - Verify all milestones met
   - Release final payment on Upwork

3. **Revoke Access Immediately**:
   ```bash
   # Remove GitHub access
   # Go to Settings → Manage access → Remove
   
   # Delete contractor branch
   git push origin --delete contractor-ios-performance-2025-09
   
   # Remove their remote
   git remote remove contractor
   ```

4. **Cleanup**:
   ```bash
   # Remove contractor files
   rm CONTRACTOR_README.md
   rm PERFORMANCE_BASELINE.md
   
   # Restore original Config.swift if needed
   cp src/ios_app/V10/App/Config.swift.backup src/ios_app/V10/App/Config.swift
   rm src/ios_app/V10/App/Config.swift.backup
   
   git add .
   git commit -m "Cleanup after contractor project"
   ```

## 💡 Tips for Success

### Do's
- ✅ Be specific about what's slow (show them exactly)
- ✅ Provide good mock data (1000+ items)
- ✅ Respond quickly to questions
- ✅ Test their changes yourself
- ✅ Document everything

### Don'ts
- ❌ Don't share your working branch (revert-to-a42786)
- ❌ Don't give write access to main repo
- ❌ Don't share real API endpoints
- ❌ Don't leave access open after project ends
- ❌ Don't merge without testing

## 🆘 Emergency Procedures

### If They Access Sensitive Files

1. **Immediate Actions**:
   ```bash
   # Revoke access NOW
   # GitHub Settings → Remove collaborator
   
   # Check what they accessed
   git log --author="[their-email]" --name-only
   ```

2. **Damage Control**:
   - Change any exposed credentials
   - Audit git history for data leaks
   - Document incident for Upwork

### If Performance Gets Worse

1. **Don't Panic**:
   - Don't merge their changes
   - Ask for explanation
   - Get second opinion if needed

2. **Recovery**:
   ```bash
   # Revert to your working state
   git checkout revert-to-a42786
   # Continue without their changes
   ```

## 📞 Getting Help

If you're unsure about:
- Whether to grant a request
- How to handle a situation
- Security concerns

Better to be cautious and ask for help than to expose sensitive data.

---

Remember: The contractor only needs iOS code to fix the performance issues. Everything else should remain private.
