from flask import Blueprint, request, jsonify
from database.db_connection import get_connection
from datetime import datetime


session_bp = Blueprint("session", __name__)


# --------------------------------
# Auto Close Expired Sessions
# --------------------------------
def close_expired_sessions():

    db = get_connection()
    db.autocommit = True
    cur = db.cursor()

    cur.execute("""
        UPDATE sessions_new
        SET status='INACTIVE'
        WHERE status='ACTIVE'
          AND end_time < NOW()
    """)

    cur.close()
    db.close()


# --------------------------------
# Create Session
# --------------------------------
@session_bp.route("/create_session", methods=["POST"])
def create_session():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data"}), 400


    try:

        close_expired_sessions()

        db = get_connection()
        db.autocommit = True
        cur = db.cursor()


        # Check course batch
        cur.execute(
            "SELECT batch_id FROM courses WHERE course_id=%s",
            (data["course_id"],)
        )

        course = cur.fetchone()

        if not course:
            return jsonify({"error": "Course not found"}), 404


        if str(course[0]) != str(data["batch_id"]):
            return jsonify({"error": "Course not in batch"}), 400


        # Insert session
        cur.execute("""
            INSERT INTO sessions_new
            (course_id, classroom_id, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, 'INACTIVE')
        """, (
            data["course_id"],
            data["classroom_id"],
            data["start_time"],
            data["end_time"]
        ))


        cur.close()
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

        close_expired_sessions()

        db = get_connection()
        db.autocommit = True
        cur = db.cursor()


        # Close others
        cur.execute("""
            UPDATE sessions_new
            SET status='INACTIVE'
            WHERE status='ACTIVE'
        """)


        # Start this
        cur.execute("""
            UPDATE sessions_new
            SET status='ACTIVE'
            WHERE session_id=%s
        """, (session_id,))


        cur.close()
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

        close_expired_sessions()

        db = get_connection()
        db.autocommit = True
        cur = db.cursor()


        cur.execute("""
            UPDATE sessions_new
            SET status='INACTIVE'
            WHERE session_id=%s
        """, (session_id,))


        cur.close()
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

        close_expired_sessions()

        db = get_connection()
        cur = db.cursor()


        cur.execute("""
            SELECT *
            FROM sessions_new
            WHERE status='ACTIVE'
              AND start_time <= NOW()
              AND end_time >= NOW()
            ORDER BY start_time DESC
            LIMIT 1
        """)

        row = cur.fetchone()

        cur.close()
        db.close()


        if row:
            return jsonify({
                "session_id": row[0],
                "course_id": row[1],
                "classroom_id": row[2],
                "start_time": str(row[3]),
                "end_time": str(row[4]),
                "status": row[5]
            })


        return jsonify({"message": "No active session"})


    except Exception as e:

        return jsonify({"error": str(e)}), 500