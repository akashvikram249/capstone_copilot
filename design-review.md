# Design Review

## Outcome

Approved as a **local demo capstone**, not as a production test management system.

## Findings and decisions

| Risk / question | Decision |
|---|---|
| User requested a Java implementation but local browser persistence. | Use a Java 17 server for static files and the runner API, with browser local storage for cases and reports. |
| AC-04 says execute a UI automation test, but no real test harness was selected. | Use a clearly labeled simulator to demonstrate In Progress, Passed, and Failed. Document that it does not run browser automation. |
| AC-01 assumes a logged-in user. | Provide a demo-only login gate with no real credentials or security claim. |
| Duplicate IDs and required fields must be reliable. | Validate trimmed mandatory fields and unique IDs (case-insensitive) in the dashboard before saving. |
| User-entered content could be unsafe when displayed. | Escape all dynamic values before inserting into dashboard HTML. |
| Runs are asynchronous and need history. | Java returns a run ID and updates status; the browser polls and stores completed reports locally. |
| Deletion should not erase evidence. | Case deletion preserves existing execution reports. |

## Review checklist

- [x] Correctness: map each user-story criterion to a visible dashboard behavior.
- [x] Security: explicitly limit demo login; escape user content; bound and validate runner requests.
- [x] Error handling: handle duplicate IDs, validation errors, missing runs, and server failures.
- [x] Tests: cover runner state transitions and HTTP endpoint success/error behavior; verify client interactions with a manual browser checklist because no browser test harness exists.
- [x] Simplicity: use JDK HTTP server and plain browser assets instead of unnecessary frameworks or database.
- [x] Transparency: label execution and login as demo-only; explain local-storage limits.

## Residual limitations

- Browser local storage is per browser profile and can be cleared by the user.
- Demo login does not authenticate a user.
- Demo runner does not launch a browser or evaluate the test steps.

## US-103 — Filter test reports by status

### Review scope and approval status

Reviewed the approved US-103 requirements (AC-06 through AC-11) together with the US-103 architecture addition and the current report renderer, storage helpers, report-detail event handling, and available tests. This section supplements the US-102 review above; it does not change or revoke its outcome.

**Status: Approved for implementation under the user-approved US-103 plan.** The normal-path design covers the stated criteria and preserves the existing client-side report ownership boundary. The user accepted the three review recommendations below; the requirements and architecture artifacts record those decisions.

### Severity-ranked findings

| ID / severity | Classification and evidence | Impact | Recommendation |
|---|---|---|---|
| US103-F1 — **P2 (Medium)** | **Confirmed existing data-validation defect / integration risk.** `app.js` `readStorage` parses JSON but does not check the parsed value's shape; `renderReports` assumes `state.reports` has array methods (`.length` and `.map`). The proposed filter similarly depends on an array. Valid JSON such as `null` or an object in the report-storage key therefore bypasses the current parse-error fallback and can throw during rendering, preventing the reports page from displaying its empty/error state. | A browser-local storage value that is syntactically valid but not an array can break both the current report view and the planned All/status-filter views. This is not a defect in the specified filtering algorithm for valid report data. | **Accepted:** validate the loaded report value before array operations, display an actionable error, and leave the stored value untouched. The error is distinct from empty-report and no-match states. |
| US103-F2 — **P2 (Medium)** | **Verification risk.** The architecture explicitly notes that there is no browser JavaScript test harness. The available `DashboardServerTest` covers Java HTTP/static delivery, not selection changes, DOM rendering, storage preservation, or report-detail actions. | The central behavior for AC-06–AC-11 could regress without any automated test failing; server tests cannot demonstrate client-side filtering or data immutability. | **Accepted:** use a documented manual browser acceptance checklist covering default/All, each subset and stable order, details action, both empty states, reload-to-All, result announcements, unchanged stored data, and invalid-data handling, together with `mvn test`. Do not add test tooling or dependencies for this feature. |
| US103-F3 — **P3 (Low)** | **Accessibility risk / assumption.** The architecture selects a native control with a visible label, which provides standard keyboard operation. However, the current report count is an ordinary `<span>` and the report container has no live-region semantics; the architecture did not specify how a screen-reader user is informed that the result list changed after selection. | A user operating the filter with assistive technology may hear the changed select value without a clear announcement of the updated match count or no-match result. | **Accepted:** add a scoped polite live region that announces the visible result count or no-match state without moving focus. |

### Decisions and trade-offs

- **Supported normal path:** retain a transient, in-memory projection of the report array; All is the initial filter; Passed and Failed preserve source order; filtering does not request the server or write/delete reports; reloading returns the filter to All. These choices directly satisfy AC-06–AC-08 and preserve the stated local-storage boundary.
- **Empty states:** keep “No execution reports yet” distinct from the explicit no-matching-reports state required by AC-09. A no-match result is ordinary filtering, not a storage/runner error.
- **Report details and rendering:** keep actions resolved by original report ID against the full report collection, and continue escaping report-derived values before HTML insertion. The existing document-level delegated click handler and `showReport` lookup provide a compatible pattern, provided the filtered renderer does not replace the source collection.
- **Invalid report data:** guard against a parsed non-array report value, surface an actionable error, and preserve the stored value without automatic repair or deletion.
- **Accessibility:** announce the filtered result count and no-match state in a polite live region while retaining focus on the native filter.
- **Verification:** use a documented manual browser acceptance checklist for client behavior and run `mvn test` for Java regressions; no new test tooling or dependency is added.
- **Count semantics:** architecture says the count reflects visible rows. This is consistent with the displayed projection; requirements do not independently prescribe count semantics.
- **Privacy/security:** the planned filter uses only already-loaded local report data and sends neither report content nor filter choice to the server. No new trust boundary or persistence surface is proposed.
- **Scope and simplicity:** the native select and existing empty-state styling are proportionate to this two-status filter. No custom control, backend endpoint, or persisted preference is justified by the requirements.

### Approval status

The three recommendations are reflected in `requirements.md` (AC-10 and AC-11), `architecture.md`, and this review. The user approved the design and implementation plan for Phase 5. This approval does not authorize scope expansion or later SDLC phases.

### US-103 implementation review

The completed report-filter diff was checked against AC-06–AC-11, the approved architecture and design decisions, report rendering and storage call sites, available tests, Maven dependencies, and the CI workflow.

| Review area | Result |
|---|---|
| Correctness | The All/Passed/Failed view preserves source order and report-detail IDs, distinguishes the empty states, and leaves filter selection transient. |
| Security | Report fields continue through HTML escaping; filtering makes no server request and adds no trust boundary. The demo-login and local-storage limitations remain documented. |
| Error handling | Valid-JSON, non-array report data is handled without overwriting it. One additional finding below was fixed: failed report-storage writes could previously be followed by a success toast. |
| Test coverage | Java tests cover runner and HTTP behavior; they do not automate dashboard JavaScript. Manual browser checks covered the report acceptance checklist and a simulated storage-write failure. |
| Clarity / DRY | The report projection and persistence path use the existing renderer and storage helper; no review-worthy duplication was found. |
| Dependency safety | `mvn --batch-mode dependency:tree` showed JUnit Jupiter 5.11.4 and its transitive dependencies in test scope, with no production dependency declared. This is an inventory only; no CVE database or automated vulnerability scanner was run, so no vulnerability-free claim is made. |
| CI configuration | `.github/workflows/ci.yml` grants only `contents: read` and configures Java 17. |

#### Finding and disposition

**US103-CR1 — P2 (Medium), resolved.** `recordReport` previously returned success even when `saveStorage` failed, and updated the in-memory report list before persistence succeeded. A run could therefore show a success-shaped message and later render an unsaved report. The fix now persists a candidate list first, updates state and rerenders only after a successful write, and leaves the existing storage-error toast visible on failure. A targeted browser check simulated a report-storage quota error and confirmed a false result, unchanged in-memory and stored reports, and the storage error message.

**Review outcome:** no unresolved code-review findings. Limits remain: the browser UI has no automated JavaScript test harness; actual screen-reader speech and a dependency CVE scan were not performed.

## DOCSYNC-1 — Generate and check the API reference from OpenAPI

### Review scope and status

Reviewed the DOCSYNC-1 requirements and architecture against all seven DOCSYNC acceptance criteria, the repository's Maven/Java 17/JUnit conventions, `.github/workflows/ci.yml`, and the inspected `docs/` and `automated-api-documentation-sync/` locations. This section is scoped only to DOCSYNC-1 and does not change the earlier US-102 through US-104 reviews.

The user approved the DOCSYNC-1 architecture. That approval does not resolve the source/output paths, OpenAPI provenance/version, or CI command: the earlier “go forward” authorized proceeding with explicitly marked assumptions, not confirmation of those specifics. The source is reported as the story pasted in chat; no Jira/MCP retrieval is claimed.

**Review status: Conditional / blocked from implementation planning pending the decisions below.** The architecture gives a credible route through AC-01–AC-07, but a missing authoritative input prevents the proposed CI integration from being safely enabled, and the CLI's output-path behavior needs a data-preservation guard. No architecture edits or behavior changes are made in this review.

### Severity-ranked findings and risks

| ID / severity | Classification and evidence | Impact | Recommendation |
|---|---|---|---|
| DOCSYNC-F1 — **P1 (High; phase blocker)** | **Confirmed dependency/operational risk, not a defect in an implemented tool.** `requirements.md` says no OpenAPI source was found and its intended path is unconfirmed; creating/changing that definition is out of scope. `architecture.md` proposes attaching the check to `verify`, which the existing CI workflow runs, and itself notes CI cannot be green without an authoritative input. | If the verify hook is enabled before an approved source exists in the repository, the existing CI command will fail on every run. Guessing a path or fabricating a definition would misstate source authority and exceed scope. | **Proposed architecture update:** make an approved, checked-in OpenAPI definition a prerequisite to enabling the verify-bound check. Keep CI integration explicitly deferred until the maintainer supplies/identifies that input, or obtain approval to expand DOCSYNC-1 to provide it. Do not silently skip a missing source in CI, since that could hide a broken check. |
| DOCSYNC-F2 — **P2 (Medium)** | **Confirmed design gap.** The proposed CLI may accept explicit input/output paths, while the generation contract says only the designated generated reference may be changed. No rule rejects an output path equal to the source or pointing at unrelated/manual documentation. | A command typo or path override could overwrite the OpenAPI definition or unrelated documentation, violating the safe-input and documentation-preservation requirements despite the dedicated-file default. | **Proposed architecture update:** constrain generation to the agreed generated-reference target (or validate any override against an explicitly approved output boundary); reject source/output identity and unsafe aliases before writing. Retain the temporary-write/replace safeguard. |
| DOCSYNC-F3 — **P2 (Medium)** | **Operational-clarity risk.** AC-03 requires stale-check guidance that tells maintainers how to regenerate. The architecture requires the “exact regeneration command” but leaves the CLI/Maven launch mechanism and command unresolved; the current `exec-maven-plugin` is configured for the dashboard server, not this utility. | A stale check could identify drift but offer unusable or incorrect guidance; the proposed CI hook is also not yet tied to a concrete, reproducible command. | **Proposed architecture update:** settle and document one canonical local generation command and one check command, then require stale diagnostics to print the former verbatim. Confirm how that command coexists with the existing Maven server entry point before attaching check to `verify`. |
| DOCSYNC-F4 — **P2 (Medium)** | **Verification risk.** The architecture promises preservation on write errors and describes a temporary sibling file plus replacement, but its test list does not exercise temporary-file creation/write/replacement failure or the stated fallback behavior. AC-07 lists source errors and stale detection; the broader non-destructive-write guarantee is not thereby verified. | A failure during generation could still damage or remove a prior reference if the implementation's replacement/fallback path is incorrect. | **Proposed architecture update:** add a deterministic write-failure test strategy and cover failures before replacement, asserting the prior target remains byte-for-byte unchanged and unrelated docs remain untouched. Specify that a fallback must fail closed rather than delete the prior target first. |

### Acceptance-criteria trace and design trade-offs

| Criterion | Review assessment |
|---|---|
| DOCSYNC-AC-01 — Generate endpoint reference | Covered in the architecture by parsing operations and rendering path, method, and summary into a clearly identified reference. Missing-summary behavior remains an assumption/open decision below. |
| DOCSYNC-AC-02 — Deterministic output | Covered by canonical path/method order, stable rendering, UTF-8/LF, and exclusion of timestamps/environment-specific data; the proposed repeated-generation test is appropriate. |
| DOCSYNC-AC-03 — Stale check guidance | Byte comparison and stale/nonzero behavior are specified, but the actionable regeneration command is not yet resolved (DOCSYNC-F3). |
| DOCSYNC-AC-04 — Read-only check | The separate in-memory check path, no-write/no-temp-file rule, and read-only CI permission align with the criterion. The proposed isolated tests should also assert no repository mutation. |
| DOCSYNC-AC-05 — Safe input errors | Parse/validation before writes and preservation of existing output for missing/invalid input are specified. The output-target guard and write-failure evidence remain necessary (DOCSYNC-F2/F4). |
| DOCSYNC-AC-06 — Preserve other documentation | A dedicated generated file is a strong isolation choice; unrestricted output-path overrides undermine that guarantee (DOCSYNC-F2). |
| DOCSYNC-AC-07 — Required test coverage | The planned suite covers generation, repeatability, stale detection, and missing/invalid input; add the write-failure protection check noted in DOCSYNC-F4. |

The Java 17/Maven/JUnit approach fits the repository and avoids a separate runtime, but robust OpenAPI parsing introduces a new production dependency. Pin and review the chosen parser/version, document supported OpenAPI version/format, and keep external reference/network resolution disabled as already specified. The read-only workflow permission is a suitable boundary; no credentials, commit, or push capability is needed. Deterministic sorting and a standalone generated file favor stability and safe preservation over matching the source document's authored order or inserting generated content into a manual guide.

### Open questions and decisions required

1. What is the authoritative OpenAPI file path, format/version, and source/ownership? It was not found in the inspected locations; no Jira/MCP provenance is asserted.
2. Is `docs/api-reference.md` the approved generated destination and Markdown the required format, or should another location/format be used?
3. Should the read-only check be attached to the existing `mvn --batch-mode verify` CI path? This can only be enabled once the approved source exists. What canonical Maven invocation should local generation and checking use?
4. OpenAPI permits operations without a `summary`, while DOCSYNC-AC-01 requests one for every endpoint. Confirm whether such an input should fail with actionable guidance (the architecture's current assumption), or whether a documented fallback is required.
5. Confirm the output-boundary rule in DOCSYNC-F2: generation should not allow an arbitrary output path to overwrite the input or unrelated repository documentation.

### Proposed architecture updates and approval gate

The recommendations in DOCSYNC-F1–F4 are proposals only; they have not been applied to `architecture.md` and are not recorded as approved decisions. Before planning, please confirm the source/output/format and CI choices, the missing-summary policy, and agreement to constrain the generation target and test write-failure preservation. Once those are resolved, the architecture can be updated precisely and reviewed for approval. No planning, implementation, or tests were performed as part of this phase.

## US-104 — Export visible execution reports as CSV

### Review scope and approval status

Reviewed approved US-104 requirements (AC-12–AC-19) with the corresponding architecture and repository evidence. Scope is limited to US-104, the CSV/report implementation evidence, and related tests/dependencies/CI and status artifacts. US-102, US-103, and DOCSYNC-1 review sections are preserved and not re-evaluated. The recorded story source is user-provided chat; no Jira, MCP, or other external source is claimed.

**Status: Pending human agreement before implementation planning.** The requirements and architecture have explicit user approval. Existing code and `impl-plan.md` record partial US-104 implementation and test evidence; this review does not authorize or perform planning, implementation, tests, or downstream phases. No architecture or production changes were made.

### Evidence reviewed

- `requirements.md` US-104 FR-7 and AC-12–AC-19: exact visible subset/order, six headers and field mapping, raw duration/timestamp, CSV quoting/UTF-8, disabled empty state, fixed filename, and local-only/read-only behavior.
- `architecture.md` US-104: shared ordered projection, Blob/object-URL/link lifecycle, invalid-data separation, local-only boundary, spreadsheet formula-interpretation risk, manual browser acceptance approach, and AC trace.
- `src/main/resources/static/index.html`: Reports page includes a labeled native filter and an Export CSV button with `aria-describedby` pointing at visible help text, plus the polite live region.
- `src/main/resources/static/app.js`: `getVisibleReports()` is used by both `renderReports()` and `exportVisibleReports()`; the serializer maps the six fields in required order, quotes comma/quote/CR/LF fields and doubles embedded quotes, and joins records with CRLF. Export uses a UTF-8 `text/csv` Blob, the exact filename, a temporary link, deferred cleanup after activation, and cleanup/error handling on synchronous exceptions. It has a distinct invalid-data state and does not call storage/network APIs in the export path.
- `src/main/resources/static/styles.css`: export button has a disabled cursor/opacity/grayscale treatment; help text is visible. This source inspection does not establish actual contrast or assistive-technology behavior.
- `src/test/java`: only Java server/service tests are present. `pom.xml` declares JUnit Jupiter as test-scope and no browser JavaScript or CSV test dependency. `.github/workflows/ci.yml` runs `mvn --batch-mode verify` with read-only `contents` permission.
- Existing status evidence: `impl-plan.md` reports Node-mocked projection/CSV/empty-state/download lifecycle checks and `mvn test` with 7 tests passing, but records integrated browser acceptance as **not run** because no browser executable or browser automation tool was available. These are reported artifacts, not tests run in this review.

### Severity-ranked findings

**No confirmed implementation defect or unresolved architecture gap was identified in the inspected US-104 source.** The prior design-review recommendations about projection reuse, accessible empty-state association/disabled styling, and exceptional/deferred cleanup are now reflected in the architecture and source. Their actual integrated browser behavior remains unverified.

| ID / severity | Classification and evidence | Impact | Mitigation / disposition |
|---|---|---|---|
| US104-F4 — **P2 (Medium)** | **Open verification risk, not a confirmed defect.** `impl-plan.md` records mocked Node checks and explicitly marks integrated browser acceptance not run. Repository tests are Java-only; `pom.xml` has no browser harness, and CI runs Maven verification rather than browser checks. | Automated evidence cannot establish real browser download naming/encoding, rendered-row parity, disabled-state usability, browser resource cleanup, or no-network/no-storage behavior end to end. A passing Maven result alone does not verify AC-12–AC-19 in the browser. | Keep browser acceptance explicitly pending; before claiming full US-104 acceptance, record actual manual browser results for the existing checklist (all filters and order, raw fields/CSV parsing/UTF-8/filename, both empty states and invalid data, storage/network non-mutation, and success/failure cleanup where feasible). Do not add test tools/dependencies without approval and do not claim a browser confirms download completion. |

### Prior findings and residual risks

- **US104-F1 — P2, addressed in source:** `getVisibleReports()` now supplies both rendering and export. This reduces filter/projection drift and uses current in-memory reports without a separate storage read.
- **US104-F3 — P2, addressed in source; browser usability unverified:** the export control references adjacent visible help text, and CSS gives its disabled state a visual treatment. The invalid-report-data message remains distinct in `renderReports()`. No screen-reader/keyboard browser acceptance evidence is recorded for US-104.
- **US104-F5 — P3, design reflected in source; browser behavior unverified:** export schedules cleanup after a successful click and attempts cleanup plus an actionable toast after synchronous failure. Browser download completion is not observable by the app. No browser check of actual download/resource lifecycle is recorded.
- **US104-F2 — P2 residual spreadsheet risk, not a defect:** formula-like values may be interpreted by spreadsheet software. The approved exact-value contract preserves source values; `impl-plan.md` records acceptance of this risk and instructs not to add formula neutralization or warnings that alter the approved behavior. Any transformation, warning, or alternate export mode remains a behavior-changing proposal requiring renewed user agreement.

### Requirement coverage / AC trace

| Criterion | Review evidence and status |
|---|---|
| AC-12 — Export action | Present in `index.html`; wired to `exportVisibleReports()` in `app.js`. |
| AC-13 — Visible subset | Shared `getVisibleReports()` serves both table and export, applying All/Passed/Failed to the in-memory report list. Mocked subset checks are reported in `impl-plan.md`; integrated browser check is pending. |
| AC-14 — Columns and values | Header constant and serializer map the six required fields, including `durationMs` and stored `timestamp`. Mocked round-trip evidence is recorded; browser evidence pending. |
| AC-15 — Header and order | Serializer emits one header row and follows projection order. Mocked order evidence is recorded; browser evidence pending. |
| AC-16 — UTF-8 escaping | Serializer quotes fields with comma, quote, CR, or LF and doubles embedded quotes; Blob declares UTF-8. Mocked CSV-reader round-trip evidence is recorded; browser download/encoding acceptance pending. |
| AC-17 — Empty visible set | Renderer disables the button and presents help text for empty/no-match cases; invalid data uses separate error text. Mocked state checks are recorded; browser/assistive-technology inspection pending. |
| AC-18 — Filename | Download link uses `caseflow-reports.csv`; actual browser download verification pending. |
| AC-19 — Read-only local export | Inspected export flow derives from in-memory state and has no storage or network call. Mocked unchanged-state evidence is recorded; integrated browser storage/network check pending. |

### Confirmed decisions, proposals, and open questions

- **Confirmed decisions:** US-104 scope, fields, raw values, filename, visible-order export, local-only/read-only behavior, and the Java 17/plain HTML-CSS-JavaScript/browser-local boundaries are approved in the requirements/architecture. Existing plan evidence records acceptance of the formula-interpretation risk.
- **Proposals:** No architecture update is required by this review. The previous behavior-preserving recommendations (one shared projection, accessible disabled explanation with invalid-data distinction, and deferred/exceptional cleanup) are present in the approved architecture and inspected source. No behavior-changing mitigation is proposed or applied.
- **Open question:** No additional behavior or architecture decision is identified. Human agreement on this review and the pending browser-verification limitation is still required at the phase gate; do not treat that agreement as authorization for any later phase unless separately given.

### Residual risks and test limitations

The approved formula-fidelity behavior retains the documented spreadsheet interpretation risk. Browser-level download behavior, actual accessibility/usability, and end-to-end no-storage/no-network behavior remain unverified. Node-mocked checks and the reported 7 passing Maven tests are not integrated browser acceptance evidence. The browser does not provide a reliable signal that a user completed or accepted the download.

### Proposed architecture updates and approval gate

**Proposed architecture updates: none.** Do not edit `architecture.md`; do not adopt any behavior-changing mitigation implicitly.

**Approval gate: pending human agreement before implementation planning.** Please review this US-104 assessment, acknowledge the retained formula-interpretation risk and browser-acceptance limitation, and explicitly approve or request changes to the design-review outcome. No planning or downstream phase is authorized by this review.

## STATS — `GET /api/stats` (STATS-AC-01 through STATS-AC-10)

### Review scope and approval status

Reviewed the human-approved stats requirements and architecture in `requirements.md` and `architecture.md` together, limited to STATS-AC-01–10. Existing US-102, US-103, US-104, and DOCSYNC-1 review text is preserved and was not re-evaluated. The story source remains the user's chat message; no Jira, MCP, or other external source is claimed.

**Status: Approved by human for implementation.** Requirements and architecture were previously approved in chat. The prior stats design-review outcome and implementation plan were also approved in chat. This first current-artifact write records that authorization without inventing an approver name or additional evidence. This approval is implementation/development status only; no implementation or test execution was performed by this phase.

### Severity-ranked findings and implementation guardrails

| ID / severity | Classification and evidence | Impact | Guardrail |
|---|---|---|---|
| STATS-F1 — **P2 (Medium)** | **Concurrency/scheduling risk.** `architecture.md` correctly requires one lifecycle synchronization boundary and identifies scheduler rejection/shutdown as an edge case, but it does not prescribe an outcome for an admitted run if scheduling completion fails. | A count could remain in progress with no terminal transition, violating intended terminal-state lifecycle behavior and, operationally, leaving the invariant true but a run permanently in progress. | Keep run admission and completion scheduling consistent: if scheduling cannot be committed, fail/rollback admission and the two admission counters together, or use a clearly synchronized failure transition that restores the invariant while preserving the existing `POST /api/runs` contract. Do not leave a counted admitted run unscheduled. This resolution must not change the approved POST response or run behavior outside the existing failure handling. |
| STATS-F2 — **P2 (Medium)** | **Lifecycle consistency/verification risk.** The architecture allows the existing run map and scheduler to publish status and aggregate state, and warns against separate unsynchronized mechanisms. | Independent updates or duplicate terminal callbacks could expose lookup/stats inconsistency or count a run twice. | Under one short-held lifecycle boundary, apply the run status and matching counter transition together; reject duplicate completion by terminal-state check; keep scheduling, HTTP serialization, and network work outside the lock. A read must obtain an immutable four-counter snapshot; independent atomic counters alone are insufficient. |
| STATS-F3 — **P2 (Medium)** | **Verification gap.** STATS-AC-07 requires JUnit coverage and STATS-AC-08 requires `mvn verify`, while the architecture relies on deterministic construction and concurrent testing described only as implementation/test guidance. | Without focused tests, an implementation may pass normal cases yet violate invariant or rejected-method non-mutation under concurrency. | Use existing JUnit 5/service and HTTP conventions to test zero, Passed, Failed, in-progress, mixed invariant, and 405/`Allow: GET` non-mutation. Add a controlled concurrent start/completion/read case where practical, and retain existing endpoint regression coverage. Run `mvn verify` only in the verification phase; this review did not execute it. |
| STATS-F4 — **P3 (Low)** | **Operational clarity risk.** Counts are process-local, but restart behavior and multiple-process aggregation are easy to confuse with persistence or a dashboard-wide total. | Operators or tests could assume that restarted or load-balanced servers retain/share counts. | Keep documentation explicit that counts describe the current process lifetime and reset on restart; do not add persistence or cross-process aggregation. Preserve existing demo/server boundaries and expose no run details. |

### Confirmed defects, risks, assumptions, and open questions

- **Confirmed architecture defects:** none identified for STATS-AC-01–10. The architecture provides a complete route, lifecycle transition, invariant, method-rejection, and test/documentation trace.
- **Risks:** scheduler failure/duplicate completion, concurrent lookup/stats publication, and verification gaps are implementation risks rather than confirmed defects in a runtime implementation.
- **Assumptions:** `ExecutionService` is the sole lifecycle authority; admitted runs start only from the existing POST path and reach at most one terminal state; JDK server and executor remain demo/local-process components; process restart resets counters.
- **Open questions:** no unresolved requirements or architecture decision. The exact code-level rollback/scheduling-failure policy is a bounded implementation guardrail (STATS-F1), not a requirement expansion or open scope question.

### Decisions and trade-offs

- Use `ExecutionService` as the sole owner of run records and aggregate counters; do not add a server-level counter store or new persistence.
- Mutate and read start/completion/snapshot transitions under one short lifecycle boundary, and publish an immutable four-field snapshot.
- Use existing JDK JSON and HTTP response conventions; add no framework, JSON library, database, cache, authentication, or run-detail fields.
- Keep the route backend-only and preserve health, static assets, POST run creation, run lookup, timing, and browser assets unchanged.
- Reject all non-GET methods before state reads/mutations and include `Allow: GET`.
- Cover behavior through existing JUnit 5 and Maven conventions plus a deterministic controlled concurrency case; do not add browser or external test tooling.
- Document process-local semantics in README and record the endpoint in CHANGELOG as later implementation/documentation work.

### Acceptance-criteria trace

| Criterion | Review assessment |
|---|---|
| STATS-AC-01 — Fresh server state | Covered: initialize four counters to zero and GET returns exactly those fields with HTTP 200. |
| STATS-AC-02 — Passed run | Covered: start moves one admitted run to total/in-progress; single Passed transition moves it to passed. |
| STATS-AC-03 — Failed run | Covered: start moves one admitted run to total/in-progress; single Failed transition moves it to failed. |
| STATS-AC-04 — In-progress run | Covered: before terminal transition, admitted run contributes 1 to total and 1 to in-progress. |
| STATS-AC-05 — Count invariant | Covered by shared lifecycle/snapshot synchronization; implementation must also guard duplicate/failed transitions. |
| STATS-AC-06 — 405 method handling | Covered: route exact-match/method check, 405 helper, `Allow: GET`, and no mutation. |
| STATS-AC-07 — JUnit coverage | Architecture has a complete planned test boundary; STATS-F3 is the implementation guardrail for invariant/concurrency and non-mutation. |
| STATS-AC-08 — Build verification | Use existing Java 17/Maven/JUnit 5; `mvn verify` is required in verification, not this design-review phase. |
| STATS-AC-09 — Documentation | Requirements and architecture require README field/state documentation and CHANGELOG entry; no documentation implementation occurred here. |
| STATS-AC-10 — Existing scope | Covered: no browser assets/local storage/POST changes and no persistence or extra endpoints in the design. |

### Recommended architecture updates

**Proposed architecture updates: none.** The architecture already contains the necessary synchronization and boundary directions. Record the following implementation guardrails in the implementation plan if planning proceeds: synchronized admission/scheduling outcome, duplicate-completion protection, immutable snapshot, and focused concurrency/non-mutation tests. These are implementation details, not applied behavior-changing architecture edits.

**Human approval status:** Approved by human in prior chat for the stats requirements, architecture, design-review outcome, and plan. No unresolved design decision is marked pending. The prior plan approval explicitly authorizes Phase 5 implementation; this planning phase adds the implementation tasks to the current artifact without changing product code or running verification.
