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


# =========================
# CACHE
# =========================

_commit_cache = {
    "data": None,
    "timestamp": 0,
}

CACHE_DURATION = 600  # 10 minutes


def get_recent_commits(limit=4):

    now = time.time()

    # =========================
    # RETURN VALID CACHE
    # =========================

    if (
        _commit_cache["data"] is not None
        and now - _commit_cache["timestamp"] < CACHE_DURATION
    ):
        return _commit_cache["data"][:limit]


    # =========================
    # FETCH FROM KATIB
    # =========================

    try:

        response = requests.get(
            KATIB_API,
            params={
                "username": GITHUB_USERNAME,
                "limit": limit,
            },
            headers=HEADERS,
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        commits = data.get("commits", [])

        # =========================
        # UPDATE CACHE
        # =========================

        _commit_cache["data"] = commits
        _commit_cache["timestamp"] = now

        return commits[:limit]

    # =========================
    # FAILSAFE
    # =========================

    except requests.RequestException as error:

        print(f"GitHub/Katib request failed: {error}")

        # Return stale cache if available
        if _commit_cache["data"] is not None:
            print("Using cached GitHub commit data.")

            return _commit_cache["data"][:limit]

        # No cache available
        print("No cached GitHub commit data available.")

        return []