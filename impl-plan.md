# Implementation Plan

| Priority | Task | Dependencies | Status |
|---:|---|---|---|
| 1 | Capture US-102 scope, behavior, and demo boundaries in requirements. | None | Complete |
| 2 | Approve the Java server, browser storage, runner API, and security limits. | 1 | Complete |
| 3 | Implement Java HTTP server and simulated asynchronous execution service. | 2 | Complete |
| 4 | Implement dashboard login gate, case CRUD, search/filter, and browser persistence. | 2 | Complete |
| 5 | Implement execution polling, status indicators, and report history. | 3, 4 | Complete |
| 6 | Add tests, CI workflow, Copilot customizations, documentation, and PR template. | 3, 4, 5 | Complete |
| 7 | Run Maven tests, start server, and verify UI/API behavior against AC-01–AC-05. | 6 | Complete |

## Blocked work

Production authentication, database persistence, and real browser automation are outside the approved demo scope.

## US-103 — Filter test reports by status

The tasks below cover approved AC-06–AC-11 and the accepted design-review decisions. They change only the existing browser report view; they do not add server behavior, persistence, or test tooling. The user approved this plan, authorizing Phase 5 implementation. Browser acceptance remains a manual check because the repository has no browser test harness.

| Priority | Task | Actual prerequisites | Completion criteria and focused verification | Status |
|---:|---|---|---|---|
| 1 | Guard report loading and rendering against valid-JSON, non-array stored values; show an actionable report-data error while leaving the stored value untouched. Ensure report-dependent rendering does not invoke array methods on invalid data. | None | In a browser, store valid JSON such as `null` or an object under the report-storage key, then load the dashboard. The dashboard does not crash, the reports view identifies the report-data problem and gives an actionable next step, and the original stored value remains byte-for-byte unchanged. | Complete — malformed shape displayed an error; stored value preserved |
| 2 | Add a visibly labeled native All/Passed/Failed status control to the reports page, with All selected by default and the selection kept only in the current page state. Reuse existing control styling. | None | Confirm the label is associated with the control, all three choices are available, All is initially selected, keyboard operation works, and changing the control does not write the selected value to browser storage. | Complete — label/options/default, keyboard selection, and reload reset checked |
| 3 | Connect the status control to an in-memory report projection and render its results. Preserve original ordering and report-detail actions, do not mutate or persist/delete the source reports, and distinguish the no-reports-yet state from an explicit no-matching-reports state. | 1, 2 | With report fixtures in browser storage, verify All shows every report and Passed/Failed show only matching rows in original relative order; report detail still opens by report ID; an unmatched selection shows a clear no-matching-reports message; changing back to All restores rows; stored reports remain unchanged. | Complete — filters, order, details, empty states, reload, and storage preservation checked |
| 4 | Add/update the polite live region for filter-result announcements without moving focus. | 3 | Change the filter and verify assistive technology is informed of the visible-result count or the no-match state; keyboard focus remains on the status control. Confirm the announcement reflects the rendered projection. | Complete — polite live-region attributes/text and retained focus checked; screen-reader speech not independently tested |
| 5 | Perform focused manual browser acceptance verification for AC-06–AC-11; record the outcomes against this checklist without introducing browser-test tooling. | 1, 2, 3, 4 | Checklist: (a) All is the initial selection and shows every report; (b) Passed and Failed update immediately, retain relative order, and keep detail actions working; (c) empty report storage retains the existing no-reports message and a nonmatching status shows a distinct no-match message; (d) filter changes leave report storage unchanged and a full reload resets to All; (e) polite count/no-match announcements occur without focus movement; (f) valid-JSON non-array report storage produces the actionable error without a crash or storage modification. Record pass/fail and any observed issue for every item. | Complete — integrated-browser checks passed; temporary fixtures/session cleared |
| 6 | Run the existing Maven test suite as regression verification; add no tests or dependencies for this feature. | 1, 2, 3, 4 | `mvn test` completes successfully; capture the command outcome and any failures for review. | Complete — `mvn test`: 7 tests passed, 0 failures/errors/skips |
| 7 | Review the completed US-103 changes against requirements, approved architecture, design-review decisions, and repository conventions. | 1, 2, 3, 4 | Review confirms AC-06–AC-11 coverage, safe escaped report rendering, non-destructive local-storage handling, no persistence/API changes, accessible announcements, and no unrelated edits; resolve or explicitly report findings. | Complete — checklist review completed; the report-storage failure finding was fixed and rechecked |
| 8 | Complete final verification and report readiness for human acceptance. | 5, 6, 7 | Confirm manual and automated evidence is recorded, review findings are resolved or clearly listed, and report readiness accurately describes remaining limitations and approval gates. | Complete — Maven verification, JavaScript syntax, and targeted browser checks passed |

### US-103 blockers

- The user-approved plan authorizes Phase 5 implementation; no additional design or tooling blocker is identified for the approved scope.
- Manual browser acceptance covered report-status subsets and order, report details, empty states, storage preservation, reload default, live-region attributes/text, focus retention, invalid-data handling, and keyboard letter selection. A targeted storage-write failure check also confirmed the report remains out of in-memory state, local storage is unchanged, and the storage error is shown.
- Latest verification: `mvn --batch-mode verify` passed (7 tests, 0 failures/errors/skips); `node --check src/main/resources/static/app.js` passed. Actual screen-reader speech was not independently tested.
- Dependency inventory found only test-scope JUnit dependencies; no automated CVE scan was run. See the implementation review in `design-review.md`.
- The story source is the user's Copilot chat message; no external JIRA, Confluence, or document source was supplied. No commit, push, deployment, or PR was authorized.

## US-104 — Export visible execution reports as CSV

This plan covers approved US-104 requirements AC-12–AC-19 and the approved design-review recommendations in `design-review.md`. The source of truth remains the user-provided chat story recorded in `requirements.md`; no Jira/MCP retrieval is claimed. Preserve exact exported values and the accepted spreadsheet formula-interpretation risk: do not add neutralization or warnings that alter the approved fidelity contract. Keep Java 17, plain HTML/CSS/JavaScript, browser-local reports, no new runtime/build dependency, and no browser-test harness.

### Actual current state

Source inspection of `app.js`, `index.html`, and `styles.css` shows partial US-104 implementation evidence already present:

- `getVisibleReports()` is used by both `renderReports()` and `exportVisibleReports()` for All/Passed/Failed.
- `serializeReportsCsv()` emits the six approved headers and maps raw `durationMs` and stored `timestamp`; special-field quoting is implemented.
- `index.html` contains an Export CSV button associated with visible help text.
- `renderReports()` disables export for both an empty report list and a no-match filter; invalid report data has a separate disabled/error state.
- Export uses a UTF-8 `text/csv` Blob, exact filename, temporary link/object URL, deferred cleanup, and a synchronous-error toast.
- Existing `impl-plan.md` records Node-mocked checks and `mvn test` evidence, but the repository has no browser harness and no actual integrated-browser download result is recorded.

This source evidence is implementation status, not browser acceptance evidence. Existing reported Node/JUnit outcomes must not be represented as end-to-end CSV verification.

| Priority | Task | Actual prerequisites | Completion criteria and focused verification | Status |
|---:|---|---|---|---|
| 1 | Baseline the partial US-104 implementation against the approved source, and leave each remaining task scoped to a specific source defect or evidence gap. Do not redesign US-103 behavior or add server/API/report persistence. | Approved `requirements.md`, `architecture.md`, and `design-review.md`; current `app.js`, `index.html`, `styles.css`, and report tests. | Review record identifies the actual implemented/partial/pending portions in source and separates source inspection, mocked checks, Maven checks, and browser checks. No unrelated US-102/US-103 behavior is changed. | Complete — source and artifact baseline recorded above |
| 2 | Inspect and, if needed, correct the shared visible-report projection and export control integration. Preserve report order, detail actions, US-103 empty states, invalid-data handling, transient filter state, and read-only report/storage behavior. | Task 1. | Browser-independent source review confirms `getVisibleReports()` supplies both table and export, and invalid data is never converted to an exportable empty projection. If a correction is needed, it has a narrow diff and reuses existing rendering patterns. | Partially implemented — source already uses the shared projection and separate invalid state; browser behavior remains unverified |
| 3 | Inspect and, if needed, correct the CSV serializer and download lifecycle. Keep exactly the six headers and field mapping, raw duration/timestamp values, CSV CR/LF quoting, UTF-8 Blob, exact filename, and exceptional/deferred cleanup. | Task 2 — export consumes the ordered projection. | A focused mock/reader or browser check demonstrates exact headers, row order, escaping, raw values, filename, cleanup, unchanged report state, and no storage/network mutation. The implementation does not transform formula-like values. | Partially implemented — source contains the serializer/lifecycle; actual round-trip/browser behavior is pending |
| 4 | Add/update focused JUnit static-asset coverage only where it adds real regression value; do not add a JavaScript/browser harness or CSV dependency. The existing Maven server test is the appropriate boundary for verifying that the served dashboard assets expose the approved control and keep static delivery working. | Task 2 and 3; no browser dependency. | `DashboardServerTest` (or a similarly scoped existing test) fetches `/` and `/app.js` and asserts presence of the Export control wiring and key US-104 constants/functions. No test claims to execute CSV behavior in JavaScript. `mvn test` passes. | Not started |
| 5 | Update README documentation directly related to US-104. | Task 2 and 3; verified or explicitly dispositioned implementation state. | README states that the Reports page can export the currently visible All/Passed/Failed rows to `caseflow-reports.csv`, that filtering/export remain browser-local and read-only, and that browser automation is not included. Wording does not claim browser acceptance or formula protection. | Not started |
| 6 | Update CHANGELOG with a concise US-104 entry. | Task 2 and 3; documentation text. | CHANGELOG records the CSV export, visible-filter subset, exact fixed filename, and browser-only/read-only limitation; no unsupported delivery or test claim. | Not started |
| 7 | Run the existing Maven regression suite after source/test/documentation changes. | Tasks 2–6 for final source state; Task 4 for JUnit additions. | `mvn test` or `mvn --batch-mode verify` completes as recorded; capture pass/fail counts and command. A passing Maven run remains no substitute for browser CSV acceptance. | Maven test has been run once in existing evidence: 7 tests passed, 0 failures/errors/skips; rerun is required after final changes |
| 8 | Conduct code review against US-104 requirements, architecture, design review, repository conventions, and the actual final diff. | Tasks 2–7; final source state. | Review disposition covers projection parity, exact schema/raw values, robust escaping, accessible disabled/invalid states, cleanup/error behavior, read-only/no-network behavior, no extra dependencies/tools, and formula risk. Findings have severity and are resolved or explicitly listed. | Not started |
| 9 | Complete focused manual browser acceptance using the checklist below. This remains a manual task; do not introduce automation unless separately approved. | Tasks 2–3 and the runnable dashboard. | Record actual pass/fail and observed issue for every AC item. Evidence must state browser/version and state fixtures used; do not claim download completion or acceptance unless observed. | Blocked on manual browser access / browser executable availability |
| 10 | Complete final verification and planning/status cleanup. | Tasks 4–9; review disposition. | `impl-plan.md` records accurate source status, Maven command evidence, browser evidence or explicit pending state, remaining limitations, and no unrecorded implementation claims. README/CHANGELOG and code-review findings are consistent. No commit, push, deployment, or PR is performed. | Not started |

### Manual browser acceptance checklist for US-104

| AC | Manual check |
|---|---|
| AC-12 | On the Reports page, locate and activate the visibly labeled Export CSV control. |
| AC-13 | With All, Passed, and Failed, verify the export contains exactly the currently displayed report rows and retains visible row order. |
| AC-14 | Parse the download and verify exactly six headers in the specified order and `durationMs`/stored `timestamp` rather than display formatting. |
| AC-15 | Verify one header record and data rows in table order. |
| AC-16 | Round-trip representative comma, quote, CR/LF, Unicode, empty, and combined-special-character values. |
| AC-17 | Verify disabled control plus visible explanation for no reports and no matching status; verify invalid report data remains a separate actionable error and is not exportable. |
| AC-18 | Verify the downloaded filename is exactly `caseflow-reports.csv`. |
| AC-19 | Verify export does not alter report storage/filter/table state or send report data by network; do not claim browser completion if only activation is observable. |

### US-104 blockers and limitations

- **Browser verification blocker:** no browser executable or browser automation tool is recorded as available in the repository workflow, and no integrated browser harness exists. Task 9 cannot be completed by Maven or Node-mocked checks alone.
- **No JUnit browser substitute:** JUnit may verify served static assets and wiring smoke, but it must not be described as CSV behavior verification. No JavaScript, CSV, or browser dependencies should be added.
- **Source/diff scope:** Source inspection shows partial US-104 implementation. A final code-review task must verify the exact final diff, findings, and no unrelated edits.
- **Residual risk:** formula-like text in a spreadsheet may be interpreted as formulas. The approved exact-value contract does not permit silent neutralization or a behavior-changing warning.
- **No implementation authorization yet:** requirements, architecture, and design review are approved, but this implementation plan is the approval gate for subsequent implementation activity. Do not implement, commit, push, deploy, or open a PR before separate approval.

## GET /api/stats — STATS (STATS-AC-01 through STATS-AC-10)

This plan adds the approved backend-only run-statistics endpoint to the existing Java/JDK server and in-memory `ExecutionService`. It does not modify browser assets, browser local storage, `POST /api/runs`, run records/details, persistence, or add any endpoint beyond `/api/stats`. The implementation must use the existing Java 17/JDK `HttpServer`, JUnit 5, and Maven conventions. Counts are process-local and reset with a fresh server process.

**Plan status:** **Approved by human for implementation.** The requirements, architecture, design-review outcome, and prior stats implementation plan were approved in chat; this current artifact records that prior plan approval for implementation authorization. The implementation tasks below are **Not started** because no stats implementation or test execution is evidenced in this planning task.

| Priority | Task | Actual prerequisites | Completion criteria and focused test approach | Status |
|---:|---|---|---|---|
| 1 | Establish the stats implementation baseline and verify no existing `/api/stats` route or four-counter state is present. | Approved `requirements.md`, `architecture.md`, and `design-review.md`; current Java sources and tests. | Source/test review records only the approved baseline, names the files to change, and confirms no browser/persistence/API scope drift. Inspection shows no stats implementation evidence requiring status to be marked complete or partial. | Not started |
| 2 | Add immutable stats state and a single synchronized lifecycle boundary to `ExecutionService`. Initialize `totalRuns`, `inProgress`, `passed`, and `failed` to zero. | Task 1. | The service holds the four counts with process-local lifetime and exposes a snapshot with exactly four fields that cannot be mutated by the caller. A lock or equivalent boundary covers admission, terminal status/count transitions, duplicate-completion checks, and snapshot reads. Test approach: JUnit asserts fresh zero state and the four counter invariant after mixed transitions. | Not started |
| 3 | Integrate run admission, scheduling, and counters without changing the successful `POST /api/runs` contract. | Task 2; existing `ExecutionService.start(...)` and scheduler behavior. | Starting an admitted run increments `totalRuns` and `inProgress` together. Scheduling completion and counters are synchronized so no run is left counted and unscheduled. If scheduler admission fails/shuts down, roll back the run and both admission counters and preserve existing POST behavior/error handling; do not count or schedule a partial admission. Normal POST 202 response/result remain unchanged. Test approach: JUnit/Maven tests cover in-progress counts, failed scheduling/rollback where practical, unchanged POST success shape, and invariant preservation. | Not started |
| 4 | Integrate one-terminal-state completion into the existing lifecycle. | Tasks 2 and 3. | Under the synchronized lifecycle boundary, update the run status and decrement `inProgress` while incrementing exactly `passed` or `failed`; a duplicate completion callback is ignored and can never count the run twice. Scheduler and HTTP/network work remain outside the critical section. Test approach: deterministic Passed/Failed JUnit tests cover before/after snapshots and a repeated completion call has no second effect. | Not started |
| 5 | Add an exact-match `GET /api/stats` route to `DashboardServer` before static fallback. | Tasks 2–4; existing JDK HTTP routing and JSON helpers. | GET returns 200 and a JSON object containing exactly `totalRuns`, `inProgress`, `passed`, and `failed`, with integer non-negative values and existing UTF-8 JSON/no-store conventions. `find`/POST behavior is unchanged. Test approach: HTTP JUnit starts a server and verifies exact field set, values, content type/status, and no extra fields. | Not started |
| 6 | Add the shared 405/`Allow: GET` method rejection for `/api/stats`. | Task 5. | POST, HEAD, PUT, DELETE, PATCH, and another method return 405 with `Allow: GET` and do not read or mutate counters or run state. The route uses existing JSON method-rejection conventions. Test approach: HTTP JUnit loops through rejected methods and verifies status/header/error shape and unchanged counters after each request. | Not started |
| 7 | Add focused JUnit service coverage for fresh, Passed, Failed, in-progress, invariant, and duplicate-completion behavior. | Tasks 2–4. | `ExecutionServiceTest` or a focused existing test class verifies zero state, Passed and Failed transitions, in-progress state, mixed-transition invariant, immutable snapshot, and duplicate-completion protection. Tests use existing Java 17/JUnit conventions and deterministic durations. | Not started |
| 8 | Add focused JUnit HTTP coverage for GET, 405/non-mutation, concurrent observation, and existing endpoint regressions. | Tasks 5–7. | `DashboardServerTest` verifies empty and lifecycle-driven JSON, exact field set, 405/`Allow`, rejected-method non-mutation, and unchanged run lookup/static/health behavior. A controlled concurrent start/completion/read test verifies no partial snapshots and invariant preservation where practical. Existing tests remain passing. No browser-test harness or new dependency is added. | Not started |
| 9 | Update README and CHANGELOG for the approved endpoint. | Tasks 5–6; implementation/API shape final. | README documents route, HTTP 200, exact four fields and state meaning, process-local lifetime/reset behavior, and no run-detail/browser/persistence semantics. CHANGELOG adds a concise endpoint entry. Documentation contains no unsupported persistence, UI, or delivery claim. Test approach: diff review plus text assertions if useful; no Maven verification run by planning. | Not started |
| 10 | Run the existing Maven regression and verification suite. | Tasks 2–9. | `mvn --batch-mode verify` is run only in Phase 5/implementation verification. The run passes with the stats implementation/tests included; capture command, pass/fail/error/skip counts and any failure. Planning itself does not claim or execute this step. | Not started |
| 11 | Review the final diff against STATS-AC-01–10 and repository conventions. | Tasks 2–10; implementation and verification evidence complete. | Review confirms synchronized lifecycle, immutable snapshot, duplicate-completion protection, scheduling-failure rollback/outcome, exact four-field JSON, 405/Allow, process-local semantics, Java 17/Maven/JUnit conventions, and no browser/assets/local-storage/POST/persistence scope drift. Resolve or explicitly record findings. | Not started |
| 12 | Complete final verification/status cleanup for human acceptance. | Tasks 9–11. | This plan records actual Maven evidence, JUnit coverage and passing/failing dispositions, code-review findings, README/CHANGELOG consistency, and remaining limitations. It also confirms no commit, push, deployment, PR, or product-code change was performed by planning. | Not started |

### STATS dependency summary

- Task 1 is a baseline review with no prerequisite.
- Tasks 2–4 establish service state and lifecycle transitions; Task 3 additionally depends on Task 2, and Task 4 additionally depends on Tasks 2 and 3.
- Task 5 depends on the service snapshot and lifecycle; Task 6 depends on the route.
- Tasks 7 and 8 add focused tests and depend on their corresponding service/HTTP work.
- Task 9 depends on the finalized route and lifecycle so documentation cannot disagree with implementation.
- Tasks 10–12 are final verification tasks and depend on implementation, tests, docs, and review evidence.

### STATS blockers

- No unresolved requirements or architecture decision blocks planning or, after this approval, implementation.
- A bounded implementation guardrail requires scheduler-failure handling to be completed without counted unscheduled runs and without changing normal POST behavior; this is covered by Task 3 and is not an external blocker.
- Browser/manual acceptance is not applicable to this backend-only story.
- No commit, push, deployment, or PR is authorized or planned.

### STATS scope and acceptance trace

| AC | Planned deliverable |
|---|---|
| STATS-AC-01 | Tasks 2 and 5: fresh zero snapshot and HTTP 200 exact JSON. |
| STATS-AC-02 | Tasks 3–5 and 7–8: Passed lifecycle moves in-progress to passed. |
| STATS-AC-03 | Tasks 3–5 and 7–8: Failed lifecycle moves in-progress to failed. |
| STATS-AC-04 | Tasks 2–5 and 7–8: admitted run remains total/in-progress until terminal transition. |
| STATS-AC-05 | Tasks 2–4 and 7–8: synchronized transitions and snapshot preserve the invariant. |
| STATS-AC-06 | Tasks 5–6 and 8: exact route method rejection, `Allow: GET`, and non-mutation. |
| STATS-AC-07 | Tasks 7–8: JUnit coverage for all required states and 405 behavior. |
| STATS-AC-08 | Task 10: `mvn --batch-mode verify` after implementation. |
| STATS-AC-09 | Task 9: README and CHANGELOG documentation. |
| STATS-AC-10 | Tasks 3–5 and 11: no browser/local-storage/POST/persistence/scope changes. |

**Plan-ready status:** **Approved by human for implementation** based on the prior chat approval of the requirements, architecture, design review, and plan. **Phase 5 authorization:** Implementation may proceed in a later approved implementation phase. No product code or test is changed by this planning task, and no Maven verification is run here.
