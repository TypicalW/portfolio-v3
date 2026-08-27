import json
import time
from datetime import datetime, timedelta

import requests


# =========================
# CONFIG
# =========================

LEETCODE_USERNAME = "TypicalW"

LEETCODE_GRAPHQL_URL = (
    "https://leetcode.com/graphql"
)

CACHE_DURATION = 600  # 10 minutes


# =========================
# CACHE
# =========================

_cache = {
    "data": None,
    "timestamp": 0,
}


# =========================
# GRAPHQL QUERY
# =========================

QUERY = """
query getUserStats($username: String!) {

    matchedUser(username: $username) {

        username

        submitStats: submitStatsGlobal {

            acSubmissionNum {
                difficulty
                count
                submissions
            }

        }

        userCalendar {

            activeYears
            streak
            totalActiveDays
            submissionCalendar

        }

    }


    userContestRanking(username: $username) {

        attendedContestsCount
        rating
        globalRanking
        totalParticipants
        topPercentage

    }


    userContestRankingHistory(username: $username) {

        attended

        rating

        contest {

            title
            startTime

        }

    }

}
"""


# =========================
# FETCH DATA
# =========================

def fetch_leetcode_data():

    headers = {
        "Content-Type": "application/json",

        "Referer": (
            f"https://leetcode.com/u/"
            f"{LEETCODE_USERNAME}/"
        ),

        "User-Agent": (
            "Mozilla/5.0 "
            "(X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151.0.0.0 "
            "Safari/537.36"
        ),
    }


    payload = {
        "query": QUERY,

        "variables": {
            "username": LEETCODE_USERNAME
        },
    }


    response = requests.post(
        LEETCODE_GRAPHQL_URL,
        json=payload,
        headers=headers,
        timeout=10,
    )


    response.raise_for_status()


    result = response.json()


    if "errors" in result:

        raise RuntimeError(
            result["errors"]
        )


    return result["data"]


# =========================
# BUILD CONTEST HISTORY
# =========================

def build_contest_history(
    history
):

    contests = []


    if not history:

        return contests


    for contest in history:

        if not contest.get(
            "attended"
        ):

            continue


        contest_info = contest.get(
            "contest"
        )


        if not contest_info:

            continue


        title = contest_info.get(
            "title"
        )


        start_time = contest_info.get(
            "startTime"
        )


        rating = contest.get(
            "rating"
        )


        if (
            title is None
            or
            start_time is None
            or
            rating is None
        ):

            continue


        # LeetCode returns the contest
        # start time as a Unix timestamp.

        date = datetime.fromtimestamp(
            int(start_time)
        ).isoformat()


        contests.append({

            "contest":
                title,

            "rating":
                round(rating),

            "date":
                date,

        })


    return contests


# =========================
# FORMAT DATA
# =========================

def format_leetcode_data(
    data
):

    user = data["matchedUser"]


    # =========================
    # SOLVED
    # =========================

    submit_stats = (
        user["submitStats"]["acSubmissionNum"]
    )


    solved = 0


    for difficulty in submit_stats:

        if (
            difficulty["difficulty"]
            == "All"
        ):

            solved = difficulty["count"]

            break


    # =========================
    # SUBMISSION CALENDAR
    # =========================

    calendar = user["userCalendar"]


    submission_calendar = json.loads(
        calendar["submissionCalendar"]
    )


    # =========================
    # LAST 60 DAYS HEATMAP
    # =========================

    submissions_by_date = {}


    for timestamp, count in (
        submission_calendar.items()
    ):

        date = datetime.fromtimestamp(
            int(timestamp)
        ).date()


        submissions_by_date[
            date.isoformat()
        ] = count


    heatmap = []


    today = datetime.now().date()


    for days_ago in range(
        59,
        -1,
        -1
    ):

        current_date = (
            today
            - timedelta(
                days=days_ago
            )
        )


        date_string = (
            current_date.isoformat()
        )


        count = submissions_by_date.get(
            date_string,
            0
        )


        # =========================
        # HEAT LEVEL
        # =========================

        if count == 0:

            level = 0

        elif count <= 5:

            level = 1

        elif count <= 15:

            level = 2

        else:

            level = 3


        heatmap.append({

            "date":
                date_string,

            "count":
                count,

            "level":
                level

        })


    # =========================
    # CONTEST RATING
    # =========================

    contest = data.get(
        "userContestRanking"
    )


    rating = None


    if contest:

        rating = round(
            contest["rating"]
        )


    # =========================
    # CONTEST HISTORY
    # =========================

    contest_history = (
        data.get(
            "userContestRankingHistory"
        )
    )


    history = build_contest_history(
        contest_history
    )


    # =========================
    # RETURN
    # =========================

    return {

        "username":
            user["username"],


        "solved":
            solved,


        "rating":
            rating,


        "global_rank": (
            contest["globalRanking"]
            if contest
            else None
        ),


        "submission_calendar":
            submission_calendar,


        "heatmap":
            heatmap,


        "streak":
            calendar["streak"],


        "total_active_days":
            calendar["totalActiveDays"],


        "history":
            history,

    }


# =========================
# PUBLIC SERVICE FUNCTION
# =========================

def get_leetcode_stats():

    current_time = time.time()


    # =========================
    # RETURN CACHED DATA
    # =========================

    if (
        _cache["data"] is not None
        and
        current_time
        - _cache["timestamp"]
        < CACHE_DURATION
    ):

        return _cache["data"]


    # =========================
    # FETCH FRESH DATA
    # =========================

    try:

        raw_data = fetch_leetcode_data()


        formatted_data = (
            format_leetcode_data(
                raw_data
            )
        )


        _cache["data"] = (
            formatted_data
        )

        _cache["timestamp"] = (
            current_time
        )


        return formatted_data


    except Exception as error:

        print(
            "LeetCode API error:",
            error
        )


        # =========================
        # FALL BACK TO CACHE
        # =========================

        if _cache["data"] is not None:

            return _cache["data"]


        return None