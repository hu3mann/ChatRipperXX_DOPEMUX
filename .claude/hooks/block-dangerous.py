#!/usr/bin/env python3
import sys, json, re

def block(msg):
    print(msg, file=sys.stderr); sys.exit(2)

try:
    payload = json.load(sys.stdin)
except Exception as e:
    print(f"[hooks] parse error: {e}", file=sys.stderr); sys.exit(0)

event = payload.get("hook_event_name") or ""
tool = payload.get("tool_name") or ""
tool_input = payload.get("tool_input") or {}

if event == "PreToolUse" and tool == "Bash":
    cmd = (tool_input.get("command") or "").strip().lower()
    if re.search(r"(^|\s)sudo(\s|$)", cmd): block("Blocked: 'sudo' is not permitted.")
    if re.search(r"(^|\s)rm(\s|-)", cmd):    block("Blocked: 'rm' is not permitted.")
    if "curl " in cmd or "wget " in cmd:       block("Blocked: network fetch disabled by default.")

if event == "PreToolUse" and tool == "Read":
    path = (tool_input.get("file_path") or "").lower()
    if path.endswith("/.env") or "/secrets/" in path or "/.env." in path or path.endswith("\\.env"):
        block(f"Blocked: reading sensitive file '{path}' is not permitted.")

sys.exit(0)
