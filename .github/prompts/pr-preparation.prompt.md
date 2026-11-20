---
description: "Prepare a truthful PR description, changelog entry, and reviewer checklist, then raise the PR if publishing is approved"
name: "SDLC 8 — PR Preparation"
agent: "PR Preparation Agent"
argument-hint: "Verified changes, test evidence, and whether publishing is approved"
---

Follow [the PR preparation skill](../skills/pr-preparation/SKILL.md). Read the verified diff, actual test evidence, known limitations, `CHANGELOG.md`, and `.github/PULL_REQUEST_TEMPLATE.md`.

Prepare the required Summary (2–3 sentences), Changes Made, Test Evidence, Known Limitations, and Reviewer Checklist in `target/pr-body.md`. Add a concise changelog entry following existing style. Do not invent test output, CI links, or a PR URL.

If publishing was approved in the request, raise the PR with `python3 scripts/pr/raise_pr.py ... --approved` and report its real result. If it was not approved, stop with the PR prepared locally and say no PR was created.
