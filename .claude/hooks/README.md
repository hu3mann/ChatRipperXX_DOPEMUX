# Project Hooks (cross-platform)
Place this folder at your **repo root** as `hooks/`.

## Configure Claude Code (`.claude/settings.json`)
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Read|Write|mcp__conport__.*|mcp__claude-context__.*|mcp__claude_context__.*|mcp__exa__.*|mcp__task-master-ai__.*|mcp__zen__.*|mcp__devdocs__.*",
        "hooks": [
          { "type": "command", "command": "python3 hooks/pre_tool_guard.py" },
          { "type": "command", "command": "python3 hooks/pre_context_budget.py" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write|mcp__serena__.*",
        "hooks": [
          { "type": "command", "command": "bash hooks/post_quality_gate.sh" }
        ]
      }
    ]
  }
}
```
**Windows:** replace the PostToolUse command with PowerShell:
```json
{ "type": "command", "command": "powershell -ExecutionPolicy Bypass -File hooks/post_quality_gate.ps1" }
```

## Quick self-test
```bash
echo '{"event":"PreToolUse","tool":"Bash","toolInput":{"command":"sudo rm -rf /"}}' | python3 hooks/pre_tool_guard.py
echo '{"event":"PreToolUse","tool":"mcp__exa__web_search","toolInput":{"query":"help"}}' | python3 hooks/pre_context_budget.py
```

## Environment variables

### Security & Quality Gates
- `HOOKS_DISABLE_NETWORK=1` (default), `HOOKS_BLOCK_SUDO=1`, `HOOKS_BLOCK_RM=1`
- `HOOKS_COV_MIN=60` (raise to 90 if desired), `HOOKS_TEST_ARGS=-q`

### Token Optimization (Recommended Settings)
- `HOOKS_CONPORT_STRICT=1`, `HOOKS_EXA_MIN_QUERY_LEN=5`, `HOOKS_CLAUDE_CONTEXT_MAX_RESULTS=3`
- `HOOKS_TASKMASTER_LIMIT=5`, `HOOKS_ZEN_MAX_FILES=2`

### Legacy/Loose Settings (Higher Token Usage)
- `HOOKS_EXA_MIN_QUERY_LEN=3`, `HOOKS_CLAUDE_CONTEXT_MAX_RESULTS=5`
