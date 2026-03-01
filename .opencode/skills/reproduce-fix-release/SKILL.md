---
name: reproduce-fix-release
description: Pipeline of TDD bug fixing
disable-model-invocation: true
---

1. Ask "reproduce-bug" subagent to reproduce the bug. Note: do not use "reproduce-bug" as a skill, but strictly as a subagent.
2. Make sure that "reproduce-bug" created a failing test
3. Read repo docs and contribution guides
4. Fix the bug (following repo docs and contribution guides)
5. Make sure that the reproducing test became green
6. Use gh to create a new release with the fix
