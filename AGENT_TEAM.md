# Core Agent Team for Agent-Relay Projects

## Installed Agents

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **lead-agent** | Coordinator, delegates, tracks progress | Multi-agent projects |
| **architect-agent** | System design, tech planning, patterns | Design phase |
| **backend-agent** | APIs, services, server logic | Building backends |
| **database-agent** | Schema, migrations, optimization | Data layer work |
| **tester-agent** | Unit, integration, e2e tests | Quality assurance |
| **debugger-agent** | Bug hunting, root cause analysis | When things break |

## Installation Commands

```bash
# Core team
cd ~/.openclaw/workspace/contextkeeper
npx prpm install @agent-relay/lead-agent
npx prpm install @agent-relay/architect-agent
npx prpm install @agent-relay/backend-agent
npx prpm install @agent-relay/database-agent
npx prpm install @agent-relay/tester-agent
npx prpm install @agent-relay/debugger-agent

# Core skills
npx prpm install @agent-relay/using-agent-relay
npx prpm install @agent-relay/agent-relay-snippet
```

## Usage Pattern

```bash
# Design phase
agent-relay spawn Architect "claude --agent architect-agent" "Design ContextKeeper schema"

# Implementation
agent-relay spawn Backend "claude --agent backend-agent" "Implement storage.py"
agent-relay spawn Database "claude --agent database-agent" "Create migrations"

# Testing
agent-relay spawn Tester "claude --agent tester-agent" "Write integration tests"

# Coordination
agent-relay spawn Lead "claude --agent lead-agent" "Review all components"
```

## Available on PRPM (710 total)

Search for more:
```bash
npx prpm search "agent relay" --limit 50
npx prpm search "claude agent" --limit 20
```

## Key Insight

Agents are specialized roles. Instead of generic "Worker1", use:
- architect-agent for design decisions
- tester-agent for quality checks
- lead-agent for coordination

This gives each agent context about its role.
