# The security report

**This file is graded.** *Deploy & Secure* reads it for the findings, the
remediation and the limits. Write it as a report someone would act on, because
that is the only reason this format exists.

## Scope

**Your own infrastructure and machines. Nothing belonging to another student,
and neither course server.** Going outside this is a project failure, not a
deduction.

What I was allowed to inspect: TODO

## Findings

Each finding carries a **stable id**, what was **actually observed**, a
**severity**, and **why it matters**. Evidence beside the claim — a verdict
alone is a conclusion without the observation behind it.

### F-001 — TODO

- **Observed:** TODO *(what the check actually saw, not what you concluded)*
- **Severity:** TODO
- **Why it matters:** TODO

## The remediation

Dry-run by default, `--confirm` required to act, safe to run twice, and a
rollback you have **genuinely executed**.

**This is where submissions most often fall down, and always in the same way:
the rollback is described rather than run.** Run it. Break the fix back, look at
what happened, and put both outputs here.

```
# dry run
TODO

# --confirm
TODO

# rollback, executed
TODO
```

## The scheduled run

What you scheduled, and what it reported when it ran unattended. TODO

## What my checks could not see

Every honest security report has this section. TODO
