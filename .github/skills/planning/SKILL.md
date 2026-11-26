---
name: planning
description: "Break the approved architecture into small, ordered implementation tasks with tests, deliverables and any blockers."
argument-hint: "Approved architecture and design review"
---

# Planning

1. Read the approved requirements, architecture and design review, and check how the repository is organized.
2. Split the work into small tasks that can each be verified on their own, highest priority first.
3. List a dependency only when one task needs another's output. Being earlier in the list isn't a dependency.
4. Cover the code, tests, documentation, review and verification.
5. For each task, say what shows it is done and how it will be tested.
6. Mark blocked tasks and say what is missing: a decision, a dependency, access or input.
7. Write or update `impl-plan.md`, show it, and wait for approval before anyone starts implementing.

Don't implement any of the planned work.
