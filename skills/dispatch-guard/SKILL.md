---
name: dispatch-guard
description: Decide whether to delegate work to a subagent or agent-crew member, or keep it inline. Use before any Task or subagent dispatch, when a plan looks like "spawn N agents", when token cost or context drift is noticed, or when reviewing a multi-agent setup. Model-agnostic — it reasons about context handoffs, never about specific models or projects.
---

# Dispatch Guard

Delegation is a **context handoff**, and every handoff has a price. This skill decides
whether the price is worth paying. It uses vendor-neutral model tiers. Adapt these defaults to the host's actual
context sharing, parallel execution, tool access and artifact support.

## The one principle

> Default to inline work when the context is already loaded. Delegate when
> isolation, independent parallel work or specialist capabilities provide a
> concrete benefit that justifies the handoff.

The rules below are recommended defaults, not universal performance results.

## What a handoff actually costs

Check these four potential costs. Hosts with shared context or durable artifacts
can reduce them; measure the actual handoff rather than assuming all four occur:

1. **Restatement** — the parent must re-describe background the parent already holds.
   Background unavailable to the child may need restating, with a risk of lost detail.
2. **Re-derivation** — the child re-reads, re-greps, re-fetches sources the parent already
   consumed. Count duplicate reads separately from necessary independent verification.
3. **Loop overhead** — the child runs its own multi-step tool loop inside its own window.
   A task that is "one lookup" in a shared context becomes N turns in a fresh one.
4. **Report loss** — prose-only returns can omit evidence needed by the parent.
   Durable artifacts, source pointers and structured results reduce this risk;
   verify that the parent can actually retrieve them.

Context rebuilt and extra tool/model turns are useful cost drivers. They are not
a billing formula: caching, runtime support and parallel latency also matter. A
small task with a large context dependency can cost more to hand off than to do inline.

## Decide: inline or delegate

Use these questions as a default decision guide. A concrete capability or measured
latency benefit can justify an exception; state that reason before dispatch.

| Question | Inline (do it yourself) | Delegate |
|---|---|---|
| Does the subtask need facts I already loaded this session? | yes | no — it owns its own sources |
| Will I need to reason about its intermediate detail, not just its conclusion? | yes | no — I only need the verdict |
| Is the subtask exploring a question whose *shape* I can't state yet? | yes | no — I can state input scope + output contract up front |
| Does it need my conversation history to be competent? | yes | normally keep inline |
| Is it 1–3 tool calls of work? | yes | normally keep inline |

**Rule of thumb:** if you cannot write the child's **input scope** and **output contract**
in two lines before dispatching, you are not ready to dispatch — you are still thinking.
Think inline first, then delegate the mechanical part.

## Patterns that often add avoidable overhead

- **Discussion split across agents.** "Have 6 personas discuss this" — they all need the
  same source material, none can see the others' moves, and the parent re-reads 6 essays.
  Prefer one structured pass unless independent perspectives have a defined,
  measurable role.
- **Reviewer agent on your own reasoning.** A blind reviewer can't see why you decided
  something, so it critiques a paraphrase of your conclusion. Either give it the artifact
  (not the reasoning) and accept that framing, or review inline.
- **Sequential chains.** Step B delegated after step A *because* it depends on A's output:
  each hop re-establishes context. Keep dependent steps in one context.
- **Spawn-per-file / spawn-per-function.** Fan-out is cheap only when the children share
  nothing; the parent still pays to collect and reconcile N reports.
- **Recursive spawn** (an agent that spawns agents). Depth ≥ 2 means context has been
  restated at least twice. Ban it unless the recursion is the product.

## Patterns that can justify delegation

- **Isolated bulk IO**: scan/transform hundreds of items, return only the distilled result.
  The parent would otherwise drown in raw output.
- **Disjoint parallel research**: several sources, no cross-dependency, only findings needed.
- **Blind evaluation**: grading an artifact the child should judge without the author's
  narrative.
- **Flood protection**: a subtask whose raw output would otherwise consume a large share of
  the parent's window, and whose conclusion fits in a paragraph.

## Guardrails to keep on

- **Default fan-out cap per turn**: 2–3. Raise it only for bounded independent work
  with a concrete latency or throughput benefit and host capacity.
- **Depth ≤ 1.** A child may not spawn.
- **Every dispatch states**: input scope (exact files/URLs/IDs), output contract (length +
  what must be included), and what the child must NOT do (no file writes, no plan changes).
- **No delegation of the decision itself.** The parent keeps judgement; children gather.
- **Reconcile, don't concatenate.** N reports must collapse into one answer with conflicts
  named, otherwise the parent has just moved its reading problem one level down.

## Two example decisions

**Inline:** the parent has already read a function and its failing test. The next
step is a two-line fix in that function. A new agent would need the same context,
and the parent still needs to inspect the exact diff. Keep the edit and test inline.

**Delegate:** three independent repositories need their public documentation links
checked. Give each worker one repository, read-only scope, and a short result with
file/line references. No worker needs another's findings. Independent execution
may reduce elapsed time; compare total spend and correctness with an inline run
before claiming a cost saving.

## Model placement (vendor-neutral tiers)

Think in tiers, not names:

- **T1 — reasoning/strong**: planning, design tradeoffs, ambiguous judgement, final synthesis.
- **T2 — workhorse**: routine multi-file edits, standard refactors, doc writing.
- **T3 — mechanical**: extraction, reformatting, classification, bulk transforms.

Placement rules:

1. **Prefer T1 for ambiguous orchestration and final judgement.** Simple, well-specified
   routing may need less reasoning. Choose capability from observed correctness
   and failure cost, not a tier label alone.
2. **Children should not silently inherit the parent's tier** if the parent is T1 and the
   child does mechanical work — that's paying T1 prices for T3 work. Conversely never let
   children inherit *downward*: a T3 parent with T3 children is a compounding error rate.
3. **Prefer reusable skills over repeated discovery.** A documented procedure can
   reduce repeated work. Compare skill-loading and execution costs before claiming
   savings over delegation.
4. **Escalate on failure, don't parallelise on doubt.** When unsure, one strong pass;
   when a pass demonstrably fails, then split.

## Measure it (this is where the illusion lives)

- **Subagent spend is often booked in a separate ledger** from the main conversation.
  If you only read the main usage figure you will systematically under-report. Sum
  **both** before judging. If the split ledger doesn't exist, treat every delegation as
  unmetered and cap harder.
- Compare **cost per successfully completed task**, including cached/uncached input,
  output, retries, correctness and latency. A short answer may require substantial valid
  analysis; tokens per answer length alone cannot show waste.
- **Output-to-input ratio** is descriptive, not a model-quality or efficiency verdict.
  Large cached input plus a short correct result can be economical. API list prices are
  not necessarily subscription quota multipliers.
- Track **duplicate-source reads**, distinguishing necessary independent verification
  from redundant discovery. Compare with an inline baseline before attributing savings.
- Before writing a reusable helper, search the available tool inventory by purpose and
  platform. Reuse the canonical script rather than regenerating it in a child context.

## Calibrating this skill on a new machine

Do this once per environment, in five minutes:

1. Find where per-turn usage is recorded, and whether delegated work lands in the same
   place. Write the two paths down. If only one exists, note that delegation is invisible.
2. Pick the last 5 delegations from history. For each, classify: isolated-IO, disjoint
   research, blind eval, discussion-split, reviewer, chain. Anything in the last three
   categories is a candidate for inlining.
3. Compute delegated-token share of total as an audit signal, not a fixed failure
   threshold. Inspect task independence and outcomes; delegated bulk work can legitimately
   dominate the total.
4. Check the crew/agent config for: delegation allowed?, children inherit model?, and
   **circular `delegatesTo` graphs** (A→B→A). A configured cycle is not proof of wasted
   execution; inspect observed handoffs for ping-pong or unclear ownership.
5. Write the result into the local policy block below. Re-run when the setup changes.

## Policy block (paste into agent instructions, keep short)

```
Delegation policy:
- Default = inline. Delegate only for isolated bulk IO, disjoint research, or blind eval.
- Before dispatching, state: input scope, output contract, forbidden actions. Can't write
  both lines? Don't dispatch yet.
- Max 3 dispatches per turn. Depth 1. Children never spawn.
- Discussion, review-of-my-own-reasoning, and dependent chains stay in one context.
- Match orchestrator capability to judgement difficulty; use cheaper workers when
  observed correctness supports it.
- Report delegated spend alongside main spend, or don't claim the run's cost.
```
