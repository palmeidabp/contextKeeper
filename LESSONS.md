# ContextKeeper - Agent Relay Lessons Learned

## Issues Encountered & Solutions

### 1. Rate Limits (429 errors)
**Problem:** Hit Chutes.ai rate limits when spawning 4 agents in parallel

**Solution:** 
- Spawn agents sequentially, not in parallel
- Add delays between spawns
- Retry logic for 429 errors

```bash
# ❌ Don't do this (parallel)
agent-relay spawn A "claude ..." &
agent-relay spawn B "claude ..." &

# ✅ Do this (sequential)
agent-relay spawn A "claude ..."
sleep 5
agent-relay spawn B "claude ..."
```

---

### 2. Timeouts During Spawning
**Problem:** `agent-relay spawn` commands timeout (appears hung)

**Root Cause:** Not resource limits! Agents spawn Claude Code in PTY sessions that stay open even after task completion.

**Solution:**
- The "timeout" is actually just long-running idle processes
- Agents do complete their work (see logs)
- Use shorter tasks or explicit exit commands

**Evidence:**
```
Load average: 0.47 (not overloaded)
Memory: 9.5GB available
Processes: 4 claude agents idle but alive
```

---

### 3. Daemon Dying Overnight
**Problem:** Relay daemon stopped at ~5:55 AM despite cron checks

**Root Cause:** Unknown - possibly:
- SSH session timeout
- System maintenance
- OOM killer (unlikely, plenty of RAM)

**Solution:**
- Run daemon in tmux (survives SSH disconnect)
- Cron should both check AND restart if needed

```bash
# Current approach (tmux)
tmux new-session -d -s relay 'agent-relay up'
```

---

### 4. Installation Requirements
**Required for headless spawning:**
```bash
export RELAY_PTY_BINARY="$HOME/.agent-relay/bin/relay-pty"
export PATH="$HOME/.local/bin:$PATH"
```

**Required flag:**
```bash
claude --dangerously-skip-permissions
```

---

### 5. Communication Protocol Complexity
**Issue:** Agents need to understand relay protocol to communicate

**What worked:**
- Simple "fire-and-forget" tasks (create file, exit)
- No back-and-forth coordination needed

**What didn't:**
- Complex multi-agent workflows
- Agents waiting for responses from each other

---

## Recommendations for Future Agent-Relay Projects

### DO:
1. ✅ Use sequential agent spawning
2. ✅ Keep tasks simple and independent
3. ✅ Use tmux for daemon persistence
4. ✅ Verify completion via file artifacts, not process status
5. ✅ Set short idle timeouts: `--idle-timeout 300` (5 min)

### DON'T:
1. ❌ Spawn multiple agents in parallel
2. ❌ Expect agents to coordinate complex workflows
3. ❌ Rely on process exit codes (agents hang after completion)
4. ❌ Use `--await` with long tasks (will timeout)
5. ❌ Trust "daemon running" from status check alone

---

## What Actually Worked Well

| Aspect | Result |
|--------|--------|
| **Agent creation** | ✅ 4 agents created 4 working Python modules |
| **Module quality** | ✅ All modules functional with proper interfaces |
| **Integration** | ✅ Main ContextKeeper class works perfectly |
| **Database** | ✅ SQLite schema and operations work |
| **Testing** | ✅ All components pass integration tests |

## Verdict

**Agent-relay is viable for:**
- Parallel task execution (with sequential spawning)
- Code generation by specialized agents
- File-based artifact delivery

**Not ideal for:**
- Real-time coordination between agents
- Long-running interactive sessions
- Complex multi-step workflows requiring communication

## File Artifacts Approach

The most reliable pattern we found:
```
1. Spawn agent with specific task
2. Agent creates file(s) as output
3. Agent sends "DONE" message
4. Main process checks for file existence
5. Main process kills idle agent if needed
```

This is essentially **map-reduce** with files instead of messages.
