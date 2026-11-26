---
name: implementation
description: "Implement an approved task with a small change, tests that cover it, updated docs and honest test results."
argument-hint: "Approved task ID or description"
---

# Implementation

1. Read the approved requirements, architecture, design-review decisions and implementation plan.
2. Confirm the task is approved, not blocked, and specific enough to start. Ask before changing what users see or how the architecture works.
3. Look at the existing code, tests, helpers and conventions around the change before editing.
4. Make the smallest change that fully does the job. Leave unrelated work and current behavior alone.
5. Add tests for the normal path, input validation, and the error and edge cases that matter.
6. Update the docs the change touches. State limitations and failures as they are.
7. Run the smallest relevant tests or build, record the exact result, and mark the task done only if the result supports it.
8. Stop before any commit, push, deployment or PR, unless the user has approved it.
