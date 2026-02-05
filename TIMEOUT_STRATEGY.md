# Agent Relay Timeout Strategy

## Understanding the Problem

The "timeouts" we saw were **NOT** the system being slow. They were:

1. **Agents completing work but staying alive** (idle in PTY)
2. **Schema mismatches** causing immediate exceptions
3. **Database path typos** causing immediate failures

The actual agent tasks (creating Python files) completed in **seconds**, not minutes.

---

## Strategies to Prevent/Handle Timeouts

### 1. Set Agent Idle Timeout

When spawning, set a short idle timeout so agents auto-exit:

```bash
# Add to agent-relay spawn command
agent-relay spawn Extractor \
  "claude --dangerously-skip-permissions" \
  "Create extractor.py" \
  --idle-timeout 60  # Auto-exit after 60s idle
```

### 2. Use timeout Wrapper for Exec Commands

```bash
# Wrap long commands
TIMEOUT=30  # seconds

# Pattern for critical operations
timeout $TIMEOUT bash -c '
  cd workspace
  agent-relay status
  agent-relay spawn Name "claude ..." "task"
'

# Check exit code
if [ $? -eq 124 ]; then
  echo "Command timed out after ${TIMEOUT}s"
fi
```

### 3. Async Pattern with Polling

Instead of waiting for agent:
```bash
# 1. Spawn agent (non-blocking)
agent-relay spawn Worker "claude ..." "Create file X" &
PID=$!

# 2. Poll for file creation
for i in {1..30}; do
  if [ -f "X" ]; then
    echo "✓ Agent completed"
    break
  fi
  sleep 1
done

# 3. Kill if still running
kill $PID 2>/dev/null
```

### 4. Python Implementation with Timeout

```python
import subprocess
import signal

def run_with_timeout(cmd, timeout_sec=30):
    """Run command with timeout handling."""
    proc = subprocess.Popen(
        cmd, 
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=timeout_sec)
        return proc.returncode, stdout.decode(), stderr.decode()
    except subprocess.TimeoutExpired:
        proc.kill()
        return -1, "", "TIMEOUT"

# Usage
rc, out, err = run_with_timeout(
    "agent-relay spawn Extractor ...",
    timeout_sec=60
)
```

### 5. Graceful Degradation

**Current approach that works:**
```python
# Don't wait for agent - just check if work was done
def spawn_and_verify(agent_name, expected_file, timeout=30):
    # Spawn agent
    subprocess.Popen(["agent-relay", "spawn", agent_name, ...])
    
    # Poll for result
    for _ in range(timeout):
        if os.path.exists(expected_file):
            return True
        time.sleep(1)
    
    return False
```

---

## Recommended Timeout Values

| Operation | Timeout | Reason |
|-----------|---------|--------|
| Simple file creation | 30s | Fast task |
| Complex code generation | 60s | May need API retries |
| Database operations | 10s | Local SQLite |
| Full integration test | 30s | Multiple operations |
| Daemon check | 5s | Just status |

---

## What We Should Have Done Differently

### ❌ What We Did
```bash
# Spawned 4 agents at once
agent-relay spawn A ... &
agent-relay spawn B ... &
agent-relay spawn C ... &
agent-relay spawn D ... &
wait  # Risk of timeout
```

### ✅ What We Should Do
```bash
# Sequential with verification
timeout 60 agent-relay spawn A ...
[ -f output_a.py ] || echo "A failed"

timeout 60 agent-relay spawn B ...
[ -f output_b.py ] || echo "B failed"

# Or use shorter idle timeout in agent config
```

---

## Current State

**The timeouts are not preventing ContextKeeper from working.**

All agents completed their tasks successfully:
- ✅ Extractor created extractor.py
- ✅ Storage created storage.py  
- ✅ Query created query.py
- ✅ Summary created summary.py

The "timeout" messages were from:
1. My exec calls not returning (agents idle but alive)
2. Schema issues causing fast failure (not timeout)

---

## Action Items

### Immediate (now)
- [ ] Add `--idle-timeout 300` to future agent spawns
- [ ] Verify files exist before assuming failure
- [ ] Kill zombie agents: `pkill -f "relay-pty --name"`

### Future projects
- [ ] Implement async spawn + poll pattern
- [ ] Set timeout=60 for all agent spawn operations
- [ ] Log completion times to optimize

### Monitoring
- [ ] Track agent completion times
- [ ] Alert if agent takes >60s for simple task
- [ ] Auto-kill agents idle >5 minutes
