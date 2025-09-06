#!/usr/bin/env python3
import sys
import json
import os
CONPORT_STRICT = os.getenv("HOOKS_CONPORT_STRICT", "1") == "1"
EXA_MIN_QUERY_LEN = int(os.getenv("HOOKS_EXA_MIN_QUERY_LEN", "3"))
CLAUDE_CONTEXT_MAX_RESULTS = int(os.getenv("HOOKS_CLAUDE_CONTEXT_MAX_RESULTS", "5"))
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
if __name__ == "__main__": main()
