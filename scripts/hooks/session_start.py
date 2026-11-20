#!/usr/bin/env python3
"""Print concise SDLC guidance and repository state at session start."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def git_output(*arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *arguments],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or f"git exited with status {result.returncode}"
        raise RuntimeError(f"Could not inspect repository state: {detail}")
    return result.stdout.strip()


def main() -> int:
    try:
        branch = git_output("branch", "--show-current") or "(detached HEAD)"
        status = git_output("status", "--short")
    except RuntimeError as error:
        print(f"SDLC session context unavailable: {error}", file=sys.stderr)
        return 1

    print("SDLC workspace context:")
    print(f"- Repository: {ROOT.name}")
    print(f"- Branch: {branch}")
    print(f"- Worktree: {'clean' if not status else 'has existing changes (preserve them)'}")
    print("- Pipeline guide: SDLC-PIPELINE.md")
    print("- Orchestrator: select “SDLC Orchestrator” in Copilot Chat.")
    print("- Follow the approved phase and pause at human approval gates.")
    print("- Do not commit, push, deploy, or open a PR without explicit approval; the final-gate approval lets the PR agent raise the PR via scripts/pr/raise_pr.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
