---
name: simple-by-design-adaptive
description: Design a solution through focused CLI-routed prompts.
disable-model-invocation: true
---

Set `S` to this skill's absolute directory. From the task project, run:

```sh
python3 "$S/scripts/sbd.py" --request '<complete request, constraints and permissions>'
```

Loop: decide → construct a counterexample → resolve or defer → challenge again.

Bare invocation resumes. Do only the returned prompt, then use its printed return command. Continue until `DONE`; if blocked, ask for what is needed and pause. Produce a design, not implementation.
