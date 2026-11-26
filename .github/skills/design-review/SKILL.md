---
name: design-review
description: "Review the architecture against the requirements and record risks, gaps, decisions and fixes before any code is written."
argument-hint: "Requirements and architecture documents"
---

# Design review

1. Read the approved `requirements.md` and `architecture.md`. If either is missing or not approved, stop.
2. Check that the design covers every requirement. Then look at data flow, trust boundaries, what happens on failure, security and privacy, scale, operations, testing, maintenance, and the dependencies it relies on.
3. Only record findings you can back with evidence and act on. Rank them by severity and give the impact, the evidence and a fix.
4. Keep findings, open questions and trade-offs in separate lists. A proposed decision is not an approved one.
5. Write the findings and the decisions that were agreed to `design-review.md`.
6. For each accepted finding, propose the exact change to the architecture. Ask before applying a change that alters behavior.
7. Wait for approval before implementation planning.

Don't write production code in this phase.
