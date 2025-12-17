# ⏰ 4-Hour Safety Timer Guide

## Overview

The master controller now includes a **4-hour safety timer** designed specifically for platforms with session time limits (like Kaggle, which has 9-12 hour session limits).

## How It Works

### Automatic Time Tracking

The system tracks runtime from the moment it starts:

```python
# Started: 2024-12-15 10:00:00
# Will auto-save and exit at: 2024-12-15 14:00:00
```

### Smart Checkpoint Management

1. **Before each step**: Checks if time limit is approaching
2. **After each step**: Checks if time limit has been reached
3. **On time limit**: Completes current micro-task, then saves and exits
4. **On any error**: Saves checkpoints before exiting (try/finally block)

### Guaranteed Safety

Uses a `try/finally` block to **guarantee** checkpoint saves:

```python
try:
    # Run pipeline...
finally:
    # ALWAYS save checkpoints, no matter what
    force_save_checkpoints()
```

## Features

### 1. Environment Detection

Automatically detects and configures for:

- **Kaggle**: Saves to `/kaggle/working/`
- **Google Colab**: Saves to Google Drive
- **Local PC**: Saves to current directory

### 2. Time Warnings

- Displays elapsed time before each step
- Warns when 30 minutes remain
- Logs exact start and projected end times

### 3. Graceful Shutdown

When time limit is reached:

1. ✅ Completes current operation (doesn't interrupt mid-task)
2. ✅ Saves all checkpoints to persistent storage
3. ✅ Saves progress tracker file
4. ✅ Clears GPU memory
5. ✅ Exits cleanly with exit code 0

### 4. Resume Capability

On next run, the system:

1. Detects existing checkpoints
2. Resumes from last completed step
3. Continues training from last epoch/sample

## Usage

### Default (4 Hours)

```bash
python 0_master_controller.py
```

### Custom Time Limit

```bash
# 2 hours
python 0_master_controller.py 2

# 8 hours (for Kaggle T4 GPU sessions)
python 0_master_controller.py 8

# 0.5 hours (30 minutes for testing)
python 0_master_controller.py 0.5
```

### For Kaggle Specifically

```python
# Kaggle notebooks typically allow 9-12 hours
# Recommended: Use 8 hours to leave buffer
!python 0_master_controller.py 8
```

## Kaggle Integration

### First Run

```python
# In Kaggle notebook
!git clone https://github.com/your-repo/ai-trainer.git
%cd ai-trainer
!pip install -r requirements.txt

# Run with 8-hour limit (safe for Kaggle)
!python 0_master_controller.py 8
```

### What Gets Saved to `/kaggle/working/`

```
/kaggle/working/
├── checkpoints/          # Training checkpoints (auto-resume)
├── data/                # Dataset progress
├── models/              # Trained adapters
├── logs/                # Log files
└── training_progress.txt # Progress tracker
```

### Subsequent Runs

When you restart the Kaggle session:

```python
# System automatically detects existing checkpoints
# and resumes from where it left off
!python 0_master_controller.py 8
```

## Architecture

### Time Checking Flow

```
┌─────────────────────────────────────┐
│  Controller Starts                  │
│  - Record start_time                │
│  - Set max_runtime_seconds          │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Before Each Step                   │
│  - Check elapsed time               │
│  - If > limit: set should_exit      │
│  - Skip step if should_exit=True    │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Run Step (subprocess)              │
│  - Execute script                   │
│  - Let it complete current task     │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  After Each Step                    │
│  - Check elapsed time               │
│  - If > limit: set should_exit      │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  Finally Block (ALWAYS)             │
│  - Force save all checkpoints       │
│  - Save progress tracker            │
│  - Clear GPU memory                 │
│  - Exit cleanly                     │
└─────────────────────────────────────┘
```

### Safety Guarantees

```python
try:
    # All pipeline operations
    run_pipeline()
    
finally:
    # This ALWAYS runs, even if:
    # - Time limit reached
    # - Error occurred
    # - User pressed Ctrl+C
    # - Out of memory
    # - Any exception
    force_save_checkpoints()
```

## Log Messages

### Normal Operation

```
⏱️ Started at: 2024-12-15 10:00:00
⏰ Will auto-save and exit at: 2024-12-15 14:00:00

🚀 Starting Dataset Generation...
   ⏱️ Elapsed time: 0.02 hours / 4 hours
   Attempt 1/5
   ✅ Dataset Generation completed successfully!

🚀 Starting Training Three Adapters...
   ⏱️ Elapsed time: 1.35 hours / 4 hours
   ...
```

### Time Warning

```
⚠️ Time warning: 29.5 minutes remaining
```

### Time Limit Reached

```
⏰ Time limit reached after Training Three Adapters
💾 FORCE SAVING ALL CHECKPOINTS AND PROGRESS
================================================================================
📂 Saving to Kaggle: /kaggle/working
   Copying checkpoints...
   ✅ checkpoints saved
   Copying data...
   ✅ data saved
   Copying models...
   ✅ models saved
   ✅ Progress file saved
✅ All checkpoints saved successfully!

⏰ PIPELINE PAUSED DUE TO TIME LIMIT
   Checkpoints saved. Resume by running again.
   
⏱️ Total runtime: 4.00 hours
💾 Safe shutdown complete. All progress saved.
```

## Best Practices

### For Kaggle Users

1. **Use 8-hour limit** for T4 GPU sessions:
   ```bash
   python 0_master_controller.py 8
   ```

2. **Enable Save Version** in Kaggle to persist `/kaggle/working/`

3. **Run multiple sessions**: The system will resume automatically

### For Colab Users

1. **Use 4-hour limit** for free tier:
   ```bash
   python 0_master_controller.py 4
   ```

2. **Colab Pro**: Can use longer (up to 12 hours):
   ```bash
   python 0_master_controller.py 12
   ```

### For Testing

1. **Quick test with 5 minutes**:
   ```bash
   python 0_master_controller.py 0.083
   ```

2. **Verify checkpoint saves work**:
   - Run for 5 minutes
   - Check checkpoint files exist
   - Run again to verify resume

## Troubleshooting

### Issue: "Time limit reached" but session still has time

**Cause**: Safety buffer built into time limit  
**Solution**: This is intentional - ensures clean shutdown before hard timeout

### Issue: Checkpoints not saved to `/kaggle/working/`

**Check**:
```bash
ls -la /kaggle/working/
```

**Solution**: 
- Verify `os.path.exists('/kaggle/working')` returns True
- Check directory permissions

### Issue: Resume doesn't work

**Check**: Look for checkpoint files:
```bash
ls -la /kaggle/working/checkpoints/
```

**Solution**: 
- Ensure previous run completed save
- Check `training_progress.txt` for last checkpoint time

## Technical Details

### Time Tracking

```python
# Initialize
self.start_time = time.time()
self.max_runtime_seconds = max_hours * 3600

# Check
elapsed = time.time() - self.start_time
remaining = self.max_runtime_seconds - elapsed

if remaining <= 0:
    self.should_exit = True
```

### Checkpoint Saving

```python
# For Kaggle
if self.is_kaggle:
    kaggle_path = Path('/kaggle/working')
    
    # Copy all important directories
    for dir_name in ['checkpoints', 'data', 'models', 'logs']:
        src = project_path / dir_name
        dst = kaggle_path / dir_name
        shutil.copytree(src, dst, dirs_exist_ok=True)
```

### Try/Finally Pattern

```python
try:
    # Main pipeline execution
    for step in steps:
        if not self.should_exit:
            run_step(step)
        
finally:
    # GUARANTEED to run
    force_save_checkpoints()
    clear_gpu_memory()
```

## Example Session Flow

### Kaggle Session 1 (8 hours)

```
00:00 - Start
00:30 - Dataset generation (5k samples)
03:00 - Training planner adapter
06:00 - Training coder adapter (partial)
08:00 - TIME LIMIT REACHED
      - Save checkpoints
      - Exit cleanly
```

### Kaggle Session 2 (8 hours)

```
00:00 - Start
00:01 - Detect checkpoints
00:02 - Resume coder adapter training
03:00 - Complete coder adapter
06:00 - Train critic adapter
08:00 - TIME LIMIT REACHED
      - Save checkpoints
      - Exit cleanly
```

### Kaggle Session 3 (8 hours)

```
00:00 - Start
00:01 - Detect checkpoints
00:02 - Resume critic adapter
02:00 - Complete critic adapter
02:30 - Merge models
03:00 - Quantize to GGUF
03:30 - COMPLETE!
```

## Benefits

1. **Zero Data Loss**: Try/finally guarantees saves
2. **Platform Agnostic**: Works on Kaggle, Colab, Local
3. **Resume Friendly**: Automatic checkpoint detection
4. **Configurable**: Adjust time limit per platform
5. **Safe**: Completes current task before exit
6. **Transparent**: Clear logging of time status

## Summary

The 4-hour safety timer ensures your training progress is **never lost**, even on platforms with strict time limits. It provides:

- ✅ Automatic time tracking
- ✅ Graceful shutdown
- ✅ Guaranteed checkpoint saves
- ✅ Resume capability
- ✅ Multi-platform support
- ✅ Configurable time limits

**For Kaggle**: Use `python 0_master_controller.py 8`  
**For Colab Free**: Use `python 0_master_controller.py 4`  
**For Local**: Use default or custom time as needed

---

**Your training is now crash-resistant and time-limit proof! 🎉**
