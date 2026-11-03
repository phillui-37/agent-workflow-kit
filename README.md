# agent-dispatch-guard

[![skills.sh](https://skills.sh/b/phillui-37/agent-dispatch-guard)](https://skills.sh/phillui-37/agent-dispatch-guard)

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

> **Waiting** — Waiting time alone is not model token consumption. Avoid repeated
> model-driven polling. Prefer reliable completion callbacks for long work; tell the user
> what is running before yielding.

Delegation and waiting can add model calls, context replay and retries. Actual cost
also depends on cache hits, output and provider billing. Measure successfully completed
tasks rather than assuming that every wait or short answer has the same cost.

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
| Wait shapes | Bounded blocking / readiness probe / managed completion callback |
| Callback contract | Job identity, result location, deadline, user update and final receipt |
| Hang diagnosis | Remote reasoning silence and low local CPU alone do not establish a hang |
| Recipe | Bounded Bash HTTP probe, including a timeout on each request |
| Evidence | Preserve original logs and distinguish timeout, failure and success |
| Cost model | Count actual model calls, tokens, retries and outcomes |

## Calibrating on your machine

Don't trust either skill blindly — both ship with a checklist.

1. Find where per-turn usage is recorded, and whether delegated work lands in the **same**
   place. If there's only one ledger, delegation is invisible — cap harder.
2. Classify your last 5 delegations: isolated-IO, disjoint research, blind eval,
   discussion-split, reviewer, chain. The last three should have been inline.
3. Compute delegated-token share as an audit signal, then compare cost and correctness
   per completed task. A high share alone does not prove waste.
4. Count model-driven polls, distinguish them from blocking observations, and verify
   whether the host can reliably resume the conversation on completion.
5. Write the result into the local policy blocks.

## License

MIT
