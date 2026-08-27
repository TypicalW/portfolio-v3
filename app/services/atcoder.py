import re
import time

import requests
from bs4 import BeautifulSoup


# =========================
# CONFIG
# =========================

ATCODER_USERNAME = "Predictable"

ATCODER_HISTORY_URL = (
    "https://atcoder.jp/users/"
    f"{ATCODER_USERNAME}/history/json"
)

ATCODER_PROFILE_URL = (
    "https://atcoder.jp/users/"
    f"{ATCODER_USERNAME}"
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
# FETCH HISTORY
# =========================

def fetch_atcoder_history():

    response = requests.get(
        ATCODER_HISTORY_URL,
        timeout=10,
        headers=HEADERS,
    )

    response.raise_for_status()

    return response.json()


# =========================
# FETCH PROFILE
# =========================

def fetch_atcoder_profile():

    response = requests.get(
        ATCODER_PROFILE_URL,
        timeout=10,
        headers=HEADERS,
    )

    response.raise_for_status()

    return response.text


# =========================
# PARSE PROFILE
# =========================

def parse_atcoder_profile(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    rating = None
    highest_rating = None
    kyu = None
    global_rank = None


    # =========================
    # FIND PROFILE TABLE
    # =========================

    tables = soup.find_all("table")


    for table in tables:

        rows = table.find_all("tr")


        for row in rows:

            cells = row.find_all(
                ["th", "td"]
            )


            if len(cells) < 2:
                continue


            label = cells[0].get_text(
                " ",
                strip=True
            )

            value = cells[1].get_text(
                " ",
                strip=True
            )


            # =========================
            # GLOBAL RANK
            # =========================

            if label == "Rank":

                match = re.search(
                    r"(\d+)",
                    value
                )

                if match:

                    global_rank = int(
                        match.group(1)
                    )


            # =========================
            # RATING
            # =========================

            elif label == "Rating":

                match = re.search(
                    r"(\d+)",
                    value
                )

                if match:

                    rating = int(
                        match.group(1)
                    )


            # =========================
            # HIGHEST RATING
            # =========================

            elif label == "Highest Rating":

                match = re.search(
                    r"(\d+)",
                    value
                )

                if match:

                    highest_rating = int(
                        match.group(1)
                    )


                # =========================
                # KYU
                # =========================

                kyu_match = re.search(
                    r"(\d+\s+Kyu)",
                    value,
                    re.IGNORECASE
                )

                if kyu_match:

                    kyu = kyu_match.group(1)


    return {

        "rating":
            rating,

        "kyu":
            kyu,

        "highest_rating":
            highest_rating,

        "global_rank":
            global_rank,

    }


# =========================
# FORMAT DATA
# =========================

def format_atcoder_data(
    history,
    profile
):

    contest_history = []


    for contest in history:

        contest_history.append({

            "contest":
                contest.get(
                    "ContestName"
                ),

            "rank":
                contest.get(
                    "Place"
                ),

            "old_rating":
                contest.get(
                    "OldRating"
                ),

            "rating":
                contest.get(
                    "NewRating"
                ),

            "performance":
                contest.get(
                    "Performance"
                ),

            "date":
                contest.get(
                    "EndTime"
                ),

        })


    return {

        "username":
            ATCODER_USERNAME,

        "rating":
            profile["rating"],

        "kyu":
            profile["kyu"],

        "highest_rating":
            profile["highest_rating"],

        "global_rank":
            profile["global_rank"],

        "contests":
            len(history),

        "history":
            contest_history,

    }


# =========================
# PUBLIC SERVICE FUNCTION
# =========================

def get_atcoder_stats():

    current_time = time.time()


    # =========================
    # RETURN CACHED DATA
    # =========================

    if (
        _cache["data"] is not None
        and
        current_time - _cache["timestamp"]
        < CACHE_DURATION
    ):

        return _cache["data"]


    # =========================
    # FETCH FRESH DATA
    # =========================

    try:

        history = (
            fetch_atcoder_history()
        )


        profile_html = (
            fetch_atcoder_profile()
        )


        profile = (
            parse_atcoder_profile(
                profile_html
            )
        )


        formatted_data = (
            format_atcoder_data(
                history,
                profile
            )
        )


        _cache["data"] = formatted_data

        _cache["timestamp"] = (
            current_time
        )


        return formatted_data


    except Exception as error:

        print(
            "AtCoder API error:",
            error
        )


        # =========================
        # FALL BACK TO STALE CACHE
        # =========================

        if _cache["data"] is not None:

            return _cache["data"]


        return None