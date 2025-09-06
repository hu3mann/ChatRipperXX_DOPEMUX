#!/usr/bin/env python3
"""
MCP Controller: list/start/stop/check servers defined in:
  - Project: .claude/mcp.config.json
  - User:    ~/.claude.json (merged, overrides project on conflicts)

Usage:
  python scripts/mcp/mcpctl.py list
  python scripts/mcp/mcpctl.py start-all
  python scripts/mcp/mcpctl.py start <server> [...]
  python scripts/mcp/mcpctl.py stop <server> [...]
  python scripts/mcp/mcpctl.py stop-all
  python scripts/mcp/mcpctl.py check

Notes:
  - Starts commands as child processes and records PIDs under ./.mcp-pids/<name>.pid
  - Env merges: current environment + server.env from config
  - "disabled": true servers are skipped by start-all
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Tuple


ROOT = Path(__file__).resolve().parents[2]
PROJECT_CFG = ROOT / ".claude" / "mcp.config.json"
USER_CFG = Path(os.path.expanduser("~/.claude.json"))
PID_DIR = ROOT / ".mcp-pids"


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def merge_servers(project: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    p = project.get("mcpServers", {})
    u = user.get("mcpServers", {})
    merged = {**p, **u}
    return merged


def read_configs() -> Dict[str, Any]:
    proj = load_json(PROJECT_CFG)
    user = load_json(USER_CFG)
    return merge_servers(proj, user)


def ensure_pid_dir():
    PID_DIR.mkdir(parents=True, exist_ok=True)


def pidfile(name: str) -> Path:
    return PID_DIR / f"{name}.pid"


def write_pid(name: str, pid: int, cmd: str):
    ensure_pid_dir()
    pf = pidfile(name)
    pf.write_text(str(pid), encoding="utf-8")
    (PID_DIR / f"{name}.cmd").write_text(cmd, encoding="utf-8")


def read_pid(name: str) -> Tuple[int, Path]:
    pf = pidfile(name)
    if not pf.exists():
        raise FileNotFoundError(f"No PID file for {name} at {pf}")
    pid = int(pf.read_text(encoding="utf-8").strip())
    return pid, pf


def is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def start_server(name: str, spec: Dict[str, Any]) -> int:
    cmd = spec.get("command")
    args = spec.get("args", [])
    env_cfg = spec.get("env", {})
    disabled = spec.get("disabled", False)
    if disabled:
        print(f"[skip] {name}: disabled")
        return 0
    if not cmd:
        print(f"[error] {name}: missing 'command'")
        return 1
    env = os.environ.copy()
    env.update({k: str(v) for k, v in env_cfg.items()})
    full = [cmd] + list(args)
    try:
        proc = subprocess.Popen(full, env=env)
    except FileNotFoundError as e:
        print(f"[error] {name}: {e}")
        return 1
    write_pid(name, proc.pid, " ".join(full))
    print(f"[ok] {name}: started pid={proc.pid}")
    return 0


def stop_server(name: str) -> int:
    try:
        pid, pf = read_pid(name)
    except FileNotFoundError:
        print(f"[skip] {name}: no pid file")
        return 0
    if is_alive(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"[ok] {name}: sent SIGTERM to pid={pid}")
        except OSError as e:
            print(f"[warn] {name}: {e}")
    else:
        print(f"[info] {name}: pid {pid} not running")
    try:
        pf.unlink(missing_ok=True)
        (PID_DIR / f"{name}.cmd").unlink(missing_ok=True)
    except Exception:
        pass
    return 0


def check_server(name: str) -> int:
    try:
        pid, _ = read_pid(name)
        alive = is_alive(pid)
        print(f"{name}: {'alive' if alive else 'dead'} (pid={pid})")
        return 0 if alive else 1
    except FileNotFoundError:
        print(f"{name}: unknown (no pid)")
        return 2


def main(argv: list[str]) -> int:
    servers = read_configs()
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")
    sub.add_parser("start-all")
    sp = sub.add_parser("start")
    sp.add_argument("names", nargs="+")
    sub.add_parser("stop-all")
    sp2 = sub.add_parser("stop")
    sp2.add_argument("names", nargs="+")
    sub.add_parser("check")

    args = ap.parse_args(argv)

    if args.cmd == "list":
        if not servers:
            print("No MCP servers found. Check .claude/mcp.config.json and ~/.claude.json")
            return 0
        print("Name\t\tDisabled\tCommand")
        for name, spec in servers.items():
            print(f"{name}\t\t{bool(spec.get('disabled', False))}\t{spec.get('command')} {' '.join(spec.get('args', []))}")
        return 0

    if args.cmd == "start-all":
        rc = 0
        for name, spec in servers.items():
            rc |= start_server(name, spec)
        return rc

    if args.cmd == "start":
        rc = 0
        for name in args.names:
            spec = servers.get(name)
            if not spec:
                print(f"[error] Unknown server: {name}")
                rc |= 1
            else:
                rc |= start_server(name, spec)
        return rc

    if args.cmd == "stop-all":
        rc = 0
        for name in servers.keys():
            rc |= stop_server(name)
        return rc

    if args.cmd == "stop":
        rc = 0
        for name in args.names:
            rc |= stop_server(name)
        return rc

    if args.cmd == "check":
        rc = 0
        for name in servers.keys():
            rc |= check_server(name)
        return rc

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

