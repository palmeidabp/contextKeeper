# Agent Relay Capabilities - What We Missed

## The Big Realization

**Agent Relay already provides async messaging!** I proposed building a SQLite task queue, but relay has this built-in.

## How Relay Async Actually Works

### 1. Agents Send Messages via Protocol

When an agent finishes work, it sends:
```bash
cat > $AGENT_RELAY_OUTBOX/msg << 'EOF'
TO: Lead
KIND: message

DONE: Created extractor.py (150 lines, tested)
EOF
->relay-file:msg
```

### 2. Messages Are Persisted

All messages stored in:
```
.agent-relay/messages/YYYY-MM-DD.jsonl
```

Each message has:
- `id` - unique message ID
- `ts` - timestamp
- `from` - sender agent
- `to` - recipient agent 
- `body` - message content
- `status` - read/unread

### 3. Receiving Messages

**Option A: SDK (Programmatic)**
```typescript
const messages = await client.getInbox({ unreadOnly: true });
```

**Option B: Read Message Files Directly**
```bash
# Check for messages sent to me
cat .agent-relay/messages/2026-02-05.jsonl | jq 'select(.message.to == "Lead")'
```

**Option C: Stay Connected**
```typescript
client.onMessage = (from, { body }) => {
  console.log(`${from}: ${body}`);
};
```

### 4. Agent Status Tracking

```bash
# Check which agents are online
agent-relay agents
agent-relay who
```

### 5. Agent Output Logs

```bash
# View what agent produced
agent-relay agents:logs Extractor -n 20
```

## What This Means for Async Pattern

### ❌ What I Proposed (Redundant)
```
SQLite task queue → Spawn agents → Poll queue → Check files
```

### ✅ What Relay Already Provides
```
Spawn agents → They send messages when done → I check inbox
```

**The difference:**
- My proposal: SQLite + file checking
- Relay reality: Message system + file checking

## Why I Missed This

1. **No CLI inbox command** - There's `agent-relay send` but no `agent-relay receive`
2. **SDK vs CLI gap** - SDK has `getInbox()`, CLI doesn't expose it
3. **I disconnected** - After spawning, I didn't stay connected to receive messages

## Correct Async Pattern with Relay

```python
# 1. Spawn all agents (they all listen)
agent-relay spawn Extractor "claude ..." "Create extractor.py"
agent-relay spawn Storage "claude ..." "Create storage.py"

# 2. Go do other work (I'm still connected?)

# 3. Check for completion via:
#    - Message inbox
#    - File existence
#    - Agent status

# 4. When I receive "DONE" messages, proceed to integration
```

## Key Insight

**The "timeout" issues weren't from relay being slow - they were from me not using the messaging system!**

Agents were sending "DONE" messages (probably), but I wasn't listening. Instead, I tried to poll files.

## For Future Projects

### Right Way to Coordinate Agents

```bash
# 1. Spawn workers (non-blocking)
agent-relay spawn Worker-A ... &
agent-relay spawn Worker-B ... &

# 2. Stay connected or use daemon to collect messages

# 3. Workers send completion messages:
#    "DONE: task complete, output in file X"

# 4. I check inbox OR files to verify
```

### Simpler Alternative (What We Actually Did)

```bash
# 1. Spawn worker with explicit output file
agent-relay spawn Agent "claude ..." "Create X.py, then exit"

# 2. Poll for file existence (reliable, simple)
while [ ! -f X.py ]; do sleep 5; done

# 3. Proceed
```

This worked because:
- Agents completed tasks quickly (seconds)
- File existence is definitive proof of completion
- No need for message coordination

## Verdict

| Approach | Complexity | Reliability | Use Case |
|----------|-----------|-------------|----------|
| **Relay messaging** | Low | High | Complex coordination |
| **File polling** | Very Low | High | Simple parallel tasks |
| **SQLite queue** | Medium | High | Over-engineered |

**For ContextKeeper:** File polling was the right choice - simple and worked.

**For future:** Use relay messaging when agents need to:
- Report partial progress
- Request clarification
- Coordinate dependencies

**Don't use SQLite unless you need persistence across sessions.**
