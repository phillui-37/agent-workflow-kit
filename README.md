# agent-dispatch-guard

A model-agnostic skill that decides **when to delegate work to a subagent and when to just do it inline** — and makes the cost of a bad dispatch visible before you pay it.

No model names. No vendor names. No project names. It reasons about **context handoffs**, so it works the same on any machine, any provider, any repo.

## The one principle

> A subagent buys you an **isolated context**. That is the only thing it buys.
> If the subtask doesn't need isolation, you paid for it and got nothing.

## The problem it targets

Multi-agent setups fail in a specific, measurable way: the parent restates context the child cannot see, the child re-reads sources the parent already read, and what comes back is prose — so evidence is lost while tokens are spent twice. In practice this shows up as:

- a "discussion" split across N personas, all of whom needed the same source material
- a reviewer agent critiquing a paraphrase of your own reasoning
- dependent chains, where each hop rebuilds context
- delegated spend booked in a **separate ledger**, so the run looks cheaper than it was

## What's inside

| Section | What it gives you |
|---|---|
| Cost model | The four things every dispatch pays, regardless of outcome |
| Decision table | 5 questions; any "inline" answer stops the dispatch |
| Anti-patterns | 6 shapes that always lose, and why |
| Legit uses | 4 shapes where isolation genuinely wins |
| Guardrails | Fan-out caps, depth limit, scope/contract requirement |
| Model tiers | T1/T2/T3 placement rules — orchestrator is always T1 |
| Measurement | How to catch split-ledger under-reporting |
| Calibration | 5-minute checklist to adapt it to a new machine |

## Install

**Alma**

```bash
alma skill install <owner>/agent-dispatch-guard
```

Or drop `SKILL.md` into `~/.config/alma/skills/dispatch-guard/SKILL.md` and restart.

**Claude Code / agent runtimes that read `SKILL.md`**

```bash
git clone https://github.com/<owner>/agent-dispatch-guard.git ~/.claude/skills/dispatch-guard
```

**Anywhere else**

The `Policy block` at the end of `SKILL.md` is plain text — paste it into your agent's system instructions. It's the whole skill compressed to 8 lines.

## Calibrating on your machine

Don't trust the skill blindly; it ships with a checklist instead:

1. Find where per-turn usage is recorded, and whether delegated work lands in the same place. If there's only one ledger, delegation is invisible — cap harder.
2. Classify your last 5 delegations: isolated-IO, disjoint research, blind eval, discussion-split, reviewer, chain. The last three should have been inline.
3. Compute delegated-token share. Above ~50% means the dispatch default is wrong.
4. Check the crew/agent config for delegation allowed, inherited model tier, and **circular `delegatesTo` graphs**.
5. Write the result into the local policy block.

## License

MIT
