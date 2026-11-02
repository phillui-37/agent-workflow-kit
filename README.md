# agent-dispatch-guard

Two model-agnostic skills about the two things that quietly cost you the most tokens:
**delegation** and **waiting**.

No model names. No vendor names. No project names. Both reason about **context handoffs**,
so they work the same on any machine, any provider, any repo.

| Skill | Question it answers |
|---|---|
| [`dispatch-guard`](skills/dispatch-guard/SKILL.md) | Should this be a subagent, or should I just do it? |
| [`bounded-wait`](skills/bounded-wait/SKILL.md) | How do I wait for this without burning context or hanging? |

## The two principles

> **Dispatch** — A subagent buys you an *isolated context*. That is the only thing it buys.
> If the subtask doesn't need isolation, you paid for it and got nothing.

> **Waiting** — Cost of a wait ≈ context size × number of wait steps. It doesn't depend on
> wall-clock time. Minimise **steps**, not seconds.

Together they explain most of a multi-agent setup's bill: the parent pays to restate
context it already had, the child pays to rebuild it, and every status check in between
re-sends the whole thing.

## Install

```bash
# both skills, project-level
npx skills add phillui-37/agent-dispatch-guard

# one of them
npx skills add phillui-37/agent-dispatch-guard --skill dispatch-guard

# globally, no prompts
npx skills add phillui-37/agent-dispatch-guard --global --all
```

**Alma**

```bash
alma skill install phillui-37/agent-dispatch-guard
```

**Manual** — copy either `skills/<name>/` directory into your skills folder
(`~/.claude/skills/`, `~/.config/alma/skills/`, …).

**Anything else** — each skill ends with a plain-text `Policy block`. Paste that into your
agent's system instructions; it's the whole thing in 8 lines.

## dispatch-guard

| Section | What it gives you |
|---|---|
| Cost model | The four things every dispatch pays, regardless of outcome |
| Decision table | 5 questions; any "inline" answer stops the dispatch |
| Anti-patterns | 6 shapes that always lose, and why |
| Legit uses | 4 shapes where isolation genuinely wins |
| Guardrails | Fan-out caps, depth limit, scope/contract requirement |
| Model tiers | T1/T2/T3 placement rules — the orchestrator is always T1 |
| Measurement | How to catch split-ledger under-reporting |

## bounded-wait

| Section | What it gives you |
|---|---|
| Three rules | One step; condition not duration; distinguishable outcome |
| Shape table | Block / probe-with-deadline / detach-and-collect-once |
| Recipe | `wait_for <seconds> <cmd>` with early exit and a timeout code |
| Readiness probes | Cheapest reliable condition per target type |
| Anti-patterns | fixed `sleep`, cross-turn polling, polling a push queue, `tail -f` |
| Cost model | Why steps matter and seconds don't |

## Calibrating on your machine

Don't trust either skill blindly — both ship with a checklist.

1. Find where per-turn usage is recorded, and whether delegated work lands in the **same**
   place. If there's only one ledger, delegation is invisible — cap harder.
2. Classify your last 5 delegations: isolated-IO, disjoint research, blind eval,
   discussion-split, reviewer, chain. The last three should have been inline.
3. Compute delegated-token share. Above ~50% means the dispatch default is wrong.
4. Count your wait steps per turn. If a single job produces more than one wait step in the
   conversation, the wait is in the wrong shape.
5. Write the result into the local policy blocks.

## License

MIT
