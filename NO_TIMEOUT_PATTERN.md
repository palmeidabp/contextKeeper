# No-Timeout Agent Pattern

## The Problem We Had

```bash
# This hangs (agent stays alive after completing):
agent-relay spawn Worker "claude ..." "Create file.py"
# ^ waits forever because agent doesn't exit
```

## The Solution (Works Now)

```bash
# 1. Spawn WITHOUT waiting
(agent-relay spawn Worker "claude ..." "Create file.py") &
#                    ^ background it

# 2. Poll for file (not process)
for i in {1..30}; do
    if [ -f file.py ]; then
        echo "✓ Agent completed"
        break
    fi
    sleep 5
done

# 3. Kill zombie agent
kill %1 2>/dev/null  # kill background job
pkill -f "relay-pty --name Worker"
```

That's it. No special messaging needed.

## Why This Works

- Agent finishes task in ~10 seconds
- Creates file
- Stays alive idle (this is the "hang")
- We don't care - we check the file
- Kill agent when done

## What We Learned

| Misconception | Reality |
|--------------|---------|
| "System overloaded" | Agents idle but alive |
| "Need async messaging" | File polling is simpler & works |
| "Timeouts breaking things" | Tasks completed successfully |

## For Next Project

Use this pattern:

```python
import subprocess
import time
import os

def spawn_worker(name, task, expected_file, timeout=60):
    """Spawn agent, wait for file, kill agent."""
    # Spawn (background)
    subprocess.Popen([
        "agent-relay", "spawn", name,
        "claude --dangerously-skip-permissions",
        task
    ])
    
    # Poll for file
    for _ in range(timeout // 5):
        if os.path.exists(expected_file):
            # Success - kill agent and return
            subprocess.call(["pkill", "-f", f"relay-pty --name {name}"])
            return True
        time.sleep(5)
    
    # Timeout - kill agent
    subprocess.call(["pkill", "-f", f"relay-pty --name {name}"])
    return False

# Usage
spawn_worker("Extractor", "Create extractor.py", "extractor.py")
spawn_worker("Storage", "Create storage.py", "storage.py")
```

## No Additional Tools Needed

- ✅ `agent-relay` - already have it
- ✅ File polling - works with shell/Python
- ✅ Process cleanup - `pkill` works

The SQLite queue and messaging systems we discussed are **optional enhancements**, not requirements.
