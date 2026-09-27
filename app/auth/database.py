import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Database file will be created inside the auth folder
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "users.db"


def get_connection():
    """Create a connection to the SQLite database.

    A timeout is set so that concurrent writes from Streamlit's rerun-heavy
    model wait for a lock to clear instead of immediately raising
    'database is locked' (which is what made some admin edits silently
    appear to do nothing).
    """
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Create required tables if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Farmer',
            is_verified INTEGER NOT NULL DEFAULT 0,
            is_approved INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    user_columns = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(users)").fetchall()
    }
    if "is_approved" not in user_columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN is_approved INTEGER NOT NULL DEFAULT 0"
        )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS advisers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            phone TEXT NOT NULL,
            location TEXT NOT NULL,
            crops TEXT NOT NULL,
            diseases TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS help_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            reply TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL,
            replied_at TEXT,
            FOREIGN KEY (farmer_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT NOT NULL,
            otp_hash TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            is_used INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_user(full_name, mobile, email, password_hash, role="Farmer"):
    """Create a new user account."""
    conn = get_connection()

    try:
        cursor = conn.cursor()

        approval = 1 if role == "Admin" else 0
        cursor.execute("""
            INSERT INTO users
            (full_name, mobile, email, password_hash, role, is_verified, is_approved, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?)
        """, (
            full_name,
            mobile,
            email,
            password_hash,
            role,
            approval,
            datetime.now().isoformat()
        ))

        conn.commit()
        return True, "Registration successful."

    except sqlite3.IntegrityError:
        return False, "Mobile number or email is already registered."

    finally:
        conn.close()


def get_user_by_mobile(mobile):
    """Find a user using mobile number."""
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE mobile = ?",
        (mobile,)
    )

    user = cursor.fetchone()
    conn.close()

    return user


def mark_user_verified(mobile):
    """Mark the user's mobile/OTP verification as completed and approve member access."""
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET is_verified = 1, is_approved = 1 WHERE mobile = ?",
        (mobile,)
    )

    conn.commit()
    conn.close()


def approve_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET is_approved = 1 WHERE id = ? AND role = 'Farmer'",
        (user_id,)
    )
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    return changed


def get_pending_farmers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, full_name, mobile, email, is_verified, created_at FROM users "
        "WHERE role = 'Farmer' AND is_approved = 0 ORDER BY id DESC"
    )
    users = cursor.fetchall()
    conn.close()
    return users


def get_farmers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, full_name, mobile, email, is_verified, is_approved, created_at
        FROM users
        WHERE role = 'Farmer'
        ORDER BY id DESC
        """
    )
    users = cursor.fetchall()
    conn.close()
    return users


def create_adviser(full_name, specialization, phone, location, crops, diseases):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO advisers
            (full_name, specialization, phone, location, crops, diseases, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (full_name, specialization, phone, location, crops, diseases, datetime.now().isoformat())
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_advisers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM advisers ORDER BY full_name")
    advisers = cursor.fetchall()
    conn.close()
    return advisers


def create_help_request(farmer_id, subject, message):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO help_requests
            (farmer_id, subject, message, status, created_at)
            VALUES (?, ?, ?, 'Pending', ?)
            """,
            (farmer_id, subject.strip(), message.strip(), datetime.now().isoformat())
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_farmer_help_requests(farmer_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM help_requests WHERE farmer_id = ? ORDER BY id DESC",
        (farmer_id,)
    )
    requests = cursor.fetchall()
    conn.close()
    return requests


def get_help_requests():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT help_requests.*, users.full_name, users.mobile, users.email
        FROM help_requests
        JOIN users ON users.id = help_requests.farmer_id
        ORDER BY CASE WHEN help_requests.status = 'Pending' THEN 0 ELSE 1 END, help_requests.id DESC
        """
    )
    requests = cursor.fetchall()
    conn.close()
    return requests


def reply_to_help_request(request_id, reply):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE help_requests
            SET reply = ?, status = 'Replied', replied_at = ?
            WHERE id = ?
            """,
            (reply.strip(), datetime.now().isoformat(), request_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def save_otp(mobile, otp_hash, expiry_minutes=5):
    """Store a new OTP securely with an expiry time."""
    conn = get_connection()

    now = datetime.now()
    expires_at = now + timedelta(minutes=expiry_minutes)

    cursor = conn.cursor()

    # Invalidate previous unused OTPs for this mobile number
    cursor.execute("""
        UPDATE otp_codes
        SET is_used = 1
        WHERE mobile = ? AND is_used = 0
    """, (mobile,))

    cursor.execute("""
        INSERT INTO otp_codes
        (mobile, otp_hash, expires_at, attempts, is_used, created_at)
        VALUES (?, ?, ?, 0, 0, ?)
    """, (
        mobile,
        otp_hash,
        expires_at.isoformat(),
        now.isoformat()
    ))

    conn.commit()
    conn.close()


def get_latest_otp(mobile):
    """Get the latest active OTP record."""
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM otp_codes
        WHERE mobile = ? AND is_used = 0
        ORDER BY id DESC
        LIMIT 1
    """, (mobile,))

    otp = cursor.fetchone()
    conn.close()

    return otp


def increment_otp_attempt(mobile):
    """Increase failed OTP verification attempts."""
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE otp_codes
        SET attempts = attempts + 1
        WHERE id = (
            SELECT id
            FROM otp_codes
            WHERE mobile = ? AND is_used = 0
            ORDER BY id DESC
            LIMIT 1
        )
    """, (mobile,))

    conn.commit()
    conn.close()


def mark_otp_used(otp_id):
    """Mark an OTP as used."""
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE otp_codes SET is_used = 1 WHERE id = ?",
        (otp_id,)
    )

    conn.commit()
    conn.close()


# Initialize database automatically when this module is loaded
init_database()
def update_user_password(mobile: str, password_hash: str):
    """Update the password hash for an existing user."""
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET password_hash = ?
            WHERE mobile = ?
            """,
            (password_hash, mobile.strip())
        )

        conn.commit()

        if cursor.rowcount == 0:
            return False, "User not found."

        return True, "Password updated successfully."

    finally:
        conn.close()