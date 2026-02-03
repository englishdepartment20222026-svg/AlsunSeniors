from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

from integrations.facebook_integration import scrape_facebook_posts

DB_PATH = Path(__file__).with_name("alsun.db")
ADMIN_HASH = hashlib.sha256(b"admin:admin").hexdigest()

app = Flask(__name__)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            doctors TEXT NOT NULL,
            portal TEXT,
            facebook TEXT,
            drive TEXT,
            info TEXT,
            tags TEXT,
            badge TEXT,
            icon TEXT,
            cover_class TEXT,
            summary TEXT,
            resources TEXT,
            drive_status TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            external_id TEXT,
            source TEXT,
            title TEXT,
            body TEXT,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT,
            time TEXT,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS integrations (
            course_id INTEGER PRIMARY KEY,
            facebook_cursor TEXT,
            facebook_cookies_path TEXT,
            drive_cursor TEXT,
            portal_cursor TEXT,
            updated_at TEXT,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
        """
    )
    conn.commit()
    _ensure_column(conn, "posts", "external_id", "TEXT")
    _ensure_column(conn, "integrations", "facebook_cookies_path", "TEXT")
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_posts_external
        ON posts (course_id, external_id)
        """
    )
    conn.commit()
    conn.close()


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, col_type: str) -> None:
    cursor = conn.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cursor.fetchall()}
    if column in columns:
        return
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")


def seed_db() -> None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    seed_courses = [
        {
            "title": "Digital Linguistics",
            "category": "Linguistics",
            "doctors": "Dr. Rania Hassan • Dr. Omar Adel",
            "portal": "faculty.edu/linguistics",
            "facebook": "fb.com/linguistics",
            "drive": "drive.google.com/alsun/linguistics",
            "info": "Focus on corpus analysis, AI translation, and applied research.",
            "tags": json.dumps(["AI translation", "Labs", "Weekly quizzes"]),
            "badge": "3 new",
            "icon": "🧠",
            "cover_class": "cover-one",
            "summary": "Latest update: Lecture slides uploaded 15 minutes ago.",
            "resources": "28",
            "drive_status": "On",
        },
        {
            "title": "Advanced Translation",
            "category": "Translation",
            "doctors": "Dr. Maha Suleiman • Dr. Nour Said",
            "portal": "faculty.edu/translation",
            "facebook": "fb.com/translation",
            "drive": "drive.google.com/alsun/translation",
            "info": "Professional translation workflows, CAT tools, and weekly peer reviews.",
            "tags": json.dumps(["CAT tools", "Peer review", "Portfolio"]),
            "badge": "2 updates",
            "icon": "🌍",
            "cover_class": "cover-two",
            "summary": "Latest update: CAT toolkit templates added this morning.",
            "resources": "19",
            "drive_status": "On",
        },
    ]

    for course in seed_courses:
        cursor.execute(
            """
            INSERT INTO courses (
                title, category, doctors, portal, facebook, drive, info, tags, badge, icon, cover_class, summary,
                resources, drive_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                course["title"],
                course["category"],
                course["doctors"],
                course["portal"],
                course["facebook"],
                course["drive"],
                course["info"],
                course["tags"],
                course["badge"],
                course["icon"],
                course["cover_class"],
                course["summary"],
                course["resources"],
                course["drive_status"],
            ),
        )

    conn.commit()
    conn.close()


def serialize_course(row: sqlite3.Row, conn: sqlite3.Connection) -> dict[str, Any]:
    course_id = row["id"]
    posts = conn.execute(
        "SELECT source, title, body FROM posts WHERE course_id = ? ORDER BY id DESC", (course_id,)
    ).fetchall()
    notifications = conn.execute(
        "SELECT title, time FROM notifications WHERE course_id = ? ORDER BY id DESC", (course_id,)
    ).fetchall()

    return {
        "id": course_id,
        "title": row["title"],
        "category": row["category"],
        "doctors": row["doctors"],
        "portal": row["portal"],
        "facebook": row["facebook"],
        "drive": row["drive"],
        "info": row["info"],
        "tags": json.loads(row["tags"]) if row["tags"] else [],
        "badge": row["badge"],
        "icon": row["icon"],
        "coverClass": row["cover_class"],
        "summary": row["summary"],
        "resources": row["resources"],
        "driveStatus": row["drive_status"],
        "posts": [dict(post) for post in posts],
        "notifications": [dict(note) for note in notifications],
    }


@app.route("/api/health")
def health() -> tuple[dict[str, str], int]:
    return {"status": "ok"}, 200


@app.route("/")
def root() -> Any:
    return send_from_directory(Path(__file__).parent, "index.html")


@app.route("/admin.html")
def admin_page() -> Any:
    return send_from_directory(Path(__file__).parent, "admin.html")


@app.route("/styles.css")
def styles() -> Any:
    return send_from_directory(Path(__file__).parent, "styles.css")


@app.route("/app.js")
def script() -> Any:
    return send_from_directory(Path(__file__).parent, "app.js")


@app.route("/course.html")
def course_page() -> Any:
    return send_from_directory(Path(__file__).parent, "course.html")


@app.route("/api/admin/login", methods=["POST"])
def admin_login() -> tuple[dict[str, str], int]:
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", ""))
    password = str(payload.get("password", ""))
    candidate = hashlib.sha256(f"{username}:{password}".encode()).hexdigest()
    if candidate == ADMIN_HASH:
        return {"status": "ok"}, 200
    return {"status": "invalid"}, 401


@app.route("/api/courses", methods=["GET", "POST"])
def courses_endpoint() -> tuple[Any, int]:
    conn = get_db()
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        tags = payload.get("tags", [])
        conn.execute(
            """
            INSERT INTO courses (
                title, category, doctors, portal, facebook, drive, info, tags, badge, icon, cover_class, summary,
                resources, drive_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("title", "Untitled"),
                payload.get("category", "General"),
                payload.get("doctors", ""),
                payload.get("portal", ""),
                payload.get("facebook", ""),
                payload.get("drive", ""),
                payload.get("info", ""),
                json.dumps(tags),
                payload.get("badge", "New"),
                payload.get("icon", "📘"),
                payload.get("coverClass", "cover-one"),
                payload.get("summary", ""),
                payload.get("resources", "0"),
                payload.get("driveStatus", "Off"),
            ),
        )
        conn.commit()

    rows = conn.execute("SELECT * FROM courses ORDER BY id DESC").fetchall()
    data = [serialize_course(row, conn) for row in rows]
    conn.close()
    return jsonify(data), 200


@app.route("/api/courses/<int:course_id>")
def course_detail(course_id: int) -> tuple[Any, int]:
    conn = get_db()
    row = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    if not row:
        conn.close()
        return {"status": "not_found"}, 404
    data = serialize_course(row, conn)
    conn.close()
    return jsonify(data), 200


@app.route("/api/integrations/facebook/upload", methods=["POST"])
def upload_facebook_cookies() -> tuple[dict[str, str], int]:
    if "cookies" not in request.files:
        return {"status": "missing"}, 400
    course_id = request.form.get("course_id")
    if not course_id:
        return {"status": "missing_course"}, 400
    file = request.files["cookies"]
    destination = Path(__file__).with_name(f"facebook_cookies_{course_id}.txt")
    file.save(destination)
    conn = get_db()
    conn.execute(
        """
        INSERT INTO integrations (course_id, facebook_cookies_path, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(course_id) DO UPDATE SET
            facebook_cookies_path = excluded.facebook_cookies_path,
            updated_at = excluded.updated_at
        """,
        (course_id, str(destination)),
    )
    conn.commit()
    conn.close()
    return {"status": "uploaded"}, 200


@app.route("/api/integrations/facebook/sync", methods=["POST"])
def sync_facebook() -> tuple[dict[str, str], int]:
    payload = request.get_json(silent=True) or {}
    course_id = payload.get("course_id")
    if not course_id:
        return {"status": "missing_course"}, 400
    conn = get_db()
    integration = conn.execute(
        "SELECT facebook_cursor, facebook_cookies_path FROM integrations WHERE course_id = ?",
        (course_id,),
    ).fetchone()
    cursor = integration["facebook_cursor"] if integration else None
    cookies_path = integration["facebook_cookies_path"] if integration else None
    course = conn.execute("SELECT facebook FROM courses WHERE id = ?", (course_id,)).fetchone()
    page_url = course["facebook"] if course else ""
    if not cookies_path or not page_url:
        conn.close()
        return {"status": "missing_configuration"}, 400

    posts, new_cursor, status = scrape_facebook_posts(page_url, Path(cookies_path), cursor)
    if status != "ok":
        conn.close()
        return {"status": status}, 202

    for post in posts:
        conn.execute(
            """
            INSERT OR IGNORE INTO posts (course_id, external_id, source, title, body)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                course_id,
                post["external_id"],
                f"Facebook Page • {post['time']}",
                post["title"],
                post["body"],
            ),
        )

    conn.execute(
        """
        INSERT INTO integrations (course_id, facebook_cursor, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(course_id) DO UPDATE SET
            facebook_cursor = excluded.facebook_cursor,
            updated_at = excluded.updated_at
        """,
        (course_id, new_cursor),
    )
    conn.commit()
    conn.close()
    return {"status": "synced", "posts": str(len(posts))}, 200


@app.route("/api/integrations/refresh", methods=["POST"])
def refresh_integrations() -> tuple[dict[str, str], int]:
    return {"status": "queued"}, 202


@app.route("/api/whatsapp/broadcast", methods=["POST"])
def whatsapp_broadcast() -> tuple[dict[str, str], int]:
    payload = request.get_json(silent=True) or {}
    if not payload.get("message"):
        return {"status": "missing"}, 400
    return {"status": "queued"}, 202


if __name__ == "__main__":
    init_db()
    seed_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
