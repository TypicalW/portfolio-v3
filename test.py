from app.services.unified_contest import (
    get_unified_contest_history
)


history = get_unified_contest_history()


print()
print("=" * 50)
print("UNIFIED CONTEST HISTORY")
print("=" * 50)


for contest in history:

    print(
        contest["platform"],
        "|",
        contest["contest"],
        "| Rating:",
        contest["rating_after_contest"],
        "| Date:",
        contest["date"]
    )