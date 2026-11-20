# Agentic SDLC Pipeline

This workspace packages the full eight-phase SDLC as Copilot custom agents, prompts, and skills. Start with **SDLC Orchestrator** for a guided cycle, or invoke a phase agent/prompt/skill directly for one stage.

## Run in Claude Code

The same eight phases are available as Claude Code subagents (`.claude/agents/sdlc-*.md`) driven by the `/sdlc` command (`.claude/skills/sdlc/SKILL.md`). Each subagent follows the matching skill in `.github/skills/`, so the workflow is defined once.

```bash
cd <path-to-this-repo>
git switch main && git pull        # every story starts from an up-to-date main
claude
```

Then, inside Claude Code, run `/sdlc` followed by the story text (or a path to a file containing it). Claude pauses for your approval at each gate; the last gate asks "Accept this verification and authorize raising the PR?". Start a new Claude Code session after pulling agent changes so they load.

## Run a guided cycle (Copilot)

1. Open Copilot Chat and select **SDLC Orchestrator**.
2. Provide a user story or point to its source. For this capstone, the current story is [US-102 in requirements.md](requirements.md).
3. The orchestrator works through the phases below in order. It loads the matching skill and prompt for each phase, invokes that phase's specialist agent, and summarizes the outcome.
4. Review and approve requirements before architecture, architecture before implementation, and implementation before verification/PR preparation. The orchestrator must pause for your decision at these gates.
5. To pause or resume, ask it to stop at a phase boundary or continue from the last approved phase. It should inspect the repository and existing artifacts rather than assume the cycle state.

Agents can draft and edit repository artifacts. **Nothing is committed, pushed, deployed, or opened as a pull request without your explicit approval.** That approval is given once, at the final gate (accepting verification and authorizing the PR). After it, the PR Preparation Agent raises the pull request itself with no further prompts; see [Raising the PR](#raising-the-pr).

## Phases

| # | Phase | Agent | Main artifact / outcome |
|---:|---|---|---|
| 1 | Requirements | Requirements Agent | `requirements.md` — clarified functional and non-functional requirements and acceptance criteria |
| 2 | Architecture | Architecture Agent | `architecture.md` — system components, data flow, technology choices, boundaries |
| 3 | Design review | Design Review Agent | `design-review.md` and agreed architecture updates |
| 4 | Implementation planning | Planning Agent | `impl-plan.md` — prioritized, dependency-ordered tasks and blockers |
| 5 | Implementation | Implementation Agent | Code, focused tests, and directly related documentation |
| 6 | Review | Code Review Agent | Structured findings against the acceptance criteria and review checklist |
| 7 | Verification | Verification Agent | Test/build/quality evidence and output-document checks |
| 8 | PR preparation and publishing | PR Preparation Agent | Changelog entry, PR description with test evidence, limitations, and checklist, and the opened pull request |

Every phase has three matching files:

- Agent: `.github/agents/<phase>.agent.md`
- Prompt: `.github/prompts/<phase>.prompt.md`
- Skill: `.github/skills/<phase>/SKILL.md`

The agent defines the role and boundaries; the prompt is a reusable task starter; the skill defines the repeatable step-by-step workflow. Specialists link to their matching prompt and skill so that using a phase agent includes both.

## Human approval gates

- **After requirements:** confirm assumptions, acceptance criteria, and scope.
- **After design review:** approve architecture and identified trade-offs before implementation.
- **After review and verification:** decide whether findings are fixed and checks are sufficient.
- **Final gate (after verification):** accept the verification evidence and authorize the PR. This single approval covers the commit, push, and PR for that story. Deployment is never covered.

The pipeline records useful evidence in repository documents. It does not claim a phase is complete when required input, approval, or verification is missing; it records that phase as blocked and explains why.

## Raising the PR

The last agent publishes through one script, `scripts/pr/raise_pr.py`, rather than ad-hoc git commands:

```bash
python3 scripts/pr/raise_pr.py --story US-103 --title "Add bulk delete" --body-file target/pr-body.md --approved
```

What it does, in order:

1. Refuses without `--approved`, if the PR body lacks any of the five template sections, or if there is nothing to publish.
2. Runs `mvn --batch-mode verify`; a failure stops everything.
3. Creates `story/<id>-<slug>` from the base branch (never publishes from `main`), stages changes, and blocks the commit if it finds credential-like files or secret patterns. Start every new story from an up-to-date `main` (`git switch main && git pull`): the script refuses if local `main` is behind `origin/main`, and refuses to run from any other branch than that story's own `story/<id>-...` branch unless you pass `--branch`, so a new story can never land on an earlier story's branch or PR.
4. Commits as `<story>: <title>`, pushes with `-u` (never force), and opens the PR using, in order: an authenticated `gh` CLI, then `GITHUB_TOKEN`/`GH_TOKEN` via the GitHub API. An already-open PR for the branch is returned instead of duplicated.
5. Prints `PR_URL=<url>`. If neither credential exists, the branch is still pushed, it exits with code 3, and prints a prefilled compare link; the PR is **not** created and the agent must say so.

`--dry-run` shows the branch, pending changes, and which PR route is available without changing anything. One-time setup for fully automatic PRs: install and sign in to `gh` (`gh auth login`) or export a `GITHUB_TOKEN` with pull-request write access. Test the script with `python3 -m unittest scripts/pr/test_raise_pr.py`.

## Useful commands

- Run the dashboard tests: `mvn test`
- Build and run all CI verification: `mvn --batch-mode verify`
- Start the dashboard: `mvn exec:java`

## Scope boundary

This workflow guides agent-assisted work in this repository; it does not implement a production SDLC platform, Jira/Confluence connector, autonomous deployment, or real authentication. The existing dashboard's demo limitations remain as stated in [README.md](README.md).

## Lifecycle hooks

Two workspace hooks are configured in `.github/hooks/hooks.json`:

- **SessionStart** runs `scripts/hooks/session_start.py`. It prints the repository, branch, whether pre-existing changes are present, the pipeline guide, and the approval/publishing reminders.
- **PostToolUse** runs `scripts/hooks/post_tool_use.py`. When pending changes include Java source, Java tests, dashboard assets, or `pom.xml`, it runs `mvn --batch-mode test`. It records the tested source snapshot in the system temporary directory so unrelated tool calls do not rerun the same test set. A changed source snapshot triggers a new run; test failure is reported with a non-zero hook exit code.

The test hook can take a couple of minutes and runs after Copilot tool actions, not only after file edits. When there are no relevant pending source changes, or the same source snapshot was already tested, it exits quietly.
