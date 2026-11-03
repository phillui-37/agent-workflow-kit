# agent-workflow-kit

[![skills.sh](https://skills.sh/b/phillui-37/agent-workflow-kit)](https://skills.sh/phillui-37/agent-workflow-kit)

Model-agnostic skills for **delegation, waiting and tool reuse**. Keep useful evidence,
avoid repeated work, and measure cost per completed task.

Previously named `agent-dispatch-guard`. The repository grew beyond delegation; the
individual skill names remain stable so you can install only what you need.

| Skill | Question it answers |
|---|---|
| [dispatch-guard](skills/dispatch-guard/SKILL.md) | Should this work be delegated or kept in the current context? |
| [bounded-wait](skills/bounded-wait/SKILL.md) | Should I block, probe readiness, or resume through a completion callback? |
| [tool-inventory](skills/tool-inventory/SKILL.md) | Does a reusable script or tool already solve this problem? |

## Install

```bash
# Select skills interactively
npx skills add phillui-37/agent-workflow-kit

# All three, globally, without prompts
npx skills add phillui-37/agent-workflow-kit -g --skill '*' -y

# Just discovery and reuse
npx skills add phillui-37/agent-workflow-kit -g --skill tool-inventory -y
```

Windows uses the same `npx` commands. Install Node.js and Python with Scoop when needed:

```powershell
scoop install nodejs-lts python
```

Alma can also install the repository:

```bash
alma skill install phillui-37/agent-workflow-kit
```

Manual installation: copy a `skills/<name>/` directory into your client's skills folder.
Preserve the `scripts/` and `assets/` subdirectories for tool-inventory. Other runtimes
can follow the skill instructions directly; verify their tool and callback support.

## What each skill does

**dispatch-guard** makes context handoff costs explicit: restatement, rediscovery,
additional tool loops and incomplete reports. It provides scope/output contracts,
fan-out/depth guardrails, model tiers and accounting checks. Compare correctness,
latency, cached/uncached input, output and retries. A low output/input ratio or high
subagent share alone cannot establish waste.

**bounded-wait** chooses bounded blocking for short work and reliable managed completion
callbacks for long work. Before yielding, tell the user what is running; retain job ID,
results, deadline and completion condition. Check the final receipt on resumption.
Plain nohup is not a callback; silence or low local CPU during remote reasoning is not
proof of a hang. Waiting time itself is not model token consumption.

**tool-inventory** adds a stdlib-only Python CLI and a small metadata catalog. Search
purpose, aliases, category and OS before writing another helper. Scripts remain at their
canonical sources; the catalog neither copies them nor executes stored commands.

## Tool inventory setup

The skill bundles:

```text
skills/tool-inventory/
  SKILL.md
  scripts/tool_index.py
  scripts/test_tool_index.py
  assets/catalog.example.json
  assets/context-state-template.md
```

Choose a registry path, normally `~/.agents/tool-inventory.json`. Copy the example only
for a new registry; never overwrite an existing one. Replace example source paths with
actual tools on that machine. You can instead set `TOOL_INVENTORY` or pass `--registry`.

Run directly from the repository or installed skill directory:

```bash
python3 skills/tool-inventory/scripts/tool_index.py find archive --os macos --limit 5
python3 skills/tool-inventory/scripts/tool_index.py show archive-helper
python3 skills/tool-inventory/scripts/tool_index.py check archive-helper
```

On Windows replace `python3` with `python`, and use `--os windows`. An optional shell
wrapper can name this command `tool-index`; skills-only installation does not add a
binary to PATH. The example catalog does not establish tool availability on Windows.

`find`, `show`, `categories` and `check` read metadata. `check` examines paths and
executable dependencies without running catalog commands; existence is not health or
permission. `add <entry.json>` validates and saves an entry, refusing replacement unless
`--replace` is explicit; it retains the previous registry in one `.bak` file.

Keep entries small: id, summary, aliases, category, source, invocation, platform,
dependencies, effects, status and verification date. Do not store credentials or private
inputs. `context-state-template.md` supports current decisions, superseded decisions,
evidence, pending work and callback identity at a task boundary.

## Verification and limits

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/tool-inventory/scripts -v
```

Four tests cover alias/platform queries, validated mutation, absent-registry errors and
checks not executing commands. Executed on macOS; Windows end-to-end validation remains
pending. Search is lexical, not semantic. There is no daemon, automatic filesystem scan,
new routing proxy, or compulsory compressor. Callback support belongs to each runtime.

This repository contains reusable procedures and generic fixtures, not a machine's
private registry, credentials or conversation records. Preserve raw evidence when a
summary cannot answer the question.

## License

MIT
