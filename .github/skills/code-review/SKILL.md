---
name: code-review
description: "Read-only review of a change against the user story, covering correctness, security, error handling, tests, clarity, duplication and dependencies."
argument-hint: "Diff, commit, or changed files"
---

# Code review

1. Read the requirements, the approved architecture and design decisions, and the whole diff.
2. Trace each changed behavior back to an acceptance criterion, and look at the code that calls it and the tests around it.
3. Check whether it is correct, whether input is validated, whether secrets are exposed, how errors are handled, whether both success and failure are tested, whether it reads clearly, whether code is duplicated, and whether new dependencies are safe. Only check what the evidence lets you.
4. Report defects and risks someone can act on, most severe first. For each, give the file and line, the impact, the evidence, a suggested fix, and how confident you are.
5. Label what is confirmed and what is a question. If you find nothing, say what you checked and what you couldn't check.

This phase is read-only. Don't edit code, don't run anything destructive, and don't say tests passed unless you ran them.
