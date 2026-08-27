from flask import (
    Flask,
    render_template,
    request
)
from app.services.github import get_recent_commits
from app.services.analytics import (
    record_view,
    get_total_views,
    record_click,
    get_total_clicks,
    get_user_clicks,
    record_time,
    get_user_time,
)
from app.services.leetcode import get_leetcode_stats

app = Flask(__name__)



SOCIALS = {
    "github": "https://github.com/TypicalW",
    "linkedin": "https://www.linkedin.com/in/ashmitmishra/",
    "x": "https://x.com/Typical__W",
    "codeforces": "https://codeforces.com/profile/TypicalW",
    "leetcode": "https://leetcode.com/u/TypicalW/"
}

CONTACT = {
    "contact": "ashmit1665@gmail.com"
}



@app.context_processor
def inject_globals():
    return {
        "socials": SOCIALS,
        "contact":CONTACT
    }



@app.route("/")
def home():

    recent_commits = get_recent_commits()

    record_view()

    total_views = get_total_views()
    total_clicks = get_total_clicks()

    leetcode_stats = get_leetcode_stats()

    return render_template(
        "index.html",
        recent_commits=recent_commits,
        total_views=total_views,
        total_clicks=total_clicks,
        leetcode_stats=leetcode_stats
    )


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/projects/")
def projects():
    return render_template("projects.html")

@app.route("/socials")
def socials():
    return render_template("socials.html")


@app.route("/api/click", methods=["POST"])
def click():
    data = request.get_json()
    visitor_id = data.get("visitor_id")

    record_click(visitor_id)

    return {
        "clicks": get_total_clicks(),
        "user_clicks": get_user_clicks(visitor_id)
    }

@app.route("/api/clicks", methods=["GET"])
def get_clicks():
    visitor_id = request.args.get("visitor_id")

    if not visitor_id:
        return {"error": "Missing visitor ID"}, 400

    return {
        "user_clicks": get_user_clicks(visitor_id)
    }

@app.route("/api/time", methods=["POST"])
def time():
    data = request.get_json()

    visitor_id = data.get("visitor_id")
    duration_seconds = data.get("duration_seconds")

    if not visitor_id:
        return {"error": "Missing visitor ID"}, 400

    if not isinstance(duration_seconds, int) or duration_seconds <= 0:
        return {"error": "Invalid duration"}, 400

    record_time(visitor_id, duration_seconds)

    return {
        "user_time": get_user_time(visitor_id)
    }


if __name__ == "__main__":
    app.run(debug=True)