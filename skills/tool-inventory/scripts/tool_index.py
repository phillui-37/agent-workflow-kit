#!/usr/bin/env python3
"""Portable, stdlib-only catalog for reusable agent tools."""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

KINDS = {"cli", "script", "mcp", "workflow"}
EFFECTS = {"read-only", "writes", "network", "mixed"}
STATUSES = {"verified", "prototype", "unverified", "deprecated"}
FIELDS = {"id", "summary", "aliases", "category", "kind", "source", "command", "platforms", "dependencies", "effects", "status", "verified_at"}
ALIASES = {"darwin": "macos", "mac": "macos", "osx": "macos", "win": "windows", "win32": "windows", "gnu/linux": "linux"}
VALID_PLATFORMS = {"macos", "windows", "linux"}


def normalize_platform(value):
    value = str(value).strip().lower()
    return ALIASES.get(value, value)


def default_registry():
    return Path(os.environ.get("TOOL_INVENTORY", "~/.agents/tool-inventory.json")).expanduser()


def load_registry(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError("registry not found: %s (set --registry or TOOL_INVENTORY)" % path)
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("tools"), list):
        raise ValueError("registry must have version 1 and a tools array")
    validate_tools(data["tools"])
    return data


def validate_tools(tools):
    seen = set()
    for i, t in enumerate(tools):
        if not isinstance(t, dict):
            raise ValueError("entry %d must be an object" % i)
        missing = FIELDS - t.keys()
        if missing:
            raise ValueError("entry %d missing: %s" % (i, ", ".join(sorted(missing))))
        if not isinstance(t["id"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", t["id"]):
            raise ValueError("id must use lowercase letters, digits, dot, underscore, or hyphen")
        if t["id"] in seen:
            raise ValueError("duplicate id: " + t["id"])
        seen.add(t["id"])
        for key in ("summary", "category", "source", "command"):
            if not isinstance(t[key], str) or not t[key].strip():
                raise ValueError("%s must be a non-empty string" % key)
        if t["kind"] not in KINDS or t["effects"] not in EFFECTS or t["status"] not in STATUSES:
            raise ValueError("invalid kind, effects, or status for " + t["id"])
        for key in ("aliases", "platforms", "dependencies"):
            if not isinstance(t[key], list) or any(not isinstance(x, str) for x in t[key]):
                raise ValueError(key + " must be an array of strings")
        t["platforms"] = [normalize_platform(p) for p in t["platforms"]]
        if any(p not in VALID_PLATFORMS for p in t["platforms"]):
            raise ValueError("platforms must be macos, windows, or linux")
        stamp = t["verified_at"]
        if stamp is not None and (not isinstance(stamp, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", stamp)):
            raise ValueError("verified_at must be YYYY-MM-DD or null")
        if "notes" in t and not isinstance(t["notes"], str):
            raise ValueError("notes must be a string")


def save_registry(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = Path(str(path) + ".bak")
        shutil.copy2(path, backup)
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def display(entry, full=False):
    if full:
        print(json.dumps(entry, indent=2, ensure_ascii=False))
    else:
        print("%s  [%s/%s] %s" % (entry["id"], entry["category"], entry["status"], entry["summary"]))


def check_entry(entry):
    source = entry["source"]
    parsed = urlparse(source)
    windows_path = bool(re.match(r"^[A-Za-z]:[\\/]", source))
    if (parsed.scheme and not windows_path) or entry["kind"] == "mcp":
        resolved = "unresolved (URI/MCP source)"
    else:
        p = Path(source).expanduser()
        resolved = "available" if p.exists() else "unavailable"
    deps = {dep: ("available" if shutil.which(dep) else "unavailable") for dep in entry["dependencies"]}
    label = "unverified" if entry["status"] in ("unverified", "prototype") else entry["status"]
    print("%s: source %s; catalog status %s; dependencies %s" % (entry["id"], resolved, label, json.dumps(deps, sort_keys=True)))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tool-index")
    parser.add_argument("--registry", type=Path, default=default_registry())
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("find"); p.add_argument("query"); p.add_argument("--os", choices=sorted(VALID_PLATFORMS)); p.add_argument("--category"); p.add_argument("--limit", type=int, default=10); p.add_argument("--json", action="store_true")
    p = sub.add_parser("show"); p.add_argument("id"); p.add_argument("--json", action="store_true")
    sub.add_parser("categories")
    p = sub.add_parser("check"); p.add_argument("id", nargs="?")
    p = sub.add_parser("add"); p.add_argument("entry", type=Path); p.add_argument("--replace", action="store_true")
    args = parser.parse_args(argv)
    try:
        args.registry = args.registry.expanduser()
        data = ({"version": 1, "tools": []} if args.action == "add" and not args.registry.exists()
                else load_registry(args.registry))
        tools = data["tools"]
        if args.action == "find":
            if args.limit < 0: raise ValueError("limit must be non-negative")
            terms = args.query.lower().split()
            matches = [t for t in tools if all(term in " ".join([t["id"], t["summary"], t["category"], *t["aliases"]]).lower() for term in terms) and (not args.os or not t["platforms"] or normalize_platform(args.os) in t["platforms"]) and (not args.category or t["category"].lower() == args.category.lower())]
            matches = matches[:args.limit]
            if args.json: print(json.dumps(matches, indent=2, ensure_ascii=False))
            else:
                for t in matches: display(t)
            return 0
        if args.action == "show":
            entry = next((t for t in tools if t["id"] == args.id), None)
            if entry is None: raise ValueError("unknown id: " + args.id)
            display(entry, True); return 0
        if args.action == "categories":
            for category in sorted({t["category"] for t in tools}, key=str.lower): print(category)
            return 0
        if args.action == "check":
            selected = [t for t in tools if args.id is None or t["id"] == args.id]
            if args.id and not selected: raise ValueError("unknown id: " + args.id)
            for entry in selected: check_entry(entry)
            return 0
        if args.action == "add":
            entry = json.loads(args.entry.read_text(encoding="utf-8"))
            validate_tools([entry])
            index = next((i for i, t in enumerate(tools) if t["id"] == entry["id"]), None)
            if index is not None and not args.replace: raise ValueError("id exists; pass --replace to overwrite")
            if index is None: tools.append(entry)
            else: tools[index] = entry
            validate_tools(tools); save_registry(args.registry, data)
            print(("replaced " if index is not None else "added ") + entry["id"])
            return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print("tool-index: " + str(exc), file=sys.stderr); return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
