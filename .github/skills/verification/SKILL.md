---
name: verification
description: "Run the tests and checks, then confirm each acceptance criterion with evidence from the run."
argument-hint: "Acceptance criteria, changed files, and expected outputs"
---

# Verification

1. Read the approved acceptance criteria, the diff, the review findings and the documented commands.
2. Pick the smallest safe set of test and build commands that covers the change. Read any script you don't recognize, and any that might delete things, before running it.
3. Run them. Report the exact commands, counts and results, and every real failure. Don't make up logs or claim a check you didn't run.
4. Check each acceptance criterion against what the system does or the output it produces. A clean compile doesn't prove acceptance.
5. If the change produces documents, check that the sections are there, that they agree with each other, and that nothing stale is left in them.
6. Say what is untested and what still fails.
7. Show the evidence and wait for the user to accept it before PR preparation.

Don't change product code, and don't hide or skip a failing test.
