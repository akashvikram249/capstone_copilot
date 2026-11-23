"use strict";

const CASES_KEY = "caseflow.testCases.v1";
const REPORTS_KEY = "caseflow.executionReports.v1";
const SESSION_KEY = "caseflow.demoUser";
const REPORT_CSV_HEADERS = ["Case ID", "Test Case", "Status", "Duration (ms)", "Executed At", "Failure Details"];
const REPORT_CSV_FILENAME = "caseflow-reports.csv";
const seedCases = [
  {
    id: "TC-101",
    name: "Sign in with valid credentials and navigate to dashboard",
    module: "Authentication",
    priority: "High",
    status: "Ready",
    lastResult: "Not run",
    steps: "1. Open the sign-in page\n2. Enter valid credentials\n3. Select Sign in",
    expectedResult: "The user is taken to the dashboard.",
    demoOutcome: "pass"
  },
  {
    id: "TC-102",
    name: "Search for a product",
    module: "Catalog",
    priority: "Medium",
    status: "Ready",
    lastResult: "Not run",
    steps: "1. Open the catalog\n2. Search for a product name\n3. Review the results",
    expectedResult: "Matching products are shown.",
    demoOutcome: "pass"
  },
  {
    id: "TC-103",
    name: "Submit an empty checkout form",
    module: "Checkout",
    priority: "High",
    status: "Ready",
    lastResult: "Not run",
    steps: "1. Open checkout\n2. Leave required fields blank\n3. Select Place order",
    expectedResult: "Required-field validation messages are displayed.",
    demoOutcome: "fail"
  },
  {
    id: "TC-104",
    name: "Update profile preferences",
    module: "Profile",
    priority: "Low",
    status: "Ready",
    lastResult: "Not run",
    steps: "1. Open profile settings\n2. Update notification preferences\n3. Save changes",
    expectedResult: "The updated preferences remain selected.",
    demoOutcome: "pass"
  }
];

const storedReports = readStorage(REPORTS_KEY, []);
const state = {
  cases: readStorage(CASES_KEY, seedCases),
  reports: Array.isArray(storedReports) ? storedReports : [],
  reportsDataInvalid: !Array.isArray(storedReports),
  page: "overview",
  editingId: null,
  toastTimer: null
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function readStorage(key, fallback) {
  try {
    const stored = localStorage.getItem(key);
    return stored === null ? structuredClone(fallback) : JSON.parse(stored);
  } catch (error) {
    console.error(`Could not read ${key} from browser storage.`, error);
    showToast("Saved browser data could not be read. Check this browser's storage settings.", true);
    return structuredClone(fallback);
  }
}

function saveStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error(`Could not save ${key} to browser storage.`, error);
    showToast("Could not save changes in this browser. Check available storage space.", true);
    return false;
  }
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  })[character]);
}

function showToast(message, isError = false) {
  const toast = $("#toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.toggle("toast-error", isError);
  toast.classList.add("show");
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => toast.classList.remove("show"), 3200);
}

function persistCases() {
  if (saveStorage(CASES_KEY, state.cases)) render();
}

function persistReports(reports) {
  if (state.reportsDataInvalid) {
    showToast("The saved reports were not changed because their browser data is not a list. Check the report data and reload before saving reports.", true);
    return false;
  }
  const reportsToSave = reports.slice(0, 250);
  if (!saveStorage(REPORTS_KEY, reportsToSave)) return false;
  state.reports = reportsToSave;
  render();
  return true;
}

function initializeLogin() {
  const existingName = sessionStorage.getItem(SESSION_KEY);
  if (existingName) enterDashboard(existingName);

  $("#login-form").addEventListener("submit", event => {
    event.preventDefault();
    const name = $("#login-name").value.trim();
    if (!name) {
      showToast("Enter your name to continue.", true);
      return;
    }
    sessionStorage.setItem(SESSION_KEY, name);
    enterDashboard(name);
  });
}

function enterDashboard(name) {
  $("#login-screen").classList.add("hidden");
  $("#app-shell").classList.remove("hidden");
  const firstName = name.trim().split(/\s+/)[0];
  $("#profile-name").textContent = name;
  $("#greeting-name").textContent = firstName;
  $("#today-label").textContent = new Intl.DateTimeFormat(undefined, {
    weekday: "short", month: "short", day: "numeric"
  }).format(new Date());
  render();
}

function navigate(page) {
  state.page = page;
  $$(".page").forEach(section => section.classList.toggle("hidden", section.id !== `${page}-page`));
  $$(".nav-link").forEach(link => link.classList.toggle("active", link.dataset.nav === page));
  $("#page-title").textContent = ({ overview: "Overview", cases: "Test cases", reports: "Test reports" })[page];
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function render() {
  renderStats();
  renderModules();
  renderCases();
  renderReports();
}

function renderStats() {
  const completed = state.reports.filter(report => report.status === "Passed" || report.status === "Failed");
  const passed = completed.filter(report => report.status === "Passed").length;
  const rate = completed.length ? `${Math.round(passed / completed.length * 100)}%` : "—";
  $("#stat-total").textContent = state.cases.length;
  $("#case-nav-count").textContent = state.cases.length;
  $("#stat-pass").textContent = rate;
  $("#stat-pass-note").textContent = completed.length ? `${passed} of ${completed.length} completed runs` : "No runs yet";
  $("#stat-runs").textContent = state.reports.length;
  $("#stat-failed").textContent = state.cases.filter(testCase => testCase.lastResult === "Failed").length;
}

function renderModules() {
  const select = $("#module-filter");
  if (!select) return;
  const selected = select.value;
  const modules = [...new Set(state.cases.map(testCase => testCase.module).filter(Boolean))]
    .sort((left, right) => left.localeCompare(right));
  select.innerHTML = `<option value="">All modules</option>${modules.map(module =>
    `<option value="${escapeHtml(module)}">${escapeHtml(module)}</option>`).join("")}`;
  if (modules.includes(selected)) select.value = selected;
}

function priorityBadge(priority) {
  const color = ({ High: "high", Medium: "medium", Low: "low" })[priority] || "low";
  return `<span class="priority priority-${color}">${escapeHtml(priority)}</span>`;
}

function resultBadge(result) {
  const color = ({
    Passed: "passed", Failed: "failed", "In Progress": "progress", Ready: "ready", "Not run": "ready"
  })[result] || "ready";
  const label = result === "Not run" ? "Not run" : result;
  return `<span class="result-badge badge-${color}">${escapeHtml(label)}</span>`;
}

function caseRows(cases, includeActions = true) {
  if (!cases.length) {
    return `<div class="empty-state"><span class="empty-icon">▤</span><strong>No test cases found</strong>
      <p>Try changing your search or add a new scenario.</p>
      <button class="button button-primary" data-action="add">Add test case</button></div>`;
  }
  return `<div class="table-wrap"><table><thead><tr>
    <th>Test case</th><th>Module</th><th>Priority</th><th>Status</th><th>Last result</th>${includeActions ? "<th>Actions</th>" : ""}
    </tr></thead><tbody>${cases.map(testCase => `<tr>
      <td><div class="case-name-cell"><strong>${escapeHtml(testCase.name)}</strong><small class="case-id">${escapeHtml(testCase.id)}</small></div></td>
      <td>${escapeHtml(testCase.module)}</td><td>${priorityBadge(testCase.priority)}</td>
      <td>${resultBadge(testCase.status)}</td><td>${resultBadge(testCase.lastResult || "Not run")}</td>
      ${includeActions ? `<td><div class="actions-cell">
        <button class="row-action run-action" data-action="run" data-id="${escapeHtml(testCase.id)}" ${testCase.status === "In Progress" ? "disabled" : ""}>${testCase.status === "In Progress" ? "Running…" : "▶ Run"}</button>
        <button class="row-action" data-action="edit" data-id="${escapeHtml(testCase.id)}" aria-label="Edit ${escapeHtml(testCase.id)}" title="Edit">✎</button>
        <button class="row-action" data-action="delete" data-id="${escapeHtml(testCase.id)}" aria-label="Delete ${escapeHtml(testCase.id)}" title="Delete">⌫</button>
      </div></td>` : ""}</tr>`).join("")}</tbody></table></div>`;
}

function renderCases() {
  const query = ($("#search-input")?.value || "").trim().toLowerCase();
  const module = $("#module-filter")?.value || "";
  const priority = $("#priority-filter")?.value || "";
  const status = $("#status-filter")?.value || "";
  const filtered = state.cases.filter(testCase => {
    const searchable = [testCase.id, testCase.name, testCase.module, testCase.steps, testCase.expectedResult]
      .join(" ").toLowerCase();
    return (!query || searchable.includes(query))
      && (!module || testCase.module === module)
      && (!priority || testCase.priority === priority)
      && (!status || testCase.status === status);
  });
  $("#table-count").textContent = filtered.length;
  $("#cases-table").innerHTML = caseRows(filtered);
  $("#overview-table").innerHTML = caseRows(state.cases.slice(0, 5), true);
}

function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Unknown time" : new Intl.DateTimeFormat(undefined, {
    month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit"
  }).format(date);
}

function formatDuration(milliseconds) {
  const seconds = Math.max(0, milliseconds) / 1000;
  return seconds < 1 ? `${Math.round(milliseconds)} ms` : `${seconds.toFixed(1)} sec`;
}

function getVisibleReports() {
  const filter = $("#report-status-filter");
  if (state.reportsDataInvalid || !filter) return [];
  return filter.value === "All"
    ? state.reports
    : state.reports.filter(report => report.status === filter.value);
}

function csvField(value) {
  const field = String(value ?? "");
  return /[",\r\n]/.test(field) ? `"${field.replace(/"/g, '""')}"` : field;
}

function serializeReportsCsv(reports) {
  const rows = reports.map(report => [
    report.caseId,
    report.title,
    report.status,
    report.durationMs,
    report.timestamp,
    report.failureDetails
  ]);
  return [REPORT_CSV_HEADERS, ...rows]
    .map(row => row.map(csvField).join(","))
    .join("\r\n");
}

function exportVisibleReports() {
  const reports = getVisibleReports();
  if (!reports.length) return;

  let objectUrl = null;
  let downloadLink = null;
  const cleanup = () => {
    if (downloadLink) {
      try {
        downloadLink.remove();
      } catch (error) {
        console.error("Could not remove the temporary CSV download link.", error);
      }
      downloadLink = null;
    }
    if (objectUrl) {
      const url = objectUrl;
      objectUrl = null;
      try {
        URL.revokeObjectURL(url);
      } catch (error) {
        console.error("Could not release the temporary CSV download URL.", error);
      }
    }
  };

  try {
    const csv = serializeReportsCsv(reports);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    objectUrl = URL.createObjectURL(blob);
    downloadLink = document.createElement("a");
    downloadLink.href = objectUrl;
    downloadLink.download = REPORT_CSV_FILENAME;
    downloadLink.hidden = true;
    document.body.append(downloadLink);
    downloadLink.click();
    setTimeout(cleanup, 1000);
  } catch (error) {
    cleanup();
    console.error("Could not export execution reports as CSV.", error);
    showToast("Could not create the CSV download. Try again; your saved reports were not changed.", true);
  }
}

function renderReports(announce = false) {
  const filter = $("#report-status-filter");
  const announcement = $("#report-announcement");
  const exportButton = $("#export-reports-button");
  const exportHelp = $("#export-reports-help");
  if (state.reportsDataInvalid) {
    filter.disabled = true;
    exportButton.disabled = true;
    exportHelp.textContent = "Export is unavailable because the saved report data is invalid. Check or restore it, then reload.";
    $("#report-count").textContent = "0";
    $("#reports-table").innerHTML = `<div class="empty-state report-data-error"><span class="empty-icon">!</span>
      <strong>Saved report data is not a list</strong>
      <p>The report data in this browser has not been changed. Check or restore the ${escapeHtml(REPORTS_KEY)} value, then reload this page.</p></div>`;
    announcement.textContent = "";
    return;
  }

  filter.disabled = false;
  const visibleReports = getVisibleReports();
  exportButton.disabled = visibleReports.length === 0;
  exportHelp.textContent = visibleReports.length
    ? "Downloads the reports currently shown; saved reports are unchanged."
    : "No visible reports to export.";
  $("#report-count").textContent = visibleReports.length;
  if (!state.reports.length) {
    $("#reports-table").innerHTML = `<div class="empty-state"><span class="empty-icon">◷</span>
      <strong>No execution reports yet</strong><p>Run a test case and its report will appear here.</p>
      <button class="button button-primary" data-nav="cases">Browse test cases</button></div>`;
  } else if (!visibleReports.length) {
    $("#reports-table").innerHTML = `<div class="empty-state"><span class="empty-icon">⌕</span>
      <strong>No matching reports</strong><p>Choose another status to see more execution reports.</p></div>`;
  } else {
    $("#reports-table").innerHTML = `<div class="table-wrap"><table><thead><tr>
      <th>Test case</th><th>Result</th><th>Duration</th><th>Executed</th><th>Details</th>
      </tr></thead><tbody>${visibleReports.map(report => `<tr>
        <td><div class="case-name-cell"><strong>${escapeHtml(report.title)}</strong><small class="case-id">${escapeHtml(report.caseId)}</small></div></td>
        <td>${resultBadge(report.status)}</td><td>${escapeHtml(formatDuration(report.durationMs))}</td>
        <td>${escapeHtml(formatDate(report.timestamp))}</td>
        <td><button class="text-button" data-action="report" data-id="${escapeHtml(report.id)}">View report →</button></td>
        </tr>`).join("")}</tbody></table></div>`;
  }
  if (announce) {
    announcement.textContent = state.reports.length && !visibleReports.length
      ? `No reports match ${filter.value}.`
      : `${visibleReports.length} ${visibleReports.length === 1 ? "report" : "reports"} shown.`;
  }
}

function recordReport(report) {
  if (state.reportsDataInvalid) {
    showToast("The run's report was not saved because saved report data is invalid. Check or restore the browser's report data, then reload.", true);
    return false;
  }
  return persistReports([report, ...state.reports]);
}

function openCaseDialog(testCase = null) {
  state.editingId = testCase?.id || null;
  $("#case-dialog-title").textContent = testCase ? "Edit test case" : "Create test case";
  $("#save-label").textContent = testCase ? "Save changes" : "Save test case";
  $("#form-error").classList.add("hidden");
  $("#case-form").reset();
  if (testCase) {
    $("#case-id").value = testCase.id;
    $("#case-id").readOnly = true;
    $("#case-name").value = testCase.name;
    $("#case-module").value = testCase.module;
    $("#case-priority").value = testCase.priority;
    $("#case-steps").value = testCase.steps;
    $("#case-expected").value = testCase.expectedResult;
    $("#case-outcome").value = testCase.demoOutcome || "pass";
  } else {
    $("#case-id").readOnly = false;
  }
  $("#case-dialog").showModal();
  $("#case-id").focus();
}

function saveCase(event) {
  event.preventDefault();
  const form = new FormData($("#case-form"));
  const values = Object.fromEntries(form.entries());
  for (const field of ["id", "name", "module", "priority", "steps", "expectedResult"]) {
    values[field] = String(values[field] || "").trim();
    if (!values[field]) {
      showFormError("Complete all required fields before saving.");
      return;
    }
  }
  const duplicate = state.cases.find(testCase => testCase.id.toLowerCase() === values.id.toLowerCase()
    && testCase.id !== state.editingId);
  if (duplicate) {
    showFormError(`Test case ID ${values.id} is already in use. Choose a unique ID.`);
    $("#case-id").focus();
    return;
  }

  if (state.editingId) {
    const current = state.cases.find(testCase => testCase.id === state.editingId);
    if (!current) {
      showFormError("This test case no longer exists. Close the form and refresh the list.");
      return;
    }
    Object.assign(current, values);
  } else {
    state.cases.unshift({ ...values, status: "Ready", lastResult: "Not run" });
  }
  const saved = saveStorage(CASES_KEY, state.cases);
  if (!saved) return;
  $("#case-dialog").close();
  render();
  showToast(state.editingId ? "Test case updated." : "Test case created.");
  state.editingId = null;
}

function showFormError(message) {
  const error = $("#form-error");
  error.textContent = message;
  error.classList.remove("hidden");
}

async function runCase(id) {
  const testCase = state.cases.find(item => item.id === id);
  if (!testCase || testCase.status === "In Progress") return;
  testCase.status = "In Progress";
  testCase.lastResult = "In Progress";
  persistCases();
  showToast(`Starting ${testCase.id}. Demo execution is in progress.`);

  const startedAt = new Date().toISOString();
  const startTime = performance.now();
  try {
    const body = new URLSearchParams({
      caseId: testCase.id,
      title: testCase.name,
      outcome: testCase.demoOutcome || "pass"
    });
    const startResponse = await fetch("/api/runs", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8" },
      body
    });
    const started = await readApiResponse(startResponse);
    let completed = started;
    while (completed.status === "In Progress") {
      await new Promise(resolve => setTimeout(resolve, 350));
      const statusResponse = await fetch(`/api/runs/${encodeURIComponent(started.id)}`);
      completed = await readApiResponse(statusResponse);
    }
    testCase.status = completed.status;
    testCase.lastResult = completed.status;
    const report = {
      id: completed.id,
      caseId: testCase.id,
      title: testCase.name,
      status: completed.status,
      durationMs: completed.durationMs ?? Math.round(performance.now() - startTime),
      timestamp: completed.timestamp || startedAt,
      failureDetails: completed.failureDetails || ""
    };
    saveStorage(CASES_KEY, state.cases);
    const reportSaved = recordReport(report);
    if (reportSaved) showToast(`${testCase.id} finished: ${completed.status}.`);
  } catch (error) {
    console.error("Demo test execution failed.", error);
    testCase.status = "Failed";
    testCase.lastResult = "Failed";
    const report = {
      id: `local-${Date.now()}`,
      caseId: testCase.id,
      title: testCase.name,
      status: "Failed",
      durationMs: Math.round(performance.now() - startTime),
      timestamp: startedAt,
      failureDetails: "Could not reach the demo runner. Confirm the dashboard server is running and try again."
    };
    saveStorage(CASES_KEY, state.cases);
    const reportSaved = recordReport(report);
    if (reportSaved) showToast(error.message || "The demo test runner could not complete this run.", true);
  }
}

async function readApiResponse(response) {
  let payload;
  try {
    payload = await response.json();
  } catch (error) {
    throw new Error("The demo runner returned an unreadable response.");
  }
  if (!response.ok) throw new Error(payload.error || `The demo runner returned HTTP ${response.status}.`);
  if (!payload.id || !payload.status) throw new Error("The demo runner response is missing run details.");
  return payload;
}

function deleteCase(id) {
  const testCase = state.cases.find(item => item.id === id);
  if (!testCase) return;
  const confirmed = window.confirm(`Delete "${testCase.name}" (${testCase.id})?\n\nExisting execution reports will be kept.`);
  if (!confirmed) return;
  state.cases = state.cases.filter(item => item.id !== id);
  persistCases();
  showToast("Test case deleted. Existing reports were kept.");
}

function showReport(id) {
  const report = state.reports.find(item => item.id === id);
  if (!report) {
    showToast("That execution report could not be found.", true);
    return;
  }
  $("#report-title").textContent = report.title;
  $("#report-detail").innerHTML = `<div class="report-detail">
    <div class="detail-item"><small>Status</small><strong>${resultBadge(report.status)}</strong></div>
    <div class="detail-item"><small>Test case</small><strong>${escapeHtml(report.caseId)}</strong></div>
    <div class="detail-item"><small>Duration</small><strong>${escapeHtml(formatDuration(report.durationMs))}</strong></div>
    <div class="detail-item"><small>Executed</small><strong>${escapeHtml(formatDate(report.timestamp))}</strong></div>
    ${report.failureDetails ? `<div class="report-failure"><strong>Failure details</strong><br>${escapeHtml(report.failureDetails)}</div>` : ""}
  </div>`;
  $("#report-dialog").showModal();
}

document.addEventListener("click", event => {
  const nav = event.target.closest("[data-nav]");
  if (nav) {
    event.preventDefault();
    navigate(nav.dataset.nav);
    return;
  }
  const close = event.target.closest("[data-close]");
  if (close) {
    $(`#${close.dataset.close}`).close();
    return;
  }
  const action = event.target.closest("[data-action]");
  if (!action) return;
  const { action: name, id } = action.dataset;
  if (name === "add") openCaseDialog();
  if (name === "edit") openCaseDialog(state.cases.find(testCase => testCase.id === id));
  if (name === "delete") deleteCase(id);
  if (name === "run") runCase(id);
  if (name === "report") showReport(id);
});

$("#case-form").addEventListener("submit", saveCase);
$("#search-input").addEventListener("input", renderCases);
$("#module-filter").addEventListener("change", renderCases);
$("#priority-filter").addEventListener("change", renderCases);
$("#status-filter").addEventListener("change", renderCases);
$("#report-status-filter").addEventListener("change", () => renderReports(true));
$("#export-reports-button").addEventListener("click", exportVisibleReports);
$("#logout-button").addEventListener("click", () => {
  sessionStorage.removeItem(SESSION_KEY);
  $("#app-shell").classList.add("hidden");
  $("#login-screen").classList.remove("hidden");
  $("#login-form").reset();
});
document.addEventListener("keydown", event => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    navigate("cases");
    $("#search-input").focus();
  }
});

initializeLogin();
