import os
import time

import requests
from dotenv import load_dotenv


load_dotenv()


GITHUB_USERNAME = "TypicalW"
KATIB_API = "https://katib.jsn.cam/v2/commits/latest"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/json",
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

    response = requests.get(
        KATIB_API,
        params={
            "username": GITHUB_USERNAME,
            "limit": limit,
        },
        headers=HEADERS,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    commits = []

    for commit in data.get("commits", []):
        commits.append({
            "repo": commit["repo"],
            "message": commit["messageHeadline"],
            "additions": commit["additions"],
            "deletions": commit["deletions"],
        })

    _cached_commits = commits
    _cache_time = current_time

    return commits[:limit]