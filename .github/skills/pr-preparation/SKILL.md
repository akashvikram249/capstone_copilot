---
name: pr-preparation
description: "Prepare a truthful pull request summary, changes list, test evidence, known limitations, changelog, and reviewer checklist from verified work, then raise the PR once publishing is approved."
argument-hint: "Verified diff, actual test evidence, and whether publishing is approved"
---

# PR Preparation and Publishing Phase

1. Read the approved story, verified diff, verification results, known limitations, changelog, and PR template.
2. Draft a 2–3 sentence summary explaining what changed and why.
3. List files changed and their purpose; include only files present in the diff.
4. Include exact test evidence and CI links only when they exist.
5. List unresolved findings, missing evidence, out-of-scope behavior, or "Not Found" outcomes as limitations.
6. Add a concise changelog entry and a reviewer checklist mapped to acceptance/security/test requirements.
7. Write the completed description to `target/pr-body.md` (git-ignored). It must keep all five template sections.
8. If the human has approved publishing (verification accepted and PR creation authorized), run:

   ```bash
   python3 scripts/pr/raise_pr.py --story <US-ID> --title "<PR title>" --body-file target/pr-body.md --approved
   ```

   Use `--dry-run` first if the branch or pending changes look unexpected. The script re-runs `mvn --batch-mode verify`, creates `story/<id>-<slug>` from the base branch, commits, scans for secrets, pushes, and opens the PR (via `gh`, then `GITHUB_TOKEN`/`GH_TOKEN`).
9. Report the outcome exactly: the `PR_URL=` value, or "branch pushed, PR NOT created" with the printed compare link when no GitHub credentials exist (exit code 3), or the script's error.

If publishing is not approved, stop after step 7 and say the PR is prepared locally only. Do not write code, and do not claim a PR was opened unless the script printed `PR_URL=`.
