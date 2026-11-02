---
name: bounded-wait
description: Decide how to wait for long-running work (servers, builds, test suites, jobs, file drops) without burning tokens or hanging a turn. Use when a command needs time to finish, when a service must become ready before the next step, when a job or background task is already running, or when you catch yourself about to write a sleep, a poll loop, or a repeated status check.
---

# Bounded Wait

Waiting is not free and it is not neutral. **Every wait costs a full re-send of the
conversation context**, whether you fill it with a 5-minute sleep or 30 one-second polls.
The only question is how many times you pay it.

Vendor-neutral. No tool names required beyond "run a command" and "read its output".

## Three rules

1. **Wait inside one step, never across steps.** A wait that spans turns pays context
   replay per turn. A wait that lives inside a single command pays once.
2. **Wait on a condition, never on a duration.** `sleep 20` is a guess. If it's too short
   you wait again (another replay); if it's too long you burn dead time. Wait for the
   *thing to be true*, with a deadline.
3. **Every wait ends with a distinguishable outcome.** Success, timeout, and failure must
   have different exit codes or markers — otherwise the next step can't tell "not ready
   yet" from "never going to be ready", and will retry a broken thing forever.

## Pick the shape before you write anything

Ask: **is the total wait shorter than one command's maximum timeout?**

| Total expected wait | Shape |
|---|---|
| Under the single-call cap (typically 1–10 min) | One blocking call with an explicit timeout. No loop, no polling. |
| Near the cap, unknown duration | Blocking readiness check with early exit, inside one call (recipe below). |
| Over the cap, or genuinely long (builds, benchmarks, migrations) | Detach it, return an id immediately, collect **once** at the end with a blocking read. |
| Already running as a managed job | Don't poll it. Collect once, blocking, at the end. |

The failure mode of the last two rows is the worst one: a detached job that gets polled
every 30 seconds from the conversation is *more* expensive than never detaching it,
because you pay context replay per poll and gain nothing over one blocking read.

## Recipe — readiness with early exit

```bash
# wait_for <seconds> <command...> ; returns 0 ready, 124 timeout
wait_for() {
  local deadline=$(( SECONDS + $1 )); shift
  until "$@" >/dev/null 2>&1; do
    (( SECONDS >= deadline )) && return 124
    sleep 1
  done
}

wait_for 120 curl -sf http://127.0.0.1:8080/health || { echo "TIMEOUT: not ready in 120s"; exit 124; }
echo READY
```

Four properties worth copying: condition-based, deadline-bounded, distinct timeout code,
and **only the outcome is printed** — not every attempt.

## Readiness conditions, cheapest first

| Target | Condition |
|---|---|
| HTTP service | `curl -sf <url>/health` (status code, not body) |
| Port listener | `nc -z 127.0.0.1 <port>` or a `/dev/tcp` probe |
| Log line | `grep -q "started" <logfile>` — but see the log rule below |
| File drop | `test -s <path>` (and optionally `! -name '*.part'`) |
| Process | `kill -0 <pid>` — confirms alive, not healthy |

Prefer a probe that returns a **status**. Absence of an error in a log is not readiness.

## Anti-patterns

- **`sleep N` as a readiness guess.** Replace with the recipe above. Fixed sleeps are
  either too short (extra replay) or too long (dead time), and never both correct.
- **Polling from the conversation.** Each poll turn = one context replay. A 10-poll wait
  in a 200K-token context reads ~2M tokens to learn one boolean.
- **Polling a job system that already pushes events.** If the runtime reports completion,
  subscribe or collect once blocking. Polling a push-based queue is pure waste.
- **`tail -f`, `watch`, interactive pagers.** They never terminate; the turn hangs until
  an external timeout kills it, and the partial output still lands in context.
- **Unbounded `until`.** Always a deadline and always a distinct exit code.
- **Dumping the whole log while waiting.** Print the last N lines, or the matching lines.
  A 5MB log in a wait step costs more than the wait itself.
- **Waiting to "see if it settles."** If you can't name the condition, you don't want to
  wait — you want to measure. Run the check once and read the result.

## Cost model

Cost of a wait ≈ **context size × number of wait steps**. It does not depend on wall-clock
time at all. Consequences:

- Two waits of 30 seconds in one call cost the same as one wait of 60 seconds.
- Two waits in *separate* turns cost double, even if each is 1 second.
- Cache hits make repeat sends cheaper but never free, and never faster for the user.

So: minimise **steps**, not seconds. Always.

## Reporting what happened

When the wait ends, report the outcome, not the process:

```
build: ok (128s) · tests: 412 passed, 0 failed · artifacts: dist/app.zip (18.2MB)
```

Not a transcript of the polling. The next reader — human or agent — needs the state and
the exit condition, not the attempts.

## Policy block (paste into agent instructions)

```
Waiting policy:
- Never wait across turns. One step, one wait.
- Never sleep a fixed duration. Wait on a condition with a deadline and a distinct timeout code.
- Long work: detach, return an id, collect ONCE with a blocking read at the end.
- If the runtime pushes completion events, don't poll.
- Print only the outcome: last N log lines or a status line, never the whole log.
- A wait step must end with success | timeout | failure, distinguishable.
```
