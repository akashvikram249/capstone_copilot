---
name: pr-preparation
description: "Write the pull request description, changelog entry and reviewer checklist from verified work, then raise the PR once publishing is approved."
argument-hint: "Verified diff, actual test evidence, and whether publishing is approved"
---

# PR preparation and publishing

1. Read the approved story, the verified diff, the verification results, the known limitations, the changelog and the PR template.
2. Write a two to three sentence summary of what changed and why.
3. List the changed files and what each change is for. Only list files that are in the diff.
4. Put in the exact test results. Add CI links only if CI actually ran.
5. List what is unresolved, what has no evidence, what is out of scope, and any "Not Found" results under limitations.
6. Add a short changelog entry and a reviewer checklist tied to the acceptance, security and test requirements.
7. Write the finished description to `target/pr-body.md` (git-ignored). Keep all five template sections.
8. If the human accepted the verification and authorized the PR, run:

   ```bash
   python3 scripts/pr/raise_pr.py --story <US-ID> --title "<PR title>" --body-file target/pr-body.md --approved
   ```

   Run it with `--dry-run` first if the branch or the pending changes look wrong. The script re-runs `mvn --batch-mode verify`, creates `story/<id>-<slug>` from the base branch, scans for secrets, commits, pushes, and opens the PR through `gh`, or through `GITHUB_TOKEN`/`GH_TOKEN` if `gh` isn't signed in. It also puts the `ai-generated` label on the PR, because AI helped write it.
9. Report exactly what happened:
   - `PR_URL=` and `PR_LABEL=ai-generated` both printed: the PR is open and labelled.
   - `PR_URL=` with `PR_LABEL_MISSING` (exit code 4): the PR is open but unlabelled. Say so and ask for the label to be added by hand.
   - Exit code 3: the branch was pushed, but no PR was created. Give the compare link it printed.
   - Anything else: the script's own error.

If publishing wasn't approved, stop after step 7 and say the PR is only prepared locally. Don't write code, and don't say a PR was opened unless the script printed `PR_URL=`.
