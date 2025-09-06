# Smart Hooks Phase 1 - Implementation Guide

**Status**: ✅ Complete | **Version**: 1.0 | **Date**: 2025-09-06

## Overview

Smart Hooks Phase 1 implements enhanced token budget management and adaptive security features that learn from user patterns and project context to provide increasingly intelligent guardrails for Claude Code sessions.

## Phase 1.1: Enhanced Token Budget Management

### Features

- **Pattern Tracking System**: Records all MCP tool usage with estimated token consumption
- **Smart Optimization Engine**: Provides real-time suggestions for high-token operations  
- **Usage Dashboard**: Real-time monitoring via `python .claude/hooks/dashboard.py`
- **Automatic Learning**: Builds optimization suggestions from command sequences over time

### Token Estimates by Tool

| Tool | Token Usage | Optimization Strategy |
|------|-------------|----------------------|
| Zen | ~29k tokens | MANDATORY `files≤1` + `continuation_id` reuse |
| TaskMaster | ~21k tokens | DEFAULT `status=pending withSubtasks=false` |
| ConPort | ~17k tokens | ALWAYS use `limit=3-5` on searches |
| Serena | ~15k tokens | Prefer symbolic tools over full file reads |
| Claude-Context | ~5k tokens | Cap results ≤3 |
| Exa | ~3k tokens | Refine over-broad queries |

### Usage

```bash
# Enable pattern tracking
export HOOKS_ENABLE_SMART_OPTIMIZATION=1

# View current session usage
python .claude/hooks/dashboard.py --current

# View usage patterns
python .claude/hooks/dashboard.py --patterns

# Get optimization suggestions
python .claude/hooks/dashboard.py --suggestions
```

## Phase 1.2: Adaptive Security Model

### Features

- **Context-Aware Evaluation**: Analyzes project type (Python/Node.js/Docker/Rust) and git status
- **Legitimate Pattern Recognition**: Automatically allows common development patterns
- **Dynamic Risk Scoring**: Calculates risk based on command patterns and project context
- **Security Audit Trail**: Complete decision history with timestamps and reasoning
- **Learning Dashboard**: Security analytics via `python .claude/hooks/security_dashboard.py`

### Risk Assessment

#### High Risk (Deny/Ask) - Score > 0.7
- `sudo` commands
- `rm -rf` operations  
- Curl/wget piped to shell
- Disk operations (`dd`, `mkfs`, `fdisk`)

#### Medium Risk (Ask) - Score 0.3-0.7
- Network package installs without lockfiles
- Executable permission changes (`chmod 777`)
- Copy operations to system paths

#### Low Risk (Allow) - Score < 0.3
- Git operations (`git status`, `git add`, `git commit`)
- Development tools (`python -m pytest`, `npm test`)
- Read operations (`ls`, `cat`, `head`, `tail`)

### Context Adjustments

- **Docker Projects**: Lower risk for Docker commands
- **Python/Node.js Projects**: Lower risk for package installs with manifest files present
- **Git Repositories**: Higher risk for destructive operations with uncommitted changes

### Usage

```bash
# Enable adaptive security
export HOOKS_ENABLE_ADAPTIVE_SECURITY=1

# View security summary
python .claude/hooks/security_dashboard.py --summary

# Analyze risk patterns
python .claude/hooks/security_dashboard.py --risk

# Check learning status  
python .claude/hooks/security_dashboard.py --learning
```

## Data Storage

### Location
All Smart Hooks data is stored in `.claude/hooks/data/`:

- `usage_patterns.json` - MCP tool usage history with token estimates
- `session_metrics.json` - Current session token budget tracking
- `security_audit.json` - Security decision audit trail

### Data Retention
- Maximum 200 records per file to prevent unbounded growth
- Records include timestamps for temporal analysis
- Graceful degradation if data files are unavailable

## Environment Configuration

### Required Variables

```bash
# Phase 1.1 - Token Budget Management
export HOOKS_ENABLE_SMART_OPTIMIZATION=1

# Phase 1.2 - Adaptive Security
export HOOKS_ENABLE_ADAPTIVE_SECURITY=1
```

### Optional Tuning

```bash
# Token budget limits
export HOOKS_CLAUDE_CONTEXT_MAX_RESULTS=3      # Default: 3
export HOOKS_TASKMASTER_LIMIT=3                # Default: 3  
export HOOKS_ZEN_MAX_FILES=1                   # Default: 1

# Security thresholds
export HOOKS_DISABLE_NETWORK=1                 # Default: 1
export HOOKS_BLOCK_SUDO=1                      # Default: 1
export HOOKS_BLOCK_RM=1                        # Default: 1
```

## Integration Points

### Pre-Tool Hooks
- `pre_context_budget.py` - Enhanced with pattern tracking (Phase 1.1)
- `pre_tool_guard.py` - Enhanced with adaptive security (Phase 1.2)

### Dashboard Commands
- `python .claude/hooks/dashboard.py` - Token usage monitoring
- `python .claude/hooks/security_dashboard.py` - Security decision analytics

### Claude Commands
- `.claude/commands/hooks-dashboard.md` - User-friendly access to dashboards

## Architecture Decisions

### Decision: Silent Failure Pattern
**Rationale**: Smart Hooks should never break user workflows. All learning features fail gracefully if data directories are unavailable or permissions are insufficient.

### Decision: Token-First Optimization
**Rationale**: Token budget management provides the highest impact on performance. Zen (~29k) and TaskMaster (~21k) optimizations alone can save 50k+ tokens per session.

### Decision: Context-Aware Security
**Rationale**: Project type detection allows for intelligent security decisions. Docker projects have different risk profiles than Python projects, enabling more nuanced evaluation.

### Decision: Audit Trail Storage  
**Rationale**: Both token usage and security decisions are stored for learning and debugging. This enables progressive improvement of the system over time.

## Testing

### Pattern Tracking Test
```bash
python .claude/hooks/test_pattern_tracking.py
```

### Security Evaluation Test
```bash
# Test legitimate pattern
echo '{"event": "PreToolUse", "tool": "bash", "toolInput": {"command": "git status"}}' | \
HOOKS_ENABLE_ADAPTIVE_SECURITY=1 python .claude/hooks/pre_tool_guard.py

# Test high-risk command  
echo '{"event": "PreToolUse", "tool": "bash", "toolInput": {"command": "sudo rm -rf /"}}' | \
HOOKS_ENABLE_ADAPTIVE_SECURITY=1 python .claude/hooks/pre_tool_guard.py
```

## Future Evolution

Phase 1 establishes the foundation for:
- **Phase 1.3**: Predictive hook system with command completion
- **Track 2**: Progressive command consolidation
- **Track 3**: Intelligent context synthesis

The modular design allows each phase to build upon previous capabilities while maintaining backward compatibility.

---

**Implementation Status**: ✅ Complete and Operational  
**Next Phase**: Ready for Phase 1.3 (Predictive Hook System) or Track 2 (Progressive Command Consolidation)