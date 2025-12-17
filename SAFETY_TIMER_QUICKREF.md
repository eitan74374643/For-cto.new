# ⏰ Safety Timer Quick Reference

## Command Line Usage

```bash
# Default (4 hours) - Good for Colab Free
python 0_master_controller.py

# 8 hours - Perfect for Kaggle
python 0_master_controller.py 8

# 12 hours - Colab Pro
python 0_master_controller.py 12

# 2 hours - Testing
python 0_master_controller.py 2

# 30 minutes - Quick test
python 0_master_controller.py 0.5
```

## Platform Recommendations

| Platform | GPU Session | Recommended Timer | Command |
|----------|-------------|-------------------|---------|
| **Kaggle** | 9-12 hours | 8 hours | `python 0_master_controller.py 8` |
| **Colab Free** | 12 hours max | 4 hours | `python 0_master_controller.py 4` |
| **Colab Pro** | 24 hours | 12 hours | `python 0_master_controller.py 12` |
| **Local PC** | Unlimited | No limit needed | `python 0_master_controller.py` |
| **Testing** | Any | 0.5 hours | `python 0_master_controller.py 0.5` |

## What Happens at Time Limit

1. ✅ **Completes current task** (no interruption mid-operation)
2. ✅ **Saves all checkpoints** to persistent storage
3. ✅ **Saves progress file** with timestamp
4. ✅ **Clears GPU memory**
5. ✅ **Exits cleanly** (exit code 0)

## Where Checkpoints Are Saved

- **Kaggle**: `/kaggle/working/` (persists with "Save Version")
- **Colab**: Google Drive `/content/drive/MyDrive/AI_Project_Master/`
- **Local**: Current working directory

## Resume Behavior

Just run the same command again:

```bash
# First run (8 hours)
python 0_master_controller.py 8
# ... saves and exits at time limit

# Second run (8 hours)
python 0_master_controller.py 8
# ... automatically detects and resumes from checkpoints
```

## Log Messages to Watch For

### Start
```
⏱️ Started at: 2024-12-15 10:00:00
⏰ Will auto-save and exit at: 2024-12-15 18:00:00
```

### Progress
```
⏱️ Elapsed time: 2.35 hours / 8 hours
```

### Warning (30 min remaining)
```
⚠️ Time warning: 29.5 minutes remaining
```

### Time Limit Reached
```
⏰ Time limit reached after Training Three Adapters
💾 FORCE SAVING ALL CHECKPOINTS AND PROGRESS
✅ All checkpoints saved successfully!
⏰ PIPELINE PAUSED DUE TO TIME LIMIT
💾 Safe shutdown complete. All progress saved.
```

## Safety Features

✅ **Try/Finally Block**: Guarantees saves even on crashes  
✅ **Time Checking**: Before and after each step  
✅ **Graceful Exit**: Completes current task before stopping  
✅ **Multi-Platform**: Works on Kaggle, Colab, Local  
✅ **Auto-Resume**: Detects checkpoints automatically  

## Common Patterns

### Kaggle Workflow
```bash
# Session 1 (8 hours)
!python 0_master_controller.py 8
# Saves to /kaggle/working/, exit cleanly

# Save Version in Kaggle (preserves /kaggle/working/)

# Session 2 (8 hours)
!python 0_master_controller.py 8
# Resumes automatically from last checkpoint

# Repeat until complete
```

### Testing Locally
```bash
# Test with 5-minute timeout
python 0_master_controller.py 0.083

# Verify checkpoints saved
ls -la checkpoints/

# Test resume
python 0_master_controller.py 0.083
```

## Troubleshooting

**Q: Why did it exit before the time limit?**  
A: It may have completed all steps early! Check logs for "PIPELINE COMPLETED SUCCESSFULLY"

**Q: Checkpoints not saving to Kaggle?**  
A: Verify `/kaggle/working/` exists: `!ls -la /kaggle/working/`

**Q: How to skip timer for local testing?**  
A: Set a very high value: `python 0_master_controller.py 999`

**Q: Can I change the timer mid-run?**  
A: No, but you can Ctrl+C (saves checkpoints) and restart with new timer

## File Locations

### Progress Tracker
- Kaggle: `/kaggle/working/training_progress.txt`
- Colab: `/content/drive/MyDrive/AI_Project_Master/last_checkpoint.txt`
- Local: `./last_checkpoint.txt`

### Checkpoints
- Kaggle: `/kaggle/working/checkpoints/`
- Colab: `/content/drive/MyDrive/AI_Project_Master/checkpoints/`
- Local: `./checkpoints/`

## Technical Notes

- Timer uses `time.time()` for precise tracking
- Checks before and after each subprocess
- 30-minute warning helps plan ahead
- Try/finally ensures saves even on errors
- Compatible with Ctrl+C interruption

---

**For detailed documentation, see `SAFETY_TIMER_GUIDE.md`**
