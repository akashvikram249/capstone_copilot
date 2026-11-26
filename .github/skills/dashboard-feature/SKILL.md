---
name: dashboard-feature
description: "Implement and check changes to the test case dashboard: case CRUD, search and filters, simulated runs, execution reports and styling."
argument-hint: "Dashboard feature or acceptance criterion"
---

# Dashboard feature

1. Read [requirements.md](../../../requirements.md), [architecture.md](../../../architecture.md) and [design-review.md](../../../design-review.md).
2. Work out which acceptance criterion the change affects.
3. Keep to the existing split: the Java HTTP service and demo runner on one side, browser state and UI in `src/main/resources/static/` on the other.
4. Keep duplicate-ID validation, report history after a case is deleted, browser-only storage, and the clear labels on what is demo-only.
5. Escape any untrusted value before it goes into HTML, and show missing or invalid data instead of hiding it.
6. Add or update tests in `src/test/java/`.
7. Run `mvn test` and report the command and what it actually returned.
8. If behavior or scope changed, update the README and design docs.
