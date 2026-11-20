# Changelog

## Claude Code SDLC agents

- Add Claude Code subagents for each SDLC phase under `.claude/agents/` and an `/sdlc` orchestrator command under `.claude/skills/sdlc/`, reusing the existing phase skills and the guarded PR script.

## Automated PR creation

- Let the PR Preparation Agent commit, push, and open the pull request for an approved story through `scripts/pr/raise_pr.py`.
- Refuse to publish from a branch that is not the story's own, and from a `main` that is behind `origin/main`, so each story gets its own branch and PR.
- Gate publishing on `--approved`, a passing `mvn verify`, a complete PR body, and a secret scan; fall back to a pushed branch plus compare link when no GitHub credentials exist.

## US-102 dashboard capstone

- Replace the OpenAPI documentation generator with the Caseflow test management dashboard.
- Add Java 17 HTTP server and simulated asynchronous test runner.
- Add browser UI for case management, search/filter, run status, and execution reports.
- Store case and report data in local storage and use a demo-only login gate.
- Add Maven tests, GitHub Actions CI, and Copilot workflow helpers.
- Add an eight-phase Copilot SDLC pipeline with a coordinating orchestrator and phase-specific agents, prompts, and skills.
