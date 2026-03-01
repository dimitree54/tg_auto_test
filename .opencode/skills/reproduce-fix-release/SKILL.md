---
name: reproduce-fix-release
description: Pipeline of TDD bug fixing
disable-model-invocation: true
---

1. Ask "reproduce-bug" subagent to reproduce the bug. Note: do not use "reproduce-bug" as a skill, but strictly as a subagent.
2. Make sure that "reproduce-bug" created a failing test. Note: do not write tests yourself. Only the "reproduce-bug" subagent is allowed to write tests.
3. Read repo docs and contribution guides
4. Fix the bug (following repo docs and contribution guides). Note: you are making not a hot-fix but a proper fix. Investigate the root cause of the bug. If some refactoring is needed for a proper fix - do it. Only a proper fix of the root cause is allowed. No hot-fixes, no hiding errors, no fallbacks. Only proper fix!
5. Make sure that the reproducing test became green
6. Use gh to create a new release with the fix
