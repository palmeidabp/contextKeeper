# PRPM Agent Team - Installed

## Core Team (6 Agents)

| Agent | Version | Description |
|-------|---------|-------------|
| lead-agent | 1.0.0 | Coordinator, delegates, tracks progress |
| architect-agent | 1.0.0 | System design, tech planning, patterns |
| backend-agent | 1.0.0 | APIs, services, server-side logic |
| database-agent | 1.0.0 | Schema, migrations, optimization |
| tester-agent | 1.0.0 | Unit, integration, e2e tests |
| debugger-agent | 1.0.0 | Bug hunting, root cause analysis |

## Installed From PRPM

```bash
npx prpm install @agent-relay/lead-agent
npx prpm install @agent-relay/architect-agent
npx prpm install @agent-relay/backend-agent
npx prpm install @agent-relay/database-agent
npx prpm install @agent-relay/tester-agent
npx prpm install @agent-relay/debugger-agent
```

## Usage

```bash
# Design phase
agent-relay spawn Architect "claude --agent architect-agent" "Design system"

# Implementation
agent-relay spawn Backend "claude --agent backend-agent" "Build API"
agent-relay spawn Database "claude --agent database-agent" "Create schema"

# Testing
agent-relay spawn Tester "claude --agent tester-agent" "Write tests"

# Coordination
agent-relay spawn Lead "claude --agent lead-agent" "Review work"
```

## Location

All agents installed to:
```
.openagents/
├── lead-agent/AGENT.md
├── architect-agent/AGENT.md
├── backend-agent/AGENT.md
├── database-agent/AGENT.md
├── tester-agent/AGENT.md
└── debugger-agent/AGENT.md
```
