from flask import (
    Flask,
    render_template,
)
from app.services.github import get_recent_commits

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

    return render_template(
        "index.html",
        recent_commits=recent_commits
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


if __name__ == "__main__":
    app.run(debug=True)