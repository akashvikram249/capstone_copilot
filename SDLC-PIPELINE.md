# Agentic SDLC Pipeline

This workspace packages the full eight-phase SDLC as Copilot custom agents, prompts, and skills. Claude Code and CodeMie use the same skills and this guide, so the workflow is defined once. Start with **SDLC Orchestrator** for a guided cycle, or invoke a phase agent/prompt/skill directly for one stage.

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

## Provide the story from a file

Put the story in a `.txt`, `.md` or `.docx` file (for example `stories/US-107.docx`) with the story ID on the first line, a role/goal/benefit sentence, and numbered acceptance criteria. Word tables become `a | b` rows; images are not read.

- **Claude Code:** `/sdlc stories/US-107.docx`
- **Copilot:** tell SDLC Orchestrator "The story is in stories/US-107.docx"
- **CodeMie:** it cannot read your disk. Run `python3 scripts/story/read_story.py stories/US-107.docx --copy` and paste the clipboard into the chat.

`scripts/story/read_story.py` has no dependencies and rejects missing files and unsupported types (`.pdf`, `.doc`) with a clear message. The agent shows the first lines it read so a bad conversion is caught, and records the file path as the story source.

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

## Retry after every stage

The orchestrator (the Copilot agent or the Claude `/sdlc` skill) checks each phase's output before it shows it to you or opens a gate:

| # | Stage check |
|---:|---|
| 1 | `requirements.md` has a section for this story with numbered acceptance criteria and a list of open questions (which may be empty) |
| 2 | `architecture.md` gives every acceptance criterion a path through the design |
| 3 | `design-review.md` has ranked findings and the decisions to take |
| 4 | `impl-plan.md` gives every task a test approach and marks any blockers |
| 5 | The tests it ran passed, and it reports the command and the real result |
| 6 | The review lists findings with file, line and severity, or says what was checked and found nothing |
| 7 | Every acceptance criterion has a command or observation behind it, and failures are listed |
| 8 | `raise_pr.py` printed `PR_URL=` and `PR_LABEL=ai-generated`, or the reason it didn't |

If a check fails because the specialist errored, called itself blocked on something it could fix, or left the artifact incomplete, the orchestrator calls it again with the exact failure. Each stage gets two retries (three attempts in all), and you're told about each one. If the last attempt fails, the pipeline stops and asks whether to try again, skip the stage, or abort.

Some failures are not retried, because a second attempt would give the same result: a decision only you can make, a refusal by `raise_pr.py` (failed `mvn verify`, secret scan, not approved, local `main` behind `origin/main`), and exit code 3 (no GitHub credentials). A change you ask for at a gate is a revision and doesn't use up a retry.

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
5. Prints `PR_URL=<url>` and labels the PR `ai-generated` (creating the label if the repository doesn't have it yet), then prints `PR_LABEL=ai-generated`. An already-open PR gets the label too. If the label can't be applied, the PR still exists, the script prints `PR_LABEL_MISSING` and exits with code 4, and the agent must report it so the label can be added by hand. If neither credential exists, the branch is still pushed, it exits with code 3, and prints a prefilled compare link; the PR is **not** created and the agent must say so.

`--dry-run` shows the branch, pending changes, the label, and which PR route is available without changing anything. One-time setup for fully automatic PRs: install and sign in to `gh` (`gh auth login`) or export a `GITHUB_TOKEN` with pull-request write access. Test the script with `python3 -m unittest scripts/pr/test_raise_pr.py`.

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
