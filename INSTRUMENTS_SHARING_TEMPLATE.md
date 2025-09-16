# Instruments Performance Report Template

Copy this template and fill in your data:

## Overview
- **Total Recording Time:** [X seconds]
- **Peak CPU Usage:** [X%]
- **Peak Memory:** [X MB]
- **Main Thread Block:** [X ms]

## Heaviest Stack Trace
```
[Right-click the heavy stack → Copy Stack Trace → Paste here]
Example:
3.65 s  V10 (3024)
├─ 2.48 s  Main Thread
│  ├─ 2.14 s  CFRunLoopRun
│  │  ├─ 1.57 s  UIUpdateSequence
```

## Problem Areas
1. **Function Name:** [dispatch_worker_thread2]
   - **Time:** [124ms / 3.4%]
   - **Issue:** [Blocking main thread]

2. **Function Name:** [CFRunLoopDoSource]
   - **Time:** [X ms / X%]
   - **Issue:** [Description]

## Timeline Events
- **0:00-0:30** - App launch, blank screen
- **0:30-0:45** - First content appears
- **0:45-1:00** - User interaction possible

## Specific Questions
- Why is [function] taking [X ms]?
- What does [hex address] represent?
- How to fix [specific issue]?

