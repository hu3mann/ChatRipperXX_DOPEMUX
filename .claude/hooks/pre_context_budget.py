#!/usr/bin/env python3
import sys
import json
import os
CONPORT_STRICT = os.getenv("HOOKS_CONPORT_STRICT", "1") == "1"
EXA_MIN_QUERY_LEN = int(os.getenv("HOOKS_EXA_MIN_QUERY_LEN", "3"))
CLAUDE_CONTEXT_MAX_RESULTS = int(os.getenv("HOOKS_CLAUDE_CONTEXT_MAX_RESULTS", "3"))
TASKMASTER_DEFAULT_LIMIT = int(os.getenv("HOOKS_TASKMASTER_LIMIT", "3"))
ZEN_MAX_FILES = int(os.getenv("HOOKS_ZEN_MAX_FILES", "1"))
GENERIC_TERMS = {"help","docs","documentation","fix","error","issue","bug","search"}
def out(decision, reason): print(json.dumps({"decision": decision, "permissionDecisionReason": reason}), flush=True)
def main():
    try: data = json.loads(sys.stdin.read() or "{}")
    except Exception: data = {}
    if (data.get("event") or data.get("eventName")) != "PreToolUse": return
    tool = (data.get("tool") or data.get("toolName") or "").lower()
    ti = data.get("toolInput") or data.get("input") or {}
    if "conport" in tool and CONPORT_STRICT:
        if "get_active_context" in tool: out("ask","Use ConPort summaries or search with small limits before full context."); return
        if not any(k in ti for k in ("limit","limit_per_type","top_k")) and any(x in tool for x in ("search_","get_decisions","get_progress","get_custom_data")):
            out("ask","Provide a small 'limit' (3–5) for ConPort reads."); return
    if "exa" in tool:
        q = (ti.get("query") or (ti.get("q") or "")).strip()
        if len(q) < EXA_MIN_QUERY_LEN or q.lower() in GENERIC_TERMS:
            out("ask","Exa query too broad. Refine (lib, function, error text)."); return
    if "claude-context" in tool or "claude_context" in tool:
        max_results = int(ti.get("max_results") or ti.get("limit") or 10)
        if max_results > CLAUDE_CONTEXT_MAX_RESULTS:
            out("ask", f"Reduce Claude-Context results to ≤ {CLAUDE_CONTEXT_MAX_RESULTS}."); return
    if "task-master-ai" in tool:
        if "get_tasks" in tool:
            # Block unlimited task dumps - require filtering
            if not ti.get("status") and ti.get("withSubtasks") != False:
                out("ask","Use status filter (pending/done) or withSubtasks=false for TaskMaster."); return
            # For unfiltered queries, enforce reasonable limits
            if not any(k in ti for k in ("status", "withSubtasks")) and not ti.get("limit"):
                out("ask",f"Add status filter or limit≤{TASKMASTER_DEFAULT_LIMIT} for TaskMaster queries."); return
    if "zen" in tool:
        files = ti.get("files", [])
        if len(files) > ZEN_MAX_FILES:
            out("ask",f"Limit Zen context files to ≤{ZEN_MAX_FILES} for token efficiency."); return
        # Encourage continuation_id reuse for long conversations
        if not ti.get("continuation_id") and len(ti.get("prompt", "")) > 200:
            out("ask","Use continuation_id for long Zen conversations to reduce context."); return
if __name__ == "__main__": main()
