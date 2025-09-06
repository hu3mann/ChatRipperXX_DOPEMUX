#!/usr/bin/env python3
import sys
import json
import re
import os
DISABLE_NETWORK = os.getenv("HOOKS_DISABLE_NETWORK", "1") == "1"
BLOCK_SUDO = os.getenv("HOOKS_BLOCK_SUDO", "1") == "1"
BLOCK_RM = os.getenv("HOOKS_BLOCK_RM", "1") == "1"
SENSITIVE_PATH_PATTERNS = [r"/?\.env($|[\\./])", r"/secrets/", r"/?\.aws/"]
ALLOWLIST_CMDS = set(filter(None, os.getenv("HOOKS_ALLOWLIST_CMDS", "").split(",")))
def out(decision, reason): print(json.dumps({"decision": decision, "permissionDecisionReason": reason}), flush=True)
def is_sensitive(path: str) -> bool:
    low = (path or "").lower()
    for pat in SENSITIVE_PATH_PATTERNS:
        if re.search(pat, low): return True
    return False
def main():
    try: data = json.loads(sys.stdin.read() or "{}")
    except Exception: data = {}
    if (data.get("event") or data.get("eventName")) != "PreToolUse": return
    tool = (data.get("tool") or data.get("toolName") or "").lower()
    ti = data.get("toolInput") or data.get("input") or {}
    if tool in {"bash","terminal","shell","execute","run","sh"}:
        cmd = (ti.get("command") or ti.get("cmd") or "").strip()
        low = cmd.lower()
        if cmd in ALLOWLIST_CMDS: out("allow", f"Allowed: {cmd}"); return
        if BLOCK_SUDO and re.search(r"(^|\s)sudo(\s|$)", low): out("deny","'sudo' not permitted."); return
        if BLOCK_RM and re.search(r"(^|\s)rm(\s|-)", low): out("ask","'rm' detected. Confirm destructive action."); return
        if DISABLE_NETWORK and any(w in low for w in ["curl ","wget ","pip install","npm install"]):
            out("ask","Network installs disabled by default. Confirm or use a lockfile."); return
    if tool in {"read","readfile","read_file"}:
        p = (ti.get("file_path") or ti.get("path") or "").strip()
        if p and is_sensitive(p): out("deny", f"Reading sensitive file '{p}' not permitted."); return
    if tool in {"write","writefile","write_file"}:
        p = (ti.get("file_path") or ti.get("path") or "").strip()
        content = (ti.get("content") or "")
        if p.endswith(("package.json","pyproject.toml","requirements.txt","poetry.lock")):
            out("ask","Dependency manifest change detected. Confirm rationale."); return
        if len(content) > 200_000: out("ask","Large write (>200KB). Confirm intent."); return
if __name__ == "__main__": main()
