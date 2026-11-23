# Caseflow — UI Test Case Management Dashboard

A Java 17 capstone demo for managing UI test cases and viewing execution results.

## What it does

- Shows test cases by name, module, priority, status, and last result.
- Searches cases and filters by module, priority, and status.
- Creates and edits test cases with required-field validation and unique IDs.
- Confirms before deletion and keeps existing run reports.
- Simulates asynchronous test runs that finish Passed or Failed.
- Stores cases and reports in browser local storage.
- Shows reports with status, duration, execution time, and simulated failure details.
- Filters report history by All, Passed, or Failed in the current page; the filter is not saved.

## Important demo limitations

- The sign-in screen is a demo gate, not real authentication. Any non-empty name works.
- The runner is simulated. It does not launch a browser or run Selenium/Playwright tests.
- Cases and reports live only in the current browser profile. Clearing browser data removes them.
- Structurally invalid saved report data is reported without automatic repair or deletion.
- Selecting Pass/Fail is only for demonstrating the two report outcomes.

## Requirements

- Java 17
- Maven 3.8+

## Run locally

```sh
mvn test
mvn exec:java
```

Open [http://localhost:8080](http://localhost:8080), enter any display name, and start exploring. Override the port with `mvn exec:java -Dexec.args="8090"` or set `PORT`.

## Test

```sh
mvn test
```

The tests cover execution state transitions, server endpoints, validation errors, missing runs, and static page delivery. GitHub Actions runs `mvn verify` for pushes to `main` and pull requests.

## Run statistics

`GET /api/stats` returns process-local aggregate counts for runs on the current server:

- `totalRuns`: runs admitted by `POST /api/runs`
- `inProgress`: admitted runs that have not reached a terminal state
- `passed`: runs that completed as Passed
- `failed`: runs that completed as Failed

The endpoint returns HTTP `200` with exactly these four integer fields. Counts reset when the server process restarts and are not persisted or browser-local. Unsupported methods return HTTP `405` with `Allow: GET`.

## Project guide

- [requirements.md](requirements.md) — user story and acceptance criteria
- [architecture.md](architecture.md) — components, data flow, API, and scope boundaries
- [design-review.md](design-review.md) — reviewed decisions and limitations
- [impl-plan.md](impl-plan.md) — dependency-ordered delivery plan
- [SDLC-PIPELINE.md](SDLC-PIPELINE.md) — guided eight-phase Copilot SDLC cycle and approval gates
- [CHANGELOG.md](CHANGELOG.md) — project changes
- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md) — PR description and reviewer checklist

## Copilot helpers

Select **SDLC Orchestrator** in Copilot Chat to guide work from a user story through PR preparation. The orchestrator delegates each phase to its own specialist agent, prompt, and skill:

1. Requirements
2. Architecture
3. Design review
4. Implementation planning
5. Implementation
6. Code review
7. Verification
8. PR preparation

The orchestrator pauses at human approval gates. It does not commit, push, deploy, or open a PR without your explicit approval. See [SDLC-PIPELINE.md](SDLC-PIPELINE.md) for phase details and direct invocation instructions. The separate Dashboard Reviewer is a read-only reviewer for US-102-specific dashboard changes.

Two workspace hooks are configured in [.github/hooks/hooks.json](.github/hooks/hooks.json): SessionStart prints concise SDLC/repository context; PostToolUse runs Maven tests when the pending Java/dashboard source snapshot changes. The test hook runs Maven and may take a little time; repeated tool calls with the same source snapshot are skipped.
