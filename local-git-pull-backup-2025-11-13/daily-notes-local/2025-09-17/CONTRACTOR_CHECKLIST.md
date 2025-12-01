# iOS Performance Contractor - Complete Checklist
> Base Branch: revert-to-a42786
> Target: Fix iOS app lag (buttons, tabs, scrolling)

## 📝 Phase 1: Hiring (Day -3 to Day 0)

### Upwork Job Posting
- [ ] Post job with title: "iOS SwiftUI Performance Expert - Fix UI Lag (2 weeks)"
- [ ] Set budget: $_____ fixed price (not hourly)
- [ ] Require portfolio examples of performance optimization
- [ ] Set milestone structure:
  - [ ] 25% - Performance audit delivered (Day 3)
  - [ ] 50% - Initial fixes implemented (Day 7)
  - [ ] 25% - Final optimizations & docs (Day 14)

### Screening Questions to Ask
- [ ] "Show me Instruments traces from past performance work"
- [ ] "How do you optimize SwiftUI list with 1000+ items?"
- [ ] "What causes tab switching delays in SwiftUI?"
- [ ] "Do you have your own Mac with Xcode 15+?"

### Before Selecting Contractor
- [ ] Verify they have 3+ years SwiftUI experience
- [ ] Confirm they own a Mac (required for iOS dev)
- [ ] Check their timezone for communication overlap
- [ ] Review their Upwork history (90%+ success rate)
- [ ] Get them to sign Upwork's NDA

## 🔧 Phase 2: Repository Preparation (Day -1)

### Create Safe Branch
```bash
cd /Users/seandavey/projects/V10

# Make sure you're on your working branch
git checkout revert-to-a42786
git pull origin revert-to-a42786

# Run preparation script
chmod +x daily-notes/2025-09-17/prepare_contractor_branch.sh
./daily-notes/2025-09-17/prepare_contractor_branch.sh
```

### Verify Sanitization
- [ ] Check contractor branch created: `contractor-ios-performance-2025-09`
- [ ] Verify sensitive files removed:
  ```bash
  git checkout contractor-ios-performance-2025-09
  ls -la | grep -E "(\.env|db_config\.py|\.sql)"  # Should be empty
  ls src/ios_app/Backend/  # Should have minimal files
  ls daily-notes/  # Should not exist
  git checkout revert-to-a42786  # Return to your branch
  ```

### GitHub Setup
- [ ] Go to repo Settings → Manage access
- [ ] Set up branch protection for `contractor-ios-performance-2025-09`:
  - [ ] Require pull request reviews
  - [ ] Dismiss stale reviews
  - [ ] No direct pushes allowed

### Document Current Performance
- [ ] Run app in Xcode with Instruments
- [ ] Record current metrics:
  - [ ] Tab switch time: _____ ms (target: <200ms)
  - [ ] Scroll FPS: _____ (target: 55+ FPS)
  - [ ] Button response: _____ ms (target: <100ms)
  - [ ] Memory at launch: _____ MB
  - [ ] Memory after 5 min: _____ MB
- [ ] Save .trace files for comparison

## 🚀 Phase 3: Day 1 - Onboarding

### Morning Tasks (Before contractor starts)
- [ ] Push contractor branch to GitHub:
  ```bash
  git push origin contractor-ios-performance-2025-09
  ```
- [ ] Prepare welcome message with:
  - [ ] Repository URL
  - [ ] Branch name: `contractor-ios-performance-2025-09`
  - [ ] Instructions to fork repo
  - [ ] Link to CONTRACTOR_README.md

### Send Onboarding Email
- [ ] Include:
  ```
  Subject: V10 Performance Project - Getting Started
  
  Hi [Name],
  
  Repository: [your-github-url]
  Branch: contractor-ios-performance-2025-09
  
  Please:
  1. Fork the repository
  2. Work from your fork
  3. Submit PRs for review
  
  First call at: [time] today
  ```

### Initial Call (15 minutes)
- [ ] Screen share and demonstrate the lag issues:
  - [ ] Show slow tab switching
  - [ ] Show choppy scrolling
  - [ ] Show button delay
- [ ] Confirm they can build the app
- [ ] Verify mock data is working
- [ ] Set daily update time: _____ AM/PM

### GitHub Access
- [ ] Add as outside collaborator (READ only)
- [ ] Confirm they've forked the repo
- [ ] Watch for their first commits

### End of Day 1
- [ ] Verify they submitted initial findings
- [ ] Check no suspicious file access:
  ```bash
  python daily-notes/2025-09-17/monitor_contractor_activity.py
  ```

## 📊 Phase 4: Daily Management (Days 2-13)

### Every Morning (5 minutes)
- [ ] Run monitoring script:
  ```bash
  cd /Users/seandavey/projects/V10
  python daily-notes/2025-09-17/monitor_contractor_activity.py
  ```
- [ ] Check report for:
  - [ ] ✅ Only iOS files modified
  - [ ] ✅ No Config.swift URL changes
  - [ ] ✅ No suspicious patterns
- [ ] Send morning check-in: "Good morning! What's today's focus?"

### Every Evening (10 minutes)
- [ ] Request status update:
  - [ ] What was investigated
  - [ ] Bottlenecks found (with numbers)
  - [ ] Tomorrow's plan
  - [ ] Any blockers
- [ ] Review any PRs submitted
- [ ] Test changes locally if PRs exist

### Red Flags to Watch For
- [ ] 🚨 Asks for database credentials → Say NO
- [ ] 🚨 Wants backend access → Say "performance is iOS-only"
- [ ] 🚨 Tries to add analytics → Reject PR
- [ ] 🚨 Modifies Config.swift URLs → Revert immediately
- [ ] 🚨 Adds external dependencies → Require justification

## ✅ Phase 5: Milestone Reviews

### Day 3: Performance Audit (25% payment)
- [ ] Receive Instruments traces
- [ ] Get bottleneck documentation
- [ ] Verify findings match your observations
- [ ] Approve milestone if satisfactory

### Day 7: Initial Fixes (50% payment)
- [ ] Test their fixes locally:
  ```bash
  git fetch origin
  git checkout contractor-ios-performance-2025-09
  git pull
  # Build in Xcode and test
  ```
- [ ] Measure improvements:
  - [ ] Tab switch: _____ ms (was _____ ms)
  - [ ] Scroll FPS: _____ (was _____)
  - [ ] Button response: _____ ms (was _____ ms)
- [ ] Approve milestone if improved

### Day 14: Final Delivery (25% payment)
- [ ] All optimizations complete
- [ ] Documentation received:
  - [ ] List of all changes
  - [ ] Performance measurements
  - [ ] Any trade-offs made
- [ ] Final testing passed
- [ ] Approve final milestone

## 🏁 Phase 6: Project Completion (Day 14)

### Code Integration
- [ ] Review all PRs thoroughly
- [ ] Test the complete app
- [ ] Merge approved changes to contractor branch:
  ```bash
  # On GitHub, merge their PRs to contractor-ios-performance-2025-09
  ```
- [ ] Cherry-pick to your working branch:
  ```bash
  git checkout revert-to-a42786
  git cherry-pick [commit-hashes]  # Only the good commits
  # OR merge everything
  git merge contractor-ios-performance-2025-09 --squash
  git commit -m "iOS performance optimizations from contractor"
  ```

### Access Revocation (IMMEDIATELY after payment)
- [ ] Remove GitHub collaborator access
- [ ] Delete contractor branch:
  ```bash
  git push origin --delete contractor-ios-performance-2025-09
  ```
- [ ] Clean up local branches:
  ```bash
  git branch -D contractor-ios-performance-2025-09
  ```

### Cleanup Repository
- [ ] Remove contractor files:
  ```bash
  rm CONTRACTOR_README.md
  rm PERFORMANCE_BASELINE.md
  rm src/ios_app/Backend/CONTRACTOR_MODE
  ```
- [ ] Restore original Config.swift:
  ```bash
  git checkout revert-to-a42786 -- src/ios_app/V10/App/Config.swift
  ```
- [ ] Commit cleanup:
  ```bash
  git add .
  git commit -m "Cleanup after contractor project"
  git push origin revert-to-a42786
  ```

### Upwork Completion
- [ ] Release final payment
- [ ] Write honest review mentioning:
  - [ ] Communication quality
  - [ ] Technical skills
  - [ ] Delivery timeline
  - [ ] Results achieved
- [ ] Close contract
- [ ] Save contractor info if good (for future projects)

### Documentation
- [ ] Create summary of improvements:
  ```markdown
  # Performance Improvements Summary
  - Tab switching: XXXms → XXXms (XX% improvement)
  - Scrolling: XX FPS → XX FPS (XX% improvement)
  - Memory usage: Reduced by XX%
  - Techniques used: [list]
  ```

## 🆘 Emergency Procedures

### If Suspicious Activity Detected
1. [ ] Run immediate audit:
   ```bash
   git log --author="[contractor-email]" --name-only --since="1 day ago"
   ```
2. [ ] If confirmed suspicious:
   - [ ] Revoke GitHub access NOW
   - [ ] Do not approve any pending milestones
   - [ ] Document everything for Upwork dispute

### If Performance Gets Worse
1. [ ] Don't merge their changes
2. [ ] Ask for explanation
3. [ ] Consider partial payment for effort
4. [ ] Find replacement contractor if needed

### If Contractor Goes Silent
1. [ ] Message via Upwork (creates record)
2. [ ] Wait 24 hours
3. [ ] Send "checking in" message
4. [ ] After 48 hours, consider ending contract

## 📋 Quick Commands Reference

```bash
# Daily monitoring
python daily-notes/2025-09-17/monitor_contractor_activity.py

# Check their changes
git fetch origin
git diff revert-to-a42786..origin/contractor-ios-performance-2025-09

# Test their code
git checkout contractor-ios-performance-2025-09
git pull
cd src/ios_app && open V10.xcodeproj

# Merge approved work
git checkout revert-to-a42786
git merge contractor-ios-performance-2025-09 --squash

# Emergency revoke (on GitHub)
Settings → Manage access → Remove collaborator

# Cleanup after project
git push origin --delete contractor-ios-performance-2025-09
```

## ✅ Success Metrics

Project is successful if:
- [ ] Tab switching < 200ms achieved
- [ ] Scrolling maintains 55+ FPS
- [ ] Button response < 100ms
- [ ] No security breaches
- [ ] Code is clean and documented
- [ ] Contractor communicated well
- [ ] Delivered on time (14 days)

---

Remember: The contractor ONLY needs iOS code access. Keep everything else private!
