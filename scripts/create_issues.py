import json
import os
import re
import subprocess
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def get_owner_repo_from_origin() -> tuple[str, str]:
    try:
        origin_url = (
            subprocess.check_output(["git", "remote", "get-url", "origin"], text=True)
            .strip()
        )
    except subprocess.CalledProcessError as exc:
        print(f"Failed to read git remote: {exc}", file=sys.stderr)
        sys.exit(1)

    # Normalize URL to extract owner/repo
    # Handles formats like:
    # https://x-access-token:***@github.com/owner/repo(.git)
    # https://github.com/owner/repo(.git)
    # git@github.com:owner/repo.git
    owner = None
    repo = None

    # SSH format
    m = re.search(r"github\.com:([^/]+)/([^\.\s]+)(?:\.git)?$", origin_url)
    if m:
        owner, repo = m.group(1), m.group(2)
    else:
        # HTTPS format
        m = re.search(r"github\.com/([^/]+)/([^\.\s]+)(?:\.git)?", origin_url)
        if m:
            owner, repo = m.group(1), m.group(2)

    if not owner or not repo:
        print(f"Could not parse owner/repo from origin URL: {origin_url}", file=sys.stderr)
        sys.exit(1)

    return owner, repo


def read_issue_file(path: str) -> tuple[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    if not lines:
        print(f"Issue file is empty: {path}", file=sys.stderr)
        sys.exit(1)

    # Expect first line like: "## Feature: Tournaments — Rack ’em up"
    title_line = lines[0].strip()
    title = title_line
    m = re.match(r"^##\s+Feature:\s+(.*)$", title_line)
    if m:
        title = m.group(1).strip()

    return title, content


def create_issue(owner: str, repo: str, token: str, title: str, body: str) -> str:
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    payload = json.dumps({"title": title, "body": body}).encode("utf-8")
    req = Request(api_url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Content-Type", "application/json")

    try:
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("html_url", "")
    except HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"GitHub API error {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    token = os.environ.get("GH_TOKEN")
    if not token:
        print("GH_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)

    owner, repo = get_owner_repo_from_origin()

    files = [
        "/workspace/docs/issues/001-tournament-feature.md",
        "/workspace/docs/issues/002-venues-feature.md",
    ]

    results: list[tuple[str, str]] = []
    for path in files:
        title, body = read_issue_file(path)
        url = create_issue(owner, repo, token, title, body)
        results.append((path, url))

    # Print machine-readable results
    print(json.dumps({"issues": [{"file": p, "url": u} for p, u in results]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

