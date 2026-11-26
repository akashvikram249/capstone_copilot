# Changelog

## SDLC hardening

- Check each phase's output against a stage check and retry the phase up to twice before a gate opens; stop and ask the user after the last failure.
- Label every pull request raised by `scripts/pr/raise_pr.py` as `ai-generated`; exit with code 4 if the PR exists but the label could not be applied.
- Reword the phase skills in plainer language without changing their steps.
- Let `/sdlc` and the SDLC Orchestrator read a story from a `.txt`, `.md` or `.docx` file through `scripts/story/read_story.py`.

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
