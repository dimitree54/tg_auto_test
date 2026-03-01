---
name: reproduce-fix-release
description: Pipeline of TDD bug fixing
disable-model-invocation: true
---

1. Ask "reproduce-bug" sub-agent to reproduce the bug
2. Make sure that "reproduce-bug" created a failing test
3. Fix the bug
4. Make sure that reproducing test became green
5. Use gh to create new release with the fix
