from flask import Blueprint, request, jsonify
from database.db_connection import get_connection

session_bp = Blueprint("session", __name__)


# --------------------------------
# CREATE SESSION
# --------------------------------
@session_bp.route("/create_session", methods=["POST"])
def create_session():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data"}), 400

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        # Check if course exists
        cursor.execute(
            "SELECT batch_id FROM courses WHERE course_id = %s",
            (data["course_id"],)
        )

        course = cursor.fetchone()

        if not course:
            return jsonify({"error": "Course not found"}), 404

        # Check if course belongs to batch
        if str(course["batch_id"]) != str(data["batch_id"]):
            return jsonify({"error": "Course does not belong to this batch"}), 400

        # Insert session (is_closed defaults to 0)
        cursor.execute("""
            INSERT INTO sessions_new
            (course_id, classroom_id, batch_id, start_time, end_time, is_closed)
            VALUES (%s, %s, %s, %s, %s, 0)
            """, (
            data["course_id"],
            data["classroom_id"],
            data["batch_id"],
            data["start_time"],
            data["end_time"]
            ))
        db.commit()

        cursor.close()
        db.close()

        return jsonify({"message": "Session created"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------
# GET ACTIVE SESSION (TIME + NOT CLOSED)
# --------------------------------
@session_bp.route("/active_session", methods=["GET"])
def active_session():

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM sessions_new
            WHERE NOW() BETWEEN start_time AND end_time
              AND is_closed = 0
            ORDER BY start_time DESC
            LIMIT 1
        """)

        session = cursor.fetchone()

        cursor.close()
        db.close()

        if session:
            session["start_time"] = str(session["start_time"])
            session["end_time"] = str(session["end_time"])
            return jsonify(session)

        return jsonify({"message": "No active session"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------
# GET ALL SESSIONS (AUTO STATUS VIEW)
# --------------------------------
@session_bp.route("/all_sessions", methods=["GET"])
def all_sessions():

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT *,
            CASE
                WHEN NOW() BETWEEN start_time AND end_time
                     AND is_closed = 0
                THEN 'ACTIVE'
                ELSE 'INACTIVE'
            END AS status
            FROM sessions_new
            ORDER BY session_id DESC
        """)

        rows = cursor.fetchall()

        cursor.close()
        db.close()

        for row in rows:
            row["start_time"] = str(row["start_time"])
            row["end_time"] = str(row["end_time"])

        return jsonify(rows)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------
# MANUAL CLOSE SESSION (Teacher Control)
# --------------------------------
@session_bp.route("/close_session/<int:session_id>", methods=["PUT"])
def close_session(session_id):

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE sessions_new
            SET is_closed = 1
            WHERE session_id = %s
        """, (session_id,))

        db.commit()

        cursor.close()
        db.close()

        return jsonify({"message": "Session closed manually"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500