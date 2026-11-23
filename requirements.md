# Requirements

## User story

**US-102: Create and Manage UI Test Cases Through a Dashboard**

As a QA Automation Engineer, I want a web-based dashboard to create, view, edit, delete, and execute UI automation test cases, so that I can manage test scenarios efficiently, monitor execution results, and identify failures without manually reviewing test logs.

## Scope decisions

- Implement a Java 17 web server and a browser dashboard using plain HTML, CSS, and JavaScript.
- Keep test cases, the demo login name, and execution reports in the browser's local storage.
- Use a simple demo login gate only; there are no real accounts, passwords, or server-side authentication.
- The Run Test action uses a server-side simulator that returns Pass or Fail after a short delay. It does not launch a browser or run Playwright/Selenium.
- Seed sample test cases when this browser has no saved cases.

## Functional requirements

### FR-1: View, search, and filter test cases

After entering the demo dashboard, show a table with test ID/name, module, priority, test status, and last result. Allow search by relevant test fields and filtering by module, priority, and status.

### FR-2: Create test cases

Allow a user to create a case with a unique ID, name, module, priority, steps, and expected result. Validate required values and reject duplicate IDs without losing the form data. Confirm successful creation.

### FR-3: Edit and delete test cases

Allow saved case details to be edited and shown in the list. Ask for confirmation before deleting a case. Keep existing execution history available after a case is deleted.

### FR-4: Execute test cases

Let a user run a saved case and immediately show In Progress, followed by Passed or Failed. Demo-only outcome selection makes both results demonstrable; the simulator does not execute the written steps.

### FR-5: View execution reports

Show report status, duration, timestamp, associated case, and failure details when a run fails. Persist reports locally in the browser.

## Non-functional requirements

- Use Java 17 and Maven, without a database or frontend framework.
- Escape user-entered values before rendering them as HTML.
- Limit request size and validate values at the Java runner endpoint.
- Keep browser storage local to the current browser profile; it is not shared or backed up.
- Show actionable errors for storage or runner failures.
- Keep demo authentication and simulated execution clearly labeled as non-production.

## Acceptance criteria

- **AC-01 — View test cases:** The dashboard lists test name, module, priority, status, and last result; search and filters work.
- **AC-02 — Create a test case:** Mandatory fields are validated, duplicate IDs are rejected, and successful saves are confirmed.
- **AC-03 — Edit/delete:** Edits appear in the dashboard and deletion requires confirmation.
- **AC-04 — Execute:** Running a saved case shows In Progress followed by Passed or Failed.
- **AC-05 — Reports:** Completed reports show status, duration, timestamp, and failure details when applicable.

## Out of scope

- Production authentication, roles, access control, and multi-user data.
- Running real browser automation or connecting to an external test framework.
- Server/database persistence, audit retention, or cross-device synchronization.

## US-103: Filter Test Reports by Status

### User story

As a QA engineer, I want to filter test reports by status so I can find failed runs quickly.

**Source:** User-provided story in Copilot chat. No JIRA, Confluence, or document link was provided.

### Context and confirmed decisions

- The reports page displays completed reports stored in browser local storage.
- Current report statuses are Passed and Failed.
- The status filter provides All, Passed, and Failed options, with All selected by default.
- The selected filter is transient and is not saved to browser storage; a full page reload returns it to All.

### Functional requirements

#### FR-6: Filter execution reports by status

Provide a labeled status filter on the reports page. Selecting All shows every report; selecting Passed or Failed shows only reports with that status. Filtering updates the displayed report rows without a page reload, preserves their existing order, and does not modify or delete stored reports. When no reports match the selected status, show an explicit no-matching-reports message.

### Non-functional requirements

- Apply filtering in the browser to the report data already loaded by the dashboard; no server or persistence changes are required.
- Keep the filter operable and understandable using the dashboard's existing form-control and empty-state patterns.
- Announce the updated visible-result count and no-match state to assistive technology through a polite live region without moving focus.

### Acceptance criteria

- **AC-06 — Filter reports by status:** The reports page offers All, Passed, and Failed; All is selected by default and shows all reports.
- **AC-07 — Show matching reports:** Selecting Passed or Failed immediately displays only reports with the selected status, preserving the existing report order and report-detail actions.
- **AC-08 — Preserve report data:** Changing or resetting the filter does not change or remove reports in browser storage; after a full page reload the filter defaults to All.
- **AC-09 — Empty filter result:** If no reports match a selected status, the reports page displays a clear no-matching-reports message.
- **AC-10 — Announce filter results:** A polite live region announces the visible-result count after a filter change and announces when no reports match; focus remains on the filter.
- **AC-11 — Handle invalid report data safely:** If the stored report value is valid JSON but not an array, the dashboard shows an actionable report-data error, does not crash, and does not overwrite or delete the stored value.

### Out of scope

- Filtering by date, case, module, or other report attributes.
- Persisting the selected filter across page reloads.
- Changing how reports are generated, stored, or retained.
- Automatically repairing or deleting structurally invalid report data.

## US-104: Export visible execution reports as CSV

### User story

As a QA engineer, I want to download the execution reports currently shown on the Reports page as a CSV file, so I can share test results with my team.

**Source:** User-provided story and acceptance criteria in this chat. No Jira, MCP, Confluence, or other external source was supplied or accessed. The final acceptance-criteria sentence was truncated in the chat message after “send report data to the”; its ending, “server.”, is carried forward from the immediately preceding assistant-provided story text and is recorded transparently here rather than treated as newly supplied text.

### Confirmed story details and project context

- The story's supplied criteria require an Export CSV action; export of exactly the currently visible reports in displayed order; respect for the All/Passed/Failed filter; the specified six columns and order; a UTF-8 headered CSV with commas, quotes, and line breaks escaped; the fixed filename `caseflow-reports.csv`; and a disabled action with an explanation when no reports are visible.
- The supplied column-value clarification is explicit: `Duration (ms)` is an integer number of milliseconds, and `Executed At` is the stored ISO-8601 timestamp, not either field's human-readable display formatting.
- The supplied final criterion intends export not to change saved reports or send report data to the server. As noted above, the words “server.” are restored from the immediately preceding assistant-provided story text because the user message was truncated.
- The existing Reports page has an All/Passed/Failed status filter; All is initially selected. Its rows follow the order of the report list, and filtering preserves that order (US-103).
- Existing report data includes case ID, test-case title, status, duration in milliseconds, execution timestamp, and failure details. The Reports page formats duration and timestamp for display, while the story requires the underlying integer duration and stored timestamp in the export.
- Existing report data is held in browser local storage. The new no-mutation/no-server-transfer constraints are part of this story and apply to the export operation.

### Functional requirements

#### FR-7: Export the visible execution reports

Provide an Export CSV action on the Reports page. Export exactly the reports currently visible under the selected status filter: All includes every report; Passed and Failed include only reports matching that status. Emit columns in this exact order and with these exact header labels: `Case ID`, `Test Case`, `Status`, `Duration (ms)`, `Executed At`, `Failure Details`. Include one header row, preserve the displayed report order, and escape fields containing commas, double quotes, or line breaks so the result is valid CSV. When no reports are visible, disable the action and explain why it is unavailable. Use the underlying integer-millisecond duration and stored ISO-8601 timestamp, rather than display-formatted values. Encode the CSV as UTF-8, name the download `caseflow-reports.csv`, and do not change saved reports or send report data to the server.

### Non-functional requirements

- The downloaded file must be UTF-8 encoded and parse as valid CSV, including correct handling of embedded commas, double quotes, and line breaks.
- The disabled state and its explanation must be perceivable and understandable to users.
- The export operation must be read-only with respect to saved reports and must not transmit report data to the server.

### Acceptance criteria

- **AC-12 — Export action:** The Reports page provides an Export CSV action.
- **AC-13 — Export the visible subset:** With All selected, the CSV contains every report; with Passed or Failed selected, it contains only reports of that status. The exported rows correspond to the reports visible on the page at the time of export.
- **AC-14 — CSV columns and values:** The first row contains exactly `Case ID`, `Test Case`, `Status`, `Duration (ms)`, `Executed At`, and `Failure Details`, in that order. Each data row places the corresponding report values under those columns; duration is an integer number of milliseconds and Executed At is the stored ISO-8601 timestamp, not display-formatted values.
- **AC-15 — Header and order:** The CSV includes one header row, and data rows retain the same order as the visible report rows.
- **AC-16 — UTF-8 CSV escaping:** The downloaded CSV is UTF-8 encoded. A CSV reader recovers the original field values when fields contain commas, double quotes, or line breaks.
- **AC-17 — No visible reports:** When the current filter yields no visible reports, Export CSV is disabled and the page explains that there are no visible reports to export. This applies both when there are no reports and when the selected status has no matches.
- **AC-18 — Filename:** The downloaded file is named exactly `caseflow-reports.csv`.
- **AC-19 — Read-only local export:** Exporting leaves saved reports unchanged and does not send report data to the server.

### Assumptions and unresolved questions

- No additional assumptions or behavior questions remain from the supplied story. The sole reconstructed wording is the truncated final sentence's “server.” ending, explicitly sourced from the immediately preceding assistant-provided story text above.

### Out of scope

- Adding or changing report fields, report generation, retention, or persistence.
- Exporting reports that are not currently visible under the selected status filter.
- Changing report values or their display formatting as part of this export story.

## DOCSYNC-1: Generate and check the API reference from OpenAPI

### User story

As a repository maintainer, I want the API reference generated from the OpenAPI definition and checked for drift, so that the documentation stays accurate as the API changes.

**Source:** Demo story and acceptance criteria pasted directly in chat. No Jira, MCP, or other external source was retrieved.

**Context:** This is a separate story from US-102 through US-104. The repository inspection found no OpenAPI definition or existing API-reference file in the `docs/` or `automated-api-documentation-sync/` directories; the current CI workflow runs `mvn --batch-mode verify`. The intended OpenAPI source path, generated reference path, and CI invocation are not yet confirmed.

### Functional requirements

#### FR-8: Generate the API reference

Given a valid OpenAPI definition, generate or update a clearly identified API reference that includes every endpoint's path, HTTP method, and summary.

#### FR-9: Check the generated reference for drift

Provide a check that detects when the existing API reference differs from what would be generated from the current OpenAPI definition. When drift is detected, report that the reference is stale and explain how to regenerate it.

#### FR-10: Preserve repository files and handle invalid input

The drift check must be read-only: it must not modify files or commit or push changes. Missing or invalid OpenAPI input must produce an actionable error and must not overwrite an existing API reference. Updating the generated reference must preserve other documentation.

#### FR-11: Cover required behavior with tests

Tests must cover successful generation, deterministic unchanged output, detection of stale documentation, and missing or invalid OpenAPI input.

### Non-functional requirements and constraints

- For unchanged OpenAPI input, repeated generation must produce byte-for-byte identical output.
- Drift checking must not change any repository files, including the generated reference.
- Generation or validation errors must be actionable and non-destructive to an existing reference.
- A reference update must not remove or alter unrelated documentation.

### Acceptance criteria

- **DOCSYNC-AC-01 — Generate endpoint reference:** With a valid OpenAPI definition, generation creates or updates a clearly identified API reference containing each defined endpoint's path, HTTP method, and summary.
- **DOCSYNC-AC-02 — Deterministic output:** Running generation at least twice with unchanged input produces byte-for-byte identical output.
- **DOCSYNC-AC-03 — Stale check guidance:** When the checked-in reference does not match the output for the current definition, the check reports that it is stale and states how to regenerate it.
- **DOCSYNC-AC-04 — Read-only check:** Running the drift check makes no file modifications and performs no commit or push.
- **DOCSYNC-AC-05 — Safe input errors:** If the OpenAPI definition is missing or invalid, the command/check reports an actionable error and leaves any existing API reference unchanged.
- **DOCSYNC-AC-06 — Preserve other documentation:** Updating the generated reference does not alter or remove documentation outside that generated reference.
- **DOCSYNC-AC-07 — Required test coverage:** The test suite covers successful generation, byte-for-byte unchanged output for unchanged input, stale-reference detection, and missing and invalid OpenAPI input.

### Duplicate-criteria handling

The pasted acceptance criteria contained duplicates and restarted numbering. Exact duplicate statements were consolidated into the seven unique criteria above and assigned stable `DOCSYNC-AC-01` through `DOCSYNC-AC-07` identifiers. No distinct criterion has been intentionally dropped.

### Proposed assumptions — not confirmed

- “Stale” means the current generated reference differs from the checked-in reference when compared against the same OpenAPI input.
- The generated API reference is a repository file. Its format and exact location remain undecided.
- The drift check is expected to be usable in CI, but how it is invoked and whether/how it is integrated into the existing workflow remain undecided.

### Open questions for the maintainer

1. What is the authoritative OpenAPI definition path (and, if relevant, which definition/version should be used)?
2. Where should the generated API reference live, and is a specific output format (for example, Markdown) required?
3. How should CI invoke the drift check: should it be added to the existing GitHub Actions workflow, and if so, which command should that workflow run?

### Out of scope

- Changing API behavior or creating/changing the OpenAPI definition itself.
- Adding endpoint details beyond path, HTTP method, and summary unless separately requested.
- Automatically committing or pushing generated documentation.
- Modifying or regenerating unrelated documentation.

### Requirements-phase status

Draft only. The story is documented, but source/output locations and CI invocation are unresolved. Human answers and explicit approval are required before handing this story to architecture.

## Dashboard run statistics endpoint

### User story

As a QA Automation Engineer, I want a `GET /api/stats` endpoint that returns the number of test runs the server has started, so that I can quickly see how many runs are in progress, passed, or failed without opening the dashboard.

**Source:** The story and acceptance criteria were supplied directly in chat. No Jira, MCP, Confluence, or other external source was supplied or accessed.

### Confirmed context and decisions

- The existing server lifecycle creates runs through `POST /api/runs` and tracks them through completion with In Progress, Passed, or Failed states.
- The new endpoint is a server-side reporting API; it does not introduce browser UI or browser-local-storage behavior.
- A fresh server process has no started run history and therefore reports all counts as zero.
- The inspected project context indicates that the existing run records are in memory. No new persistence or cross-restart behavior is requested.
- Counts describe the server's own run state: starting a run adds to `inProgress`, and completing a run moves that run from `inProgress` to `passed` or `failed`.

### Functional requirements

#### STATS-FR-1: Return current server run counts

Handle `GET /api/stats` and return HTTP `200` with a JSON object containing exactly these counters: `totalRuns`, `inProgress`, `passed`, and `failed`. The values must be non-negative integers representing the run-count states known to the current server process.

The successful response shape is:

```json
{"totalRuns":N,"inProgress":N,"passed":N,"failed":N}
```

#### STATS-FR-2: Initialize counts on a fresh server

After a server starts with no runs started, `GET /api/stats` must return `totalRuns:0`, `inProgress:0`, `passed:0`, and `failed:0`.

#### STATS-FR-3: Update counts from the existing run lifecycle

When `POST /api/runs` starts a run, increment `totalRuns` and `inProgress`. When that run completes as Passed, decrement `inProgress` and increment `passed`. When that run completes as Failed, decrement `inProgress` and increment `failed`. Count updates must not require changes to the existing `POST /api/runs` request or response behavior.

For every response, the invariant `totalRuns == inProgress + passed + failed` must hold.

#### STATS-FR-4: Reject non-GET methods consistently

For `POST`, `HEAD`, `PUT`, `DELETE`, `PATCH`, or any other non-GET method to `/api/stats`, return HTTP `405`, include `Allow: GET`, and do not alter any run counts.

#### STATS-FR-5: Keep the endpoint backend-only

The endpoint must not add or modify browser UI, browser local storage, or `POST /api/runs` behavior. It is not a browser data source and does not change run creation or completion behavior.

#### STATS-FR-6: Document the endpoint

Document `GET /api/stats`, its JSON response shape, and its run-state meaning in `README.md`. Document the endpoint in `CHANGELOG.md`.

### Non-functional requirements

- Use the existing Java 17 and JDK HTTP-server conventions; no new storage, framework, or external service is required.
- Return valid JSON with the four required fields and integer counts.
- Count operations must remain consistent when runs are started or complete during concurrent HTTP requests.
- The endpoint must not expose run details beyond the four aggregate counters.
- The implementation must preserve the existing behavior of health, static assets, run start, and run lookup endpoints.

### Acceptance criteria

- **STATS-AC-01 — Fresh server state:** Immediately after a server starts with no runs started, `GET /api/stats` returns HTTP `200`, valid JSON, and `{ "totalRuns": 0, "inProgress": 0, "passed": 0, "failed": 0 }` (semantic JSON values; whitespace is irrelevant).
- **STATS-AC-02 — Passed run:** After a run is started through the existing `POST /api/runs` and that run completes as Passed, `GET /api/stats` returns `inProgress:0`, `passed:1`, `totalRuns:1`, and `failed:0` for a server with no prior runs.
- **STATS-AC-03 — Failed run:** After a run is started through the existing `POST /api/runs` and that run completes as Failed, `GET /api/stats` returns `inProgress:0`, `failed:1`, `totalRuns:1`, and `passed:0` for a server with no prior runs.
- **STATS-AC-04 — In-progress run:** While a started run is still in progress and before completion, `GET /api/stats` returns `totalRuns:1`, `inProgress:1`, `passed:0`, and `failed:0`.
- **STATS-AC-05 — Count invariant:** After any mix of started, passed, and failed runs, the returned `totalRuns` equals `inProgress + passed + failed`.
- **STATS-AC-06 — 405 method handling:** A non-GET request to `/api/stats` returns HTTP `405` and an `Allow: GET` response header; the run counters remain unchanged.
- **STATS-AC-07 — JUnit coverage:** JUnit tests cover the empty state, at least one Passed completion, at least one Failed completion, an in-progress run, and the 405/`Allow: GET` case.
- **STATS-AC-08 — Build verification:** `mvn verify` passes with the stats implementation and tests included.
- **STATS-AC-09 — Documentation:** `README.md` and `CHANGELOG.md` each contain documentation of `GET /api/stats`, and README documentation identifies the response fields and state meaning.
- **STATS-AC-10 — Existing behavior and scope:** The implementation does not change browser assets, browser local storage, or existing `POST /api/runs` behavior.

### Assumptions

- `passed` and `failed` count server-known run completions, not browser-local report counts or case-level latest results.
- Counts cover the lifetime of the current server process and reset when a fresh server process starts; no persistence, replication, or cross-server aggregation is requested.
- The existing run IDs and lifecycle remain unchanged; this endpoint reads aggregate state rather than run records.

### Open questions

- None. The story fixes the route, response contract, fresh state, lifecycle count transitions and invariant, 405 behavior, backend-only boundary, tests, build check, and documentation requirements.

### Out of scope

- Browser dashboard changes or additions for displaying run statistics.
- Browser local-storage changes.
- Adding fields or endpoints beyond `GET /api/stats`.
- Changing run creation, run lookup, run timing, outcomes, or `POST /api/runs` request/response behavior.
- Database, cache, persistence, replication, or cross-restart/cross-server run aggregation.
- Authentication, authorization, role enforcement, or exposing individual run details.
- Real browser automation or changes to the existing simulated runner.

### Requirements-phase status

**Approved by human.** The `GET /api/stats` requirements and STATS-FR/STATS-AC-01–10 are approved for use as the stats story source of truth. Prior human approval is recorded from chat authorization; no separate approver name or external evidence is asserted.
