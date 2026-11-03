---
name: bounded-wait
description: Choose bounded blocking waits or reliable asynchronous completion callbacks for long-running work. Use for builds, tests, service readiness, background tasks, or suspected hangs. Avoid repeated model-driven polling, preserve job identity and outcomes, and tell the user when waiting for a callback.
---

# Bounded Wait

Waiting time alone does not consume model tokens. Extra model calls, repeated context,
generated output and retries do. Choose a wait shape that preserves responsiveness and
completion evidence without repeatedly asking the model whether a job is done.

## Choose the wait shape

| Situation | Shape |
|---|---|
| Short command, within the runtime's foreground limit | One blocking command with an explicit timeout. |
| Service must become ready | Condition probe with a deadline and a timeout on each probe. Keep attempts outside the model loop. |
| Long work, runtime supports completion events and session resumption | Managed background job; tell the user what is running; resume on the completion event. |
| Job already runs under a managed runtime | Use its job ID and completion receipt. Do not relaunch or repeatedly snapshot it. |
| No reliable callback/resumption support | Bounded blocking output read. If still running, retain the ID and report the actual limitation. |

A plain `nohup ... &` starts a process; it does not establish a callback. A desktop
notification is not proof that the conversation will resume. Verify the host's actual
completion mechanism before promising to return automatically.

## Asynchronous completion contract

Before yielding to a callback, record enough information for the resumed session:

- Job ID and originating conversation/task ID.
- Command, working directory, purpose and authorized scope.
- Location of results/logs, deadline and success condition.
- Completion mechanism and how to retrieve the final exit status.

Tell the user, for example: "Tests are running in the background. I'm waiting for the
completion callback and will report the result here." Include an estimate only when
there is evidence for it. If other work remains, continue it while the job runs.

Follow the host's execution rules. Some hosts require foreground waiting unless the
user authorized background work. User authorization to work asynchronously is not
permission to drop unfinished tasks: retain ownership through completion or failure.

On callback: match the job ID, retrieve its exit status and bounded output, then report
success, failure or timeout. If delivery repeats, do not repeat the work. After a crash
or restart, inspect recorded job state before relaunching; absence of a callback is not
proof that a side-effecting operation never ran. Do not start a new agent solely to wait.

## Silence is not a hang

A remote model may reason for minutes while local CPU usage and stdout stay unchanged.
Low CPU, stale logs, or no visible tokens alone are insufficient grounds to kill it.

Check the actual request/job state, configured deadline, transport errors and any
available provider progress. Cancel on user request, a reached deadline, explicit
failure, or verified deadlock/stall with task-specific evidence. State that evidence.

For scripts you own, emit useful phase/progress receipts when available. Heartbeats
mean "alive", not "making progress". Do not alter an unrelated program merely to make
it print every 30 seconds. Do not force streaming or lower reasoning effort just to
make a reasoning task appear active.

## Readiness recipe (Bash)

```bash
# A healthy HTTP response is the condition; every request and the whole loop are bounded.
wait_http() {
  local seconds="$1" url="$2" deadline
  deadline=$((SECONDS + seconds))
  while (( SECONDS < deadline )); do
    if curl -fsS --connect-timeout 1 --max-time 2 "$url" >/dev/null 2>&1; then
      echo READY
      return 0
    fi
    sleep 1
  done
  echo "TIMEOUT: readiness deadline reached" >&2
  return 124
}
wait_http 120 http://127.0.0.1:8080/health
```

The caller should also set a tool timeout slightly above the readiness deadline; an
in-flight probe can overrun it by its own short timeout. This recipe uses Bash `SECONDS`;
on Windows use an equivalent bounded PowerShell probe, not Bash pasted into PowerShell.
A socket listener or live process establishes less than an application health response.
A nonempty result file may still be incomplete: use the producer's completion receipt.

## Output and evidence

- Return exit status, elapsed time, useful summary, and a pointer to the original log.
- Keep raw evidence available; a summary or truncated tail cannot establish absence of
  earlier errors. Read more when the decision depends on complete coverage.
- Preserve distinctions between success, timeout, process exit and callback failure.
- Do not stack lossy compressors blindly; use one summary with a raw-evidence recovery path.

## Cost and anti-patterns

Count model invocations, actual input/cached input/output tokens, retries and task
outcomes. A blocking observation may wait without invoking the model; another host may
return a running status and trigger another model step. Check the runtime rather than
assuming every tool read has identical cost.

Avoid repeated model-driven status checks, fixed sleeps used as readiness guesses,
unbounded `tail -f`/loops, full-log dumps, and relaunching jobs because the callback is
late. Event-based resumption may add one final model call; that can still beat many polls
while keeping the user informed. Cache savings and provider billing vary.

## Policy block

```text
Waiting policy:
- Short work: bounded blocking call. Readiness: bounded condition probe.
- Long work: prefer managed completion events that reliably resume this conversation.
- Before yielding, tell the user what is running and waiting; retain job/result identity.
- No reliable callback: bounded output read, retain job ID, disclose the limitation.
- Do not repeatedly invoke the model to poll or spawn an agent just to wait.
- Silence or low local CPU during remote reasoning is not proof of a hang.
- On completion/failure, verify the receipt and report once with evidence pointers.
```
