import time

import requests


# =========================
# CONFIG
# =========================

CODEFORCES_USERNAME = "TypicalW"

CODEFORCES_API_URL = (
    "https://codeforces.com/api"
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
# HEADERS
# =========================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0.0.0 "
        "Safari/537.36"
    )
}


# =========================
# API REQUEST
# =========================

def fetch_codeforces_api(
    method,
    params
):

    response = requests.get(
        f"{CODEFORCES_API_URL}/{method}",
        params=params,
        headers=HEADERS,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("status") != "OK":

        raise RuntimeError(
            data.get(
                "comment",
                "Codeforces API request failed"
            )
        )

    return data["result"]


# =========================
# FETCH USER INFO
# =========================

def fetch_user_info():

    result = fetch_codeforces_api(
        "user.info",
        {
            "handles":
                CODEFORCES_USERNAME
        }
    )

    if not result:

        raise RuntimeError(
            "Codeforces user not found"
        )

    return result[0]


# =========================
# FETCH RATING HISTORY
# =========================

def fetch_user_rating_history():

    return fetch_codeforces_api(
        "user.rating",
        {
            "handle":
                CODEFORCES_USERNAME
        }
    )


# =========================
# FETCH SUBMISSIONS
# =========================

def fetch_user_submissions():

    submissions = []

    start = 1

    batch_size = 1000


    while True:

        batch = fetch_codeforces_api(
            "user.status",
            {
                "handle":
                    CODEFORCES_USERNAME,

                "from":
                    start,

                "count":
                    batch_size,
            }
        )


        if not batch:

            break


        submissions.extend(
            batch
        )


        if len(batch) < batch_size:

            break


        start += batch_size


    return submissions


# =========================
# COUNT SOLVED PROBLEMS
# =========================

def count_solved_problems(
    submissions
):

    solved_problems = set()


    for submission in submissions:

        if submission.get(
            "verdict"
        ) != "OK":

            continue


        problem = submission.get(
            "problem"
        )


        if not problem:

            continue


        contest_id = problem.get(
            "contestId"
        )

        problem_index = problem.get(
            "index"
        )


        if (
            contest_id is None
            or
            problem_index is None
        ):

            continue


        solved_problems.add(
            (
                contest_id,
                problem_index
            )
        )


    return len(
        solved_problems
    )


# =========================
# BUILD CONTEST HISTORY
# =========================

def build_contest_history(
    rating_history
):

    history = []


    for contest in rating_history:

        history.append({

            "contest_id":
                contest.get(
                    "contestId"
                ),

            "contest":
                contest.get(
                    "contestName"
                ),

            "rating":
                contest.get(
                    "newRating"
                ),

            "date":
                contest.get(
                    "ratingUpdateTimeSeconds"
                ),

        })


    return history


# =========================
# FORMAT DATA
# =========================

def format_codeforces_data(
    user,
    submissions,
    rating_history
):

    solved = count_solved_problems(
        submissions
    )


    history = build_contest_history(
        rating_history
    )


    return {

        "username":
            user.get(
                "handle"
            ),

        "rating":
            user.get(
                "rating"
            ),

        "rank":
            user.get(
                "rank"
            ),

        "highest_rating":
            user.get(
                "maxRating"
            ),

        "solved":
            solved,

        "history":
            history,

    }


# =========================
# PUBLIC SERVICE FUNCTION
# =========================

def get_codeforces_stats():

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

        user = fetch_user_info()


        submissions = (
            fetch_user_submissions()
        )


        rating_history = (
            fetch_user_rating_history()
        )


        formatted_data = (
            format_codeforces_data(
                user,
                submissions,
                rating_history
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
            "Codeforces API error:",
            error
        )


        # =========================
        # FALL BACK TO CACHE
        # =========================

        if _cache["data"] is not None:

            return _cache["data"]


        return None