#!/usr/bin/env python3
"""Verify, commit, push, and open a pull request for an approved SDLC story.

Every PR it opens or finds is labelled "ai-generated".

Exit codes: 0 PR opened (or already open) and labelled, 1 precondition/verification failure,
3 branch pushed but no PR could be created (no gh CLI or token available),
4 PR opened but the ai-generated label could not be applied.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

REQUIRED_SECTIONS = [
    "## Summary",
    "## Changes Made",
    "## Test Evidence",
    "## Known Limitations",
    "## Reviewer Checklist",
]

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)authorization:\s*basic\s+[A-Za-z0-9+/=]{20,}"),
]
BLOCKED_FILE = re.compile(r"(^|/)(\.env(\..*)?|[^/]*\.(pem|key|p12|jks)|credentials(\.[^/]*)?)$")
SAFE_SUFFIXES = (".example", ".sample", ".template")

AI_LABEL = "ai-generated"
AI_LABEL_COLOR = "7057ff"
AI_LABEL_DESCRIPTION = "Pull request created with AI assistance"


class Fail(Exception):
    pass


def git(*args, check=True):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise Fail(f"git {' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def slugify(text, max_len=40):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len].strip("-")


def branch_name(story, title):
    return f"story/{slugify(story, 20)}-{slugify(title)}".rstrip("-")


def choose_branch(story, title, current, base, explicit):
    if explicit:
        return explicit
    if current in (base, "HEAD"):
        return branch_name(story, title)
    if current.startswith(f"story/{slugify(story, 20)}-"):
        return current
    raise Fail(
        f"on branch '{current}', which is not this story's branch; switch to '{base}' "
        f"(git switch {base} && git pull) so a new story branch is created, or pass --branch"
    )


def parse_remote(url):
    match = re.match(
        r"^(?:https://(?:[^@/]+@)?github\.com/|git@github\.com:|ssh://git@github\.com/)"
        r"([^/]+)/([^/]+?)(?:\.git)?/?$",
        url,
    )
    if not match:
        raise Fail(f"origin is not a github.com remote: {url}")
    return match.group(1), match.group(2)


def compare_url(owner, repo, base, branch, title):
    return (
        f"https://github.com/{owner}/{repo}/compare/{base}...{urllib.parse.quote(branch, safe='/')}"
        f"?expand=1&title={urllib.parse.quote(title)}"
    )


def scan_staged():
    problems = []
    for name in git("diff", "--cached", "--name-only").splitlines():
        if BLOCKED_FILE.search(name) and not name.endswith(SAFE_SUFFIXES):
            problems.append(f"credential-like file staged: {name}")
    for line in git("diff", "--cached", "-U0").splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            for pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    problems.append(f"possible secret in added line: {line[:60]}...")
                    break
    return problems


def default_base():
    ref = git("symbolic-ref", "--quiet", "refs/remotes/origin/HEAD", check=False)
    return ref.rsplit("/", 1)[-1] if ref else "main"


def validate_body(path):
    if not os.path.isfile(path):
        raise Fail(f"PR body file not found: {path}")
    with open(path, encoding="utf-8") as handle:
        body = handle.read()
    missing = [s for s in REQUIRED_SECTIONS if s not in body]
    if missing:
        raise Fail(f"PR body is missing required sections: {', '.join(missing)}")
    return body


def run_verification():
    if not shutil.which("mvn"):
        raise Fail("mvn not found; cannot produce verification evidence")
    print("Running mvn --batch-mode verify ...", flush=True)
    if subprocess.run(["mvn", "--batch-mode", "-q", "verify"]).returncode != 0:
        raise Fail("mvn verify failed; refusing to publish")


def api_request(method, url, token, payload=None):
    request = urllib.request.Request(
        url,
        method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "capstone-sdlc-pr-agent",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read() or b"{}")


def create_pr_with_gh(base, branch, title, body_file):
    created = subprocess.run(
        ["gh", "pr", "create", "--base", base, "--head", branch, "--title", title, "--body-file", body_file],
        capture_output=True, text=True,
    )
    if created.returncode == 0:
        return created.stdout.strip().splitlines()[-1]
    existing = subprocess.run(
        ["gh", "pr", "view", branch, "--json", "url", "-q", ".url"], capture_output=True, text=True
    )
    if existing.returncode == 0 and existing.stdout.strip():
        return existing.stdout.strip()
    raise Fail(f"gh pr create failed: {created.stderr.strip()}")


def create_pr_with_token(owner, repo, base, branch, title, body, token):
    api = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    status, data = api_request("POST", api, token, {"title": title, "head": branch, "base": base, "body": body})
    if status == 201:
        return data["html_url"]
    status, existing = api_request("GET", f"{api}?state=open&head={owner}:{branch}", token)
    if status == 200 and existing:
        return existing[0]["html_url"]
    raise Fail(f"GitHub API could not create the PR: {data.get('message', status)}")


def label_pr_with_gh(url):
    # Fails harmlessly when the label already exists.
    subprocess.run(
        ["gh", "label", "create", AI_LABEL, "--color", AI_LABEL_COLOR, "--description", AI_LABEL_DESCRIPTION],
        capture_output=True, text=True,
    )
    edited = subprocess.run(["gh", "pr", "edit", url, "--add-label", AI_LABEL], capture_output=True, text=True)
    if edited.returncode != 0:
        raise Fail(f"gh pr edit could not add the '{AI_LABEL}' label: {edited.stderr.strip()}")


def label_pr_with_token(owner, repo, url, token):
    api = f"https://api.github.com/repos/{owner}/{repo}"
    # 422 means the label already exists, which is fine.
    api_request(
        "POST", f"{api}/labels", token,
        {"name": AI_LABEL, "color": AI_LABEL_COLOR, "description": AI_LABEL_DESCRIPTION},
    )
    number = url.rstrip("/").rsplit("/", 1)[-1]
    status, data = api_request("POST", f"{api}/issues/{number}/labels", token, {"labels": [AI_LABEL]})
    if status not in (200, 201):
        raise Fail(f"GitHub API could not add the '{AI_LABEL}' label: {data.get('message', status)}")


def open_pr(owner, repo, base, branch, title, body_file, body):
    """Return (url, label_error); url is None when no PR route is available."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if shutil.which("gh") and subprocess.run(["gh", "auth", "status"], capture_output=True).returncode == 0:
        url = create_pr_with_gh(base, branch, title, body_file)
        label = lambda: label_pr_with_gh(url)
    elif token:
        url = create_pr_with_token(owner, repo, base, branch, title, body, token)
        label = lambda: label_pr_with_token(owner, repo, url, token)
    else:
        return None, None
    try:
        label()
    except Fail as err:
        return url, str(err)
    return url, None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--story", required=True, help="story id, e.g. US-102")
    parser.add_argument("--title", required=True, help="PR title")
    parser.add_argument("--body-file", required=True, help="completed PR description (markdown)")
    parser.add_argument("--base", help="target branch (default: origin HEAD, else main)")
    parser.add_argument("--branch", help="feature branch name (default: story/<id>-<title-slug>)")
    parser.add_argument("--commit-trailer", help="trailer line appended to the commit message")
    parser.add_argument("--approved", action="store_true", help="human approved publishing this story")
    parser.add_argument("--dry-run", action="store_true", help="report the plan without changing anything")
    args = parser.parse_args(argv)

    if not args.approved and not args.dry_run:
        raise Fail("publishing requires --approved (the human accepted verification and PR creation)")

    os.chdir(git("rev-parse", "--show-toplevel"))
    body = validate_body(args.body_file)
    owner, repo = parse_remote(git("remote", "get-url", "origin"))
    base = args.base or default_base()
    current = git("rev-parse", "--abbrev-ref", "HEAD")
    if current == base:
        git("fetch", "-q", "origin", base)
        behind = git("rev-list", "--count", f"{base}..origin/{base}", check=False) or "0"
        if behind != "0":
            raise Fail(f"local '{base}' is {behind} commit(s) behind origin/{base}; run 'git pull' first")
    branch = choose_branch(args.story, args.title, current, base, args.branch)
    if branch == base:
        raise Fail(f"refusing to publish directly from the base branch '{base}'")

    pending = git("status", "--porcelain")
    ahead = git("rev-list", "--count", f"origin/{base}..HEAD", check=False) or "0"
    if not pending and ahead == "0":
        raise Fail("nothing to publish: no pending changes and no commits ahead of base")

    if args.dry_run:
        has_gh = bool(shutil.which("gh"))
        has_token = bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
        print(f"[dry-run] repo={owner}/{repo} base={base} branch={branch} (current={current})")
        print(f"[dry-run] pending changes:\n{pending or '  (none)'}\n[dry-run] commits ahead of base: {ahead}")
        print(f"[dry-run] PR route: {'gh' if has_gh else 'token' if has_token else 'compare URL only'}")
        print(f"[dry-run] PR label: {AI_LABEL}")
        return 0

    run_verification()

    if current != branch:
        git("switch", "-c", branch)
    if pending:
        git("add", "-A")
        problems = scan_staged()
        if problems:
            git("reset", "-q")
            raise Fail("refusing to commit:\n  " + "\n  ".join(problems))
        message = [f"{args.story}: {args.title}"] + ([args.commit_trailer] if args.commit_trailer else [])
        git("commit", *[part for text in message for part in ("-m", text)])
    git("push", "-u", "origin", branch)

    url, label_error = open_pr(owner, repo, base, branch, args.title, args.body_file, body)
    if url:
        print(f"PR_URL={url}")
        if label_error:
            print(f"PR_LABEL_MISSING: {label_error}")
            print(f"Add the '{AI_LABEL}' label to the PR manually.")
            return 4
        print(f"PR_LABEL={AI_LABEL}")
        return 0
    print(f"BRANCH_PUSHED={branch}")
    print("PR NOT CREATED: no authenticated gh CLI and no GITHUB_TOKEN/GH_TOKEN.")
    print(f"Open it manually: {compare_url(owner, repo, base, branch, args.title)}")
    print(f"Paste the description from: {args.body_file}")
    return 3


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as err:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)
