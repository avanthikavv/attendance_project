from flask import Blueprint, request, jsonify
from database.db_connection import get_connection
from datetime import datetime

session_bp = Blueprint("session", __name__)


# --------------------------------
# Auto Close Expired Sessions
# --------------------------------
def close_expired_sessions(cursor):

    cursor.execute("""
        UPDATE sessions_new
        SET status = 'INACTIVE'
        WHERE status = 'ACTIVE'
        AND end_time < NOW()
    """)


# --------------------------------
# Create Session
# --------------------------------
@session_bp.route("/create_session", methods=["POST"])
def create_session():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data"}), 400

    try:

        db = get_connection()
        cursor = db.cursor()

        # Close expired sessions first
        close_expired_sessions(cursor)

        # --------------------------------
        # Check Course-Batch Relation
        # --------------------------------
        cursor.execute(
            "SELECT batch_id FROM courses WHERE course_id=%s",
            (data["course_id"],)
        )

        course = cursor.fetchone()

        if not course:
            return jsonify({"error": "Course not found"}), 404

        if str(course["batch_id"]) != str(data["batch_id"]):
            return jsonify({"error": "Course does not belong to this batch"}), 400


        # --------------------------------
        # Insert Session
        # --------------------------------
        cursor.execute("""
            INSERT INTO sessions_new
            (course_id, classroom_id, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, 'INACTIVE')
        """, (
            data["course_id"],
            data["classroom_id"],
            data["start_time"],
            data["end_time"]
        ))

        db.commit()

        cursor.close()
        db.close()

        return jsonify({"message": "Session created"})


    except Exception as e:
        return jsonify({"error": str(e)}), 500



# --------------------------------
# Start Session
# --------------------------------
@session_bp.route("/start_session/<int:session_id>", methods=["PUT"])
def start_session(session_id):

    try:

        db = get_connection()
        cursor = db.cursor()

        close_expired_sessions(cursor)

        # Close all other active sessions
        cursor.execute("""
            UPDATE sessions_new
            SET status='INACTIVE'
            WHERE status='ACTIVE'
        """)

        # Start selected session
        cursor.execute("""
            UPDATE sessions_new
            SET status='ACTIVE'
            WHERE session_id=%s
        """, (session_id,))

        db.commit()

        cursor.close()
        db.close()

        return jsonify({"message": "Session started"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# --------------------------------
# End Session
# --------------------------------
@session_bp.route("/end_session/<int:session_id>", methods=["PUT"])
def end_session(session_id):

    try:

        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE sessions_new
            SET status='INACTIVE'
            WHERE session_id=%s
        """, (session_id,))

        db.commit()

        cursor.close()
        db.close()

        return jsonify({"message": "Session ended"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# --------------------------------
# Get Active Session
# --------------------------------
@session_bp.route("/active_session", methods=["GET"])
def active_session():

    try:

        db = get_connection()
        cursor = db.cursor()

        close_expired_sessions(cursor)

        cursor.execute("""
            SELECT *
            FROM sessions_new
            WHERE status='ACTIVE'
              AND start_time <= NOW()
              AND end_time >= NOW()
            ORDER BY start_time DESC
            LIMIT 1
        """)

        session = cursor.fetchone()

        cursor.close()
        db.close()

        if session:
            return jsonify(session)

        return jsonify({"message": "No active session"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
   
    
@session_bp.route("/all_sessions", methods=["GET"])
def all_sessions():

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM sessions_new ORDER BY session_id")
    rows = cursor.fetchall()

    cursor.close()
    db.close()

    for row in rows:
        row["start_time"] = str(row["start_time"])
        row["end_time"] = str(row["end_time"])

    return jsonify(rows)