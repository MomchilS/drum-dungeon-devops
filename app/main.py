#from services.exercises import DAILY_EXERCISES
#from services.medals import medal_labels
#from fastapi import FastAPI, Request, Form
#from fastapi.responses import HTMLResponse, RedirectResponse
#from fastapi.templating import Jinja2Templates
#from fastapi.staticfiles import StaticFiles
#from starlette.middleware.sessions import SessionMiddleware
#from auth import DATA_DIR as BASE_DIR

#import json
#import shutil
#from pathlib import Path
#import os
#import sys
#from datetime import date, timedelta
#import subprocess


#from pathlib import Path
#from auth import load_users, verify_password, update_password
#from services.attendance import apply_attendance




from webapp.auth import DATA_DIR as BASE_DIR
from webapp.auth import load_users, verify_password, update_password

from pathlib import Path
import os
import sys
import json
import shutil
from datetime import date, timedelta
import subprocess

from webapp.services.exercises import DAILY_EXERCISES
from webapp.services.medals import medal_labels
from webapp.services.attendance import apply_attendance

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

# ✅ DEFINE DERIVED PATHS ONLY AFTER BASE_DIR IS SET
STUDENTS_DIR = BASE_DIR / "students"
LEADERBOARD_FILE = BASE_DIR / "leaderboard.json"



def format_minutes(total_minutes: int) -> str:
    if total_minutes < 60:
        return f"{total_minutes}m"
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}h {minutes}m"

def update_streak_on_practice(stats: dict):
    """
    Called when a student completes a practice.
    Updates current streak, longest streak, and last_practice_date.
    """
    today = date.today()
    last_date_str = stats["streak"].get("last_practice_date")

    if last_date_str:
        last_date = date.fromisoformat(last_date_str)
        delta = (today - last_date).days

        if delta == 0:
            # Already practiced today
            return

        elif delta == 1:
            stats["streak"]["current"] += 1
        else:
            stats["streak"]["current"] = 1
    else:
        # First practice ever
        stats["streak"]["current"] = 1

    if stats["streak"]["current"] > stats["streak"]["longest"]:
        stats["streak"]["longest"] = stats["streak"]["current"]

    stats["streak"]["last_practice_date"] = today.isoformat()


def validate_streak(stats: dict) -> bool:
    """
    Ensures the current streak is valid.
    Resets it to 0 if at least one day was missed.
    Returns True if the stats were modified.
    """
    last_date = stats["streak"].get("last_practice_date")

    if not last_date:
        return False

    last = date.fromisoformat(last_date)
    today = date.today()

    if today - last > timedelta(days=1):
        stats["streak"]["current"] = 0
        return True

    return False


# ---------------------------------------------------
# App & Session Middleware
# ---------------------------------------------------

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="CHANGE_THIS_SECRET_KEY"
)

# ---------------------------------------------------
# Templates & Static files
# ---------------------------------------------------

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

###BASE_DIR = Path(os.environ.get("PRACTICE_DATA_DIR", "/srv/practice-data"))


# ---------------------------------------------------
# Auth routes
# ---------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    users = load_users()
    user = users.get(username)

    if not user or not verify_password(password, user["password"]):
        return RedirectResponse("/", status_code=302)

    request.session["user"] = username
    request.session["role"] = user["role"]

    if user["role"] == "student" and user.get("force_change"):
        return RedirectResponse("/change-password", status_code=302)

    if user["role"] == "admin":
        return RedirectResponse("/admin/dashboard", status_code=302)

    return RedirectResponse("/student/dashboard", status_code=302)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

# ---------------------------------------------------
# Password change
# ---------------------------------------------------

@app.get("/change-password", response_class=HTMLResponse)
def change_password_form(request: Request):
    if request.session.get("role") != "student":
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        "change_password.html",
        {"request": request}
    )


@app.post("/change-password")
def change_password_submit(
    request: Request,
    password: str = Form(...),
    confirm: str = Form(...)
):
    if request.session.get("role") != "student":
        return RedirectResponse("/", status_code=302)

    if password != confirm:
        return RedirectResponse("/change-password", status_code=302)

    update_password(request.session["user"], password)
    return RedirectResponse("/student/dashboard", status_code=302)

# ---------------------------------------------------
# Admin routes
# ---------------------------------------------------

@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    if request.session.get("role") != "admin":
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request}
    )


@app.get("/admin/students", response_class=HTMLResponse)
def admin_students(request: Request):
    if request.session.get("role") != "admin":
        return RedirectResponse("/", status_code=302)

    students = sorted(d.name for d in STUDENTS_DIR.iterdir() if d.is_dir())

    return templates.TemplateResponse(
        "admin/students_list.html",
        {"request": request, "students": students}
    )


@app.get("/admin/attendance", response_class=HTMLResponse)
def admin_attendance_form(request: Request):
    if request.session.get("role") != "admin":
        return RedirectResponse("/", status_code=302)

    students = sorted(
        d.name for d in STUDENTS_DIR.iterdir() if d.is_dir()
    )

    return templates.TemplateResponse(
        "admin/attendance.html",
        {
            "request": request,
            "students": students,
        }
    )

from datetime import date as today_date
import json

@app.post("/admin/attendance")
def admin_attendance_submit(
    request: Request,
    student: str = Form(...),
    date: str = Form(...),
    grade: int = Form(...),
):
    if request.session.get("role") != "admin":
        return RedirectResponse("/", status_code=302)

    # Apply attendance XP
    apply_attendance(student, date)

    # Write history entry
    stats_file = STUDENTS_DIR / student / "stats.json"

    with open(stats_file, "r") as f:
        stats = json.load(f)

    history = stats.setdefault("history", {})
    events = history.setdefault("events", [])

    events.append({
        "type": "attendance",
        "name": "Private Lesson",
        "date": today_date.today().isoformat(),
        "grade": grade,        
    })

    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)

    return RedirectResponse(
        "/admin/attendance",
        status_code=302
    )

@app.get("/admin/dashboard/student-management", response_class=HTMLResponse)
def admin_student_management(request: Request):
    if request.session.get("role") != "admin":
        return RedirectResponse("/", status_code=302)

    students = sorted(
        d.name for d in STUDENTS_DIR.iterdir() if d.is_dir()
    )

    return templates.TemplateResponse(
        "admin/student_management.html",
        {
            "request": request,
            "students": students
        }
    )

@app.post("/admin/dashboard/student-management/remove")
def remove_student(
    request: Request,
    student: str = Form(...)
):
    if request.session.get("role") != "admin":
        return RedirectResponse("/", status_code=302)

    # 🔒 Prevent admin removing themselves
    if student == request.session.get("user"):
        return RedirectResponse(
            "/admin/dashboard/student-management",
            status_code=302
        )

    student_dir = STUDENTS_DIR / student

    if student_dir.exists() and student_dir.is_dir():
        shutil.rmtree(student_dir)

    # Remove from auth system
    from webapp.auth import delete_user
    delete_user(student)

    return RedirectResponse(
        "/admin/dashboard/student-management",
        status_code=302
    )

@app.post("/admin/dashboard/student-management/add")
def add_student(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    avatar: str = Form(...),
):
    if request.session.get("role") != "admin":
        return RedirectResponse("/", status_code=302)

    # 1) Create student using environment‑aware script
    env = {
        **os.environ,
        "PRACTICE_DATA_DIR": str(BASE_DIR),
    }

    result = subprocess.run(
        [
            sys.executable,
            str(BASE_DIR / "scripts" / "create_student.py"),
            username,
        ],
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("CREATE_STUDENT FAILED")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise RuntimeError("create_student.py failed")

    #if result.returncode != 0:
        #return RedirectResponse(
            #"/admin/dashboard/student-management",
            #status_code=302
        #)

    # 2) Add user to auth system
    from webapp.auth import add_user

    add_user(
        username=username,
        password=password,
        role="student",
        force_change=True,
    )

    # 3) Set avatar in stats.json
    stats_file = STUDENTS_DIR / username / "stats.json"

    with open(stats_file, "r") as f:
        stats = json.load(f)

    stats.setdefault("profile", {})["avatar"] = avatar

    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)

    return RedirectResponse(
        "/admin/dashboard/student-management",
        status_code=302
    )

# ---------------------------------------------------
# Student routes
# ---------------------------------------------------

@app.get("/student/dashboard", response_class=HTMLResponse)
def student_dashboard(request: Request):
    if request.session.get("role") != "student":
        return RedirectResponse("/", status_code=302)

    student = request.session["user"]
    stats_file = STUDENTS_DIR / student / "stats.json"

    with open(stats_file) as f:
        stats = json.load(f)

    # ✅ STREAK VALIDATION GOES HERE
    modified = validate_streak(stats)

    if modified:
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)

    return templates.TemplateResponse(
        "student/dashboard.html",
        {
            "request": request,
            "student": student,
            "stats": stats,
            "medals_map": medal_labels(),
            "exercises": DAILY_EXERCISES,
        },
    )

@app.get("/student/dashboard/daily-pad-exercises", response_class=HTMLResponse)
def daily_pad_exercises(request: Request):
    if request.session.get("role") != "student":
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        "student/daily_pad_exercises.html",
        {
            "request": request,
            "exercises": DAILY_EXERCISES,
        }
    )


@app.post("/student/dashboard/daily-pad-exercises/complete")
def complete_daily_pad_exercise(
    request: Request,
    exercise_name: str = Form(...)
):
    if request.session.get("role") != "student":
        return RedirectResponse("/", status_code=302)

    student = request.session["user"]

    env = {
        **os.environ,
        "STUDENT": student,
    "EXERCISE_ID": exercise_name,
        "PRACTICE_DATA_DIR": str(BASE_DIR),
        "PYTHONPATH": str(BASE_DIR / "webapp"),
    }

    result = subprocess.run(
        [
            sys.executable,
            str(BASE_DIR / "scripts" / "add_pad_xp.py"),
        ],
        env=env,
        capture_output=True,
        text=True,
    )

    # Write history entry
    from datetime import date
    import json

    stats_file = STUDENTS_DIR / student / "stats.json"

    with open(stats_file, "r") as f:
        stats = json.load(f)

    # ✅ INCREMENT STREAK ON PRACTICE
    update_streak_on_practice(stats)

    history = stats.setdefault("history", {})
    events = history.setdefault("events", [])

    events.append({
        "type": "pad",
        "name": exercise_name,
        "date": date.today().isoformat(),
    })

    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)

    return RedirectResponse(
        "/student/dashboard",
        status_code=302
    )


@app.get("/student/dashboard/history", response_class=HTMLResponse)
def student_history(request: Request):
    if request.session.get("role") != "student":
        return RedirectResponse("/", status_code=302)

    student = request.session["user"]
    stats_file = STUDENTS_DIR / student / "stats.json"

    if not stats_file.exists():
        return RedirectResponse("/student/dashboard", status_code=302)

    with open(stats_file, "r") as f:
        stats = json.load(f)

    events = stats.get("history", {}).get("events", [])

    # ========================
    # FEATURE 3: Overall Grade (LIFETIME)
    # ========================

    lesson_grades = [
        e["grade"] for e in events
        if e.get("type") == "attendance" and "grade" in e
    ]

    if lesson_grades:
        overall_grade = round(sum(lesson_grades) / len(lesson_grades), 2)
    else:
        overall_grade = None

    cutoff = date.today() - timedelta(days=30)

    # Events in last 30 days (for counters)
    recent_events = [
        e for e in events
        if date.fromisoformat(e["date"]) >= cutoff
    ]

    # Totals (last 30 days)
    total_pad = sum(1 for e in recent_events if e["type"] == "pad")
    total_attendance = sum(1 for e in recent_events if e["type"] == "attendance")

    # ✅ FEATURE 2: Total time practiced (LIFETIME)
    total_minutes = 0
    for e in events:
        if e["type"] == "pad":
            total_minutes += 5
        elif e["type"] == "attendance":
            total_minutes += 60

    formatted_time = format_minutes(total_minutes)

    # newest first
    recent_events = list(reversed(recent_events))

    return templates.TemplateResponse(
        "student/history.html",
        {
            "request": request,
            "events": recent_events,
            "total_pad": total_pad,
            "total_attendance": total_attendance,
            "total_time_practiced": formatted_time,
        "overall_grade": overall_grade,
            "longest_streak": stats["streak"]["longest"],
        }
    )

# ---------------------------------------------------
# Leaderboard
# ---------------------------------------------------

@app.get("/leaderboard", response_class=HTMLResponse)
def leaderboard_view(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/", status_code=302)

    if LEADERBOARD_FILE.exists():
        with open(LEADERBOARD_FILE) as f:
            data = json.load(f)
            students = data.get("students", [])
    else:
        students = []

    return templates.TemplateResponse(
        "leaderboard.html",
        {"request": request, "students": students},
    )
