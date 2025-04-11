import os
from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Event Service URL (Ensure it's set in .env)
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://127.0.0.1:5005")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Home Route
@app.route("/")
def home():
    return render_template("index.html")

# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]  # Assuming your signup requires a name

        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if response.user:
                return redirect(url_for("login"))
            else:
                return render_template("signup.html", error="Signup failed")
        except Exception as e:
            return render_template("signup.html", error=str(e))

    return render_template("signup.html")

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response.session:
                session["token"] = response.session.access_token
                return redirect(url_for("profile"))
            else:
                return render_template("login.html", error="Login failed")
        except Exception as e:
            return render_template("login.html", error=str(e))

    return render_template("login.html")

# Profile Route
@app.route("/profile")
def profile():
    token = session.get("token")
    if not token:
        return redirect(url_for("login"))

    try:
        user = supabase.auth.get_user(token)
        if user.user:
            return render_template("profile.html", user=user.user)
        else:
            session.pop("token", None)
            return redirect(url_for("login"))
    except Exception as e:
        session.pop("token", None)
        return redirect(url_for("login"))


# Logout Route
@app.route("/logout")
def logout():
    session.pop("token", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=5858)
