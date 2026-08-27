import os
import time

import requests
from dotenv import load_dotenv


load_dotenv()


GITHUB_USERNAME = "TypicalW"
GITHUB_API = "https://api.github.com"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


CACHE_DURATION = 600  # 10 minutes

_cached_commits = None
_cache_time = 0


def get_recent_commits(limit=4):
    global _cached_commits, _cache_time

    current_time = time.time()

    # Return cached data if it is still valid
    if (
        _cached_commits is not None
        and current_time - _cache_time < CACHE_DURATION
    ):
        return _cached_commits[:limit]

    events_url = f"{GITHUB_API}/users/{GITHUB_USERNAME}/events/public"

    response = requests.get(
        events_url,
        params={"per_page": 100},
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    events = response.json()

    commits = []

    for event in events:
        if event["type"] != "PushEvent":
            continue

        repo = event["repo"]["name"]
        before = event["payload"]["before"]
        head = event["payload"]["head"]

        if before == head:
            continue

        compare_url = (
            f"{GITHUB_API}/repos/{repo}/compare/{before}...{head}"
        )

        compare_response = requests.get(
            compare_url,
            headers=HEADERS,
            timeout=10
        )

        compare_response.raise_for_status()

        compare_data = compare_response.json()

        for commit in compare_data.get("commits", []):
            commit_url = (
                f"{GITHUB_API}/repos/{repo}/commits/{commit['sha']}"
            )

            commit_response = requests.get(
                commit_url,
                headers=HEADERS,
                timeout=10
            )

            commit_response.raise_for_status()

            commit_data = commit_response.json()

            commits.append({
                "repo": repo.split("/")[-1],
                "message": commit["commit"]["message"].split("\n")[0],
                "additions": commit_data["stats"]["additions"],
                "deletions": commit_data["stats"]["deletions"],
            })

            if len(commits) >= limit:
                _cached_commits = commits
                _cache_time = current_time
                return commits[:limit]

    _cached_commits = commits
    _cache_time = current_time

    return commits[:limit]