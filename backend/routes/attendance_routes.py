from flask import Blueprint, request, jsonify
from database.db_connection import get_connection
from datetime import datetime

import ipaddress

attendance_bp = Blueprint("attendance", __name__)


# ---------------------------------
# Mark Attendance
# ---------------------------------
@attendance_bp.route("/mark_attendance", methods=["POST"])
def mark_attendance():

    data = request.get_json(force=True)

    if not data:
        return jsonify({"error": "No JSON data"}), 400


    student_id = data.get("student_id")
    status = data.get("status")


    if not student_id or not status:
        return jsonify({"error": "Missing fields"}), 400


    # Get Client IP
    student_ip = request.remote_addr


    # TEMP: Allow localhost for testing
    if student_ip == "127.0.0.1":
        student_ip = "192.168.2.10"


    db = None
    cursor = None


    try:

        db = get_connection()
        cursor = db.cursor(dictionary=True)


        # Auto close expired sessions
        cursor.execute(
            """
            UPDATE sessions_new
            SET status='INACTIVE'
            WHERE status='ACTIVE'
            AND end_time < %s
            """,
            (datetime.now(),)
        )

        db.commit()


        # ---------------------------------
        # Get Active Session
        # ---------------------------------

        now = datetime.now()

        cursor.execute(
            """
            UPDATE sessions_new
            SET status='INACTIVE'
            WHERE status='ACTIVE'
            AND end_time < %s
            """,
            (now,)
        )

        db.commit()


        # Get valid active session
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

        session = cursor.fetchone()

        if not session:
            return jsonify({"error": "No active session"}), 403


        session_id = session["session_id"]


        # ---------------------------------
        # Check If Already Marked
        # ---------------------------------
        cursor.execute(
            """
            SELECT 1
            FROM attendance_new
            WHERE student_id=%s AND session_id=%s
            """,
            (student_id, session_id)
        )

        if cursor.fetchone():
            return jsonify({"error": "already_marked"}), 409


        # ---------------------------------
        # Get Classroom Network
        # ---------------------------------
        cursor.execute(
            "SELECT ip_range FROM classrooms WHERE classroom_id=%s",
            (session["classroom_id"],)
        )

        classroom = cursor.fetchone()

        if not classroom:
            return jsonify({"error": "Classroom not found"}), 404


        allowed_range = classroom["ip_range"]


        # ---------------------------------
        # IP Validation
        # ---------------------------------
        network = ipaddress.ip_network(allowed_range)
        ip = ipaddress.ip_address(student_ip)

        if ip not in network:
            return jsonify({"error": "Not in classroom network"}), 403


        # ---------------------------------
        # Insert Attendance
        # ---------------------------------
        cursor.execute(
            """
            INSERT INTO attendance_new
            (student_id, session_id, status)
            VALUES (%s, %s, %s)
            """,
            (student_id, session_id, status)
        )

        db.commit()


        return jsonify({
            "message": "success",
            "session_id": session_id
        })


    except Exception as e:

        if db:
            db.rollback()

        return jsonify({"error": str(e)}), 500


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()



# ---------------------------------
# Check If Already Marked (Student)
# ---------------------------------
@attendance_bp.route("/check_attendance/<int:student_id>", methods=["GET"])
def check_attendance(student_id):

    db = None
    cursor = None


    try:

        db = get_connection()
        cursor = db.cursor(dictionary=True)


        cursor.execute(
            """
            SELECT 1
            FROM attendance_new a
            JOIN sessions_new s
              ON a.session_id = s.session_id
            WHERE a.student_id=%s
              AND s.status='ACTIVE'
            """,
            (student_id,)
        )

        data = cursor.fetchone()


        if data:
            return jsonify({"marked": True})


        return jsonify({"marked": False})


    except Exception as e:

        return jsonify({"error": str(e)}), 500


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()

# -------------------------------
# Student Attendance History
# -------------------------------
@attendance_bp.route("/student_history/<int:student_id>", methods=["GET"])
def student_history(student_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT 
        c.course_name,
        a.status,
        a.timestamp
    FROM attendance_new a

    JOIN sessions_new s ON a.session_id = s.session_id
    JOIN courses c ON s.course_id = c.course_id

    WHERE a.student_id = %s

    ORDER BY a.timestamp DESC
    """

    cursor.execute(query, (student_id,))

    data = cursor.fetchall()

    db.close()

    return jsonify(data)

