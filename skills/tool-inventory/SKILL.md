---
name: tool-inventory
description: Find and reuse existing scripts and CLI helpers before writing another one. Query the central categorized tool catalog by purpose, aliases and platform; inspect only the matching entry. Use when searching for a helper, repeated tool-call pattern, log/test/data summary or quota operation.
---

# Tool inventory

Before writing a reusable helper, run:

```sh
tool-index find "<purpose>" --os macos --limit 5
tool-index show <id>
tool-index check <id>
```

Use `windows` or `linux` on those hosts. This skill ships `scripts/tool_index.py`:
if the wrapper is absent, use `python3 <skill-directory>/scripts/tool_index.py` on macOS
or `python <skill-directory>/scripts/tool_index.py` on Windows (Scoop: `scoop install python`).
Resolve paths relative to the actual installed skill directory, not the current project.
The central registry defaults to `~/.agents/tool-inventory.json`; `TOOL_INVENTORY` or
`--registry PATH` can override it. Commands that query an absent registry fail explicitly.
For an authorized first-time setup, copy `assets/catalog.example.json` there without
overwriting an existing registry, then adapt its source paths. It is an example, not a
list of already-installed tools. `assets/context-state-template.md` supports compact
state handoffs. Tests live in `scripts/test_tool_index.py`; run unittest discovery on
that directory with bytecode disabled.

Search is lexical: try category terms or aliases when a phrase returns no results.
Use `tool-index categories` to see the small taxonomy. Load matching entries, not the
entire inventory into the conversation.

`find`, `show` and `check` do not execute catalog commands. `check` only inspects source
paths and dependency availability. A verified label is a dated observation, not current
health, authorization or a safety guarantee. Inspect the original source and its help
before running a newly found invocation. Honor task scope and effects metadata.

Reuse the original script in its repository or installed canonical location. Do not
copy it into another repo just to make it easier to find. If a matching helper needs a
fix, improve that source instead of generating an incompatible second version.

After creating an authorized reusable helper, add a metadata entry with `tool-index add
<entry.json>`: id, summary, aliases, category, kind, source, command, platforms,
dependencies, effects, status, verified_at, and optional notes. Use `--replace` only for
an intentional update of that id. Never store keys, environment dumps or private input.
Do not index every one-off command or scan unrelated repositories without scope.

On no match, perform a bounded local search before implementing. If the CLI or registry
is unavailable, state the limitation and use ordinary discovery; do not automatically
install packages as a substitute.

For async work, read bounded-wait: prefer reliable managed completion callbacks for long
jobs, tell the user what is running before yielding, and verify the final receipt. A
catalog entry describes capabilities; it does not create callback support in a host.
