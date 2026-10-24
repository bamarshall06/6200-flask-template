# The deploy

**This file is graded.** *Deploy & Secure* reads it for four of five criteria.
Replace each TODO; the headings are where the grader looks.

## The guardrail

**Commit your budget alarm or recorded starting position BEFORE you create your
first AWS resource.** The ordering is what is graded, not the alarm — and in a
repository the ordering is a fact rather than a claim, because the commit is
dated.

Screenshot committed as: `TODO`

## IAM, permission by permission

Paste the policy, then **one line per permission naming the code that needs
it**. No wildcards. "Which line of my code needs this, and what breaks without
it?" is the question each line answers.

```json
TODO
```

| Permission | The code that needs it | What breaks without it |
|---|---|---|
| | | |

## The Bedrock call, and both ways it goes wrong

A model call fails in two distinct ways and both need handling:

1. **The call itself fails** — timeout, throttle, no credentials. TODO
2. **The call succeeds and returns something unusable** — truncated, not the
   shape you parsed for, empty. TODO

## It ran without my laptop

An S3 object with a timestamp, and a log entry from an invocation you did not
trigger by hand. TODO

## What my code assumed about my laptop that broke in the cloud

TODO

## Cost, by service

Label what was **continuous** and what was **per-use**. A single number is not a
breakdown.

| Service | Cost | Continuous or per-use |
|---|---|---|
| | | |

## Teardown, verified

What you destroyed, **how you confirmed it is gone**, and what would still be
billing if you had missed something. A teardown you did not verify is not a
teardown.

TODO
