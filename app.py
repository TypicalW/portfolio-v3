from flask import (
    Flask,
    render_template
)

app = Flask(__name__)



SOCIALS = {
    "github": "https://github.com/TypicalW",
    "linkedin": "https://www.linkedin.com/in/ashmitmishra/",
    "x": "https://x.com/Typical__W",
    "codeforces": "https://codeforces.com/profile/TypicalW",
}



@app.context_processor
def inject_globals():
    return {
        "socials": SOCIALS,
    }



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/projects/")
def projects():
    return render_template("projects.html")



if __name__ == "__main__":
    app.run(debug=True)