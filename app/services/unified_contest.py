import time
from datetime import datetime, timezone

from app.services.atcoder import get_atcoder_stats
from app.services.codeforces import get_codeforces_stats
from app.services.leetcode import get_leetcode_stats


# =========================
# CACHE
# =========================

_cache = {
    "data": None,
    "timestamp": 0,
}

CACHE_DURATION = 600  # 10 minutes


# =========================
# NORMALIZE DATE
# =========================

def normalize_date(date):

    if date is None:
        return None


    # =========================
    # CODEFORCES UNIX TIMESTAMP
    # =========================

    if isinstance(date, (int, float)):

        return datetime.fromtimestamp(
            date,
            tz=timezone.utc
        ).isoformat()


    # =========================
    # STRING DATE
    # =========================

    if isinstance(date, str):

        try:

            parsed_date = datetime.fromisoformat(
                date.replace(
                    "Z",
                    "+00:00"
                )
            )


            # LeetCode may return a
            # timezone-naive datetime.
            #
            # Treat it as UTC so it can
            # safely be compared with
            # AtCoder and Codeforces dates.

            if parsed_date.tzinfo is None:

                parsed_date = parsed_date.replace(
                    tzinfo=timezone.utc
                )


            # Convert everything to UTC.

            parsed_date = parsed_date.astimezone(
                timezone.utc
            )


            return parsed_date.isoformat()


        except ValueError:

            return None


    return None


# =========================
# CREATE CONTEST
# =========================

def create_contest(
    platform,
    name,
    rating,
    date
):

    normalized_date = normalize_date(
        date
    )


    return {

        "platform":
            platform,

        "contest":
            name,

        "rating_after_contest":
            rating,

        "date":
            normalized_date,

    }


# =========================
# GET UNIFIED HISTORY
# =========================

def get_unified_contest_history():

    current_time = time.time()


    # =========================
    # RETURN CACHE
    # =========================

    if (
        _cache["data"] is not None
        and
        current_time
        - _cache["timestamp"]
        < CACHE_DURATION
    ):

        return _cache["data"]


    contests = []


    # =========================
    # ATCODER
    # =========================

    try:

        atcoder = get_atcoder_stats()


        if atcoder:

            for contest in atcoder.get(
                "history",
                []
            ):

                contests.append(
                    create_contest(
                        "AtCoder",
                        contest.get(
                            "contest"
                        ),
                        contest.get(
                            "rating"
                        ),
                        contest.get(
                            "date"
                        ),
                    )
                )


    except Exception as error:

        print(
            "Unified history - AtCoder error:",
            error
        )


    # =========================
    # CODEFORCES
    # =========================

    try:

        codeforces = get_codeforces_stats()


        if codeforces:

            for contest in codeforces.get(
                "history",
                []
            ):

                contests.append(
                    create_contest(
                        "Codeforces",
                        contest.get(
                            "contest"
                        ),
                        contest.get(
                            "rating"
                        ),
                        contest.get(
                            "date"
                        ),
                    )
                )


    except Exception as error:

        print(
            "Unified history - Codeforces error:",
            error
        )


    # =========================
    # LEETCODE
    # =========================

    try:

        leetcode = get_leetcode_stats()


        if leetcode:

            for contest in leetcode.get(
                "history",
                []
            ):

                contests.append(
                    create_contest(
                        "LeetCode",
                        contest.get(
                            "contest"
                        ),
                        contest.get(
                            "rating"
                        ),
                        contest.get(
                            "date"
                        ),
                    )
                )


    except Exception as error:

        print(
            "Unified history - LeetCode error:",
            error
        )


    # =========================
    # REMOVE INVALID CONTESTS
    # =========================

    contests = [
        contest
        for contest in contests
        if (
            contest.get("date")
            is not None
        )
    ]


    # =========================
    # SORT NEWEST → OLDEST
    # =========================

    def sort_key(contest):

        date = contest.get(
            "date"
        )


        try:

            parsed_date = datetime.fromisoformat(
                date.replace(
                    "Z",
                    "+00:00"
                )
            )


            if parsed_date.tzinfo is None:

                parsed_date = parsed_date.replace(
                    tzinfo=timezone.utc
                )


            return parsed_date


        except (
            ValueError,
            AttributeError
        ):

            return datetime.min.replace(
                tzinfo=timezone.utc
            )


    contests.sort(
        key=sort_key,
        reverse=True
    )


    # =========================
    # KEEP LAST 5
    # =========================

    contests = contests[:5]


    # =========================
    # CACHE
    # =========================

    _cache["data"] = contests

    _cache["timestamp"] = (
        current_time
    )


    return contests