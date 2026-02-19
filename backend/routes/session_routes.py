from flask import Blueprint, request, jsonify
from database.db_connection import get_connection
from datetime import datetime


session_bp = Blueprint("session", __name__)


def close_expired_sessions(cursor, db):

    now = datetime.now()

    query = """
    UPDATE sessions_new
    SET status='INACTIVE'
    WHERE status='ACTIVE'
      AND end_time < %s
    """

    cursor.execute(query, (now,))
    db.commit()


# -------------------------------
# Create Session
# -------------------------------
@session_bp.route("/create_session", methods=["POST"])
def create_session():

    data = request.get_json(force=True)

    if not data:
        return jsonify({"error": "No JSON data"}), 400


    db = None
    cursor = None


    try:

        db = get_connection()
        cursor = db.cursor(dictionary=True)


        # -------------------------------
        # Validate Course-Batch Relation
        # -------------------------------
        cursor.execute(
            "SELECT batch_id FROM courses WHERE course_id=%s",
            (data["course_id"],)
        )

        course = cursor.fetchone()

        if not course:
            return jsonify({"error": "Course not found"}), 404


        if str(course["batch_id"]) != str(data["batch_id"]):
            return jsonify({"error": "Course does not belong to this batch"}), 400


        # -------------------------------
        # Insert Session
        # -------------------------------
        query = """
        INSERT INTO sessions_new
        (course_id, classroom_id, start_time, end_time, status)
        VALUES (%s, %s, %s, %s, 'INACTIVE')
        """

        cursor.execute(
            query,
            (
                data["course_id"],
                data["classroom_id"],
                data["start_time"],
                data["end_time"]
            )
        )

        db.commit()

        return jsonify({"message": "Session created"})


    except Exception as e:

        return jsonify({"error": str(e)}), 500


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()



# -------------------------------
# Start Session
# -------------------------------
@session_bp.route("/start_session/<int:session_id>", methods=["PUT"])
@session_bp.route("/start_session/<int:session_id>", methods=["PUT"])
def start_session(session_id):

    db = get_connection()
    cursor = db.cursor()

    try:

        # Close all other active sessions
        cursor.execute(
            "UPDATE sessions_new SET status='INACTIVE' WHERE status='ACTIVE'"
        )

        # Start selected session
        cursor.execute(
            "UPDATE sessions_new SET status='ACTIVE' WHERE session_id=%s",
            (session_id,)
        )

        db.commit()

        return jsonify({"message": "Session started"})

    finally:

        cursor.close()
        db.close()



# -------------------------------
# End Session
# -------------------------------
@session_bp.route("/end_session/<int:session_id>", methods=["PUT"])
def end_session(session_id):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE sessions_new SET status='INACTIVE' WHERE session_id=%s",
        (session_id,)
    )

    db.commit()
    db.close()

    return jsonify({"message": "Session ended"})


# -------------------------------
# Active Session
# -------------------------------
@session_bp.route("/active_session", methods=["GET"])
def active_session():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    # Close expired sessions first
    close_expired_sessions(cursor, db)

    # Get current active session
    cursor.execute(
        """
        SELECT *
        FROM sessions_new
        WHERE status='ACTIVE'
          AND start_time <= NOW()
          AND end_time >= NOW()
        ORDER BY start_time DESC
        LIMIT 1
        """
    )

    data = cursor.fetchone()

    cursor.close()
    db.close()

    if data:
        return jsonify(data)

    return jsonify({"message": "No active session"})
