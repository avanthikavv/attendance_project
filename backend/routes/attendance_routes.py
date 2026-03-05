from flask import Blueprint, request, jsonify
from database.db_connection import get_connection
from netaddr import IPAddress, IPNetwork

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

    try:

        db = get_connection()
        cursor = db.cursor(dictionary=True)

        # ---------------------------------
        # Get active session
        # ---------------------------------
        cursor.execute("""
            SELECT *
            FROM sessions_new
            WHERE NOW() BETWEEN start_time AND end_time
            AND is_closed = 0
            ORDER BY start_time DESC
            LIMIT 1
        """)

        session = cursor.fetchone()

        if not session:
            return jsonify({"error": "No active session"}), 403

        session_id = session["session_id"]

        # ---------------------------------
        # IP CHECK
        # ---------------------------------
        student_ip = request.remote_addr
        print("Student IP:", student_ip)

        cursor.execute("""
            SELECT cl.ip_range
            FROM sessions_new se
            JOIN classrooms cl
            ON se.classroom_id = cl.classroom_id
            WHERE se.session_id = %s
        """, (session_id,))

        room = cursor.fetchone()

        if not room:
            return jsonify({"error": "Classroom not found"}), 404

        ip_range = room["ip_range"]

        if IPAddress(student_ip) not in IPNetwork(ip_range):
            return jsonify({"error": "Not inside classroom network"}), 403

        # ---------------------------------
        # Check duplicate attendance
        # ---------------------------------
        cursor.execute("""
            SELECT 1
            FROM attendance_new
            WHERE student_id=%s AND session_id=%s
        """, (student_id, session_id))

        if cursor.fetchone():
            return jsonify({"error": "already_marked"}), 409

        # ---------------------------------
        # Insert attendance
        # ---------------------------------
        cursor.execute("""
            INSERT INTO attendance_new
            (student_id, session_id, status)
            VALUES (%s, %s, %s)
        """, (student_id, session_id, status))

        db.commit()

        return jsonify({
            "message": "success",
            "session_id": session_id
        }), 200

    except Exception as e:

        return jsonify({"error": str(e)}), 500

    finally:

        cursor.close()
        db.close()


# ---------------------------------
# Check If Already Marked
# ---------------------------------
@attendance_bp.route("/check_attendance/<int:student_id>", methods=["GET"])
def check_attendance(student_id):

    try:

        db = get_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 1
            FROM attendance_new a
            JOIN sessions_new s
            ON a.session_id = s.session_id
            WHERE a.student_id=%s
            AND NOW() BETWEEN s.start_time AND s.end_time
            AND s.is_closed = 0
        """, (student_id,))

        data = cursor.fetchone()

        if data:
            return jsonify({"marked": True})

        return jsonify({"marked": False})

    except Exception as e:

        return jsonify({"error": str(e)}), 500

    finally:

        cursor.close()
        db.close()


# -------------------------------
# Student Attendance History
# -------------------------------
@attendance_bp.route("/student_history/<int:student_id>", methods=["GET"])
def student_history(student_id):

    try:

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

        return jsonify(data)

    except Exception as e:

        return jsonify({"error": str(e)}), 500

    finally:

        cursor.close()
        db.close()