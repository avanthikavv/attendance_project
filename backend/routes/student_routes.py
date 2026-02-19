from flask import Blueprint, request, jsonify
from models.student_model import add_student, get_students
from database.db_connection import get_connection


student_bp = Blueprint("student", __name__)


@student_bp.route("/add_student", methods=["POST"])
def add_student_api():

    data = request.json

    add_student(
        data["name"],
        data["email"],
        data["batch"]
    )

    return jsonify({"message": "Student added"})


@student_bp.route("/students", methods=["GET"])
def get_students_api():

    students = get_students()

    return jsonify(students)

# ---------------------------------
# Student Dashboard Info
# ---------------------------------
# ---------------------------------
# Student Dashboard Info
# ---------------------------------
# ---------------------------------
# Student Dashboard Info
# ---------------------------------
@student_bp.route("/student_dashboard/<int:student_id>", methods=["GET"])
def student_dashboard(student_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # ----------------------------
        # Get Student Info
        # ----------------------------
        cursor.execute(
            """
            SELECT 
                s.student_id,
                s.name,
                s.email,
                s.batch_id,
                b.batch_name
            FROM students_new s
            JOIN batches b
              ON s.batch_id = b.batch_id
            WHERE s.student_id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            return jsonify(None)


        # ----------------------------
        # Get Active Session
        # ----------------------------
        cursor.execute(
            """
            SELECT 
                se.session_id,
                se.course_id,
                se.classroom_id,

                c.course_name,

                cl.room_name

            FROM sessions_new se

            JOIN courses c
              ON se.course_id = c.course_id

            JOIN classrooms cl
              ON se.classroom_id = cl.classroom_id

            WHERE se.status='ACTIVE'
              AND c.batch_id = %s

            ORDER BY se.start_time DESC
            LIMIT 1
            """,
            (student["batch_id"],)
        )

        session = cursor.fetchone()


        # ----------------------------
        # Combine Result
        # ----------------------------
        result = {
            "student_id": student["student_id"],
            "name": student["name"],
            "email": student["email"],
            "batch_name": student["batch_name"],
        }


        if session:
            result["course_name"] = session["course_name"]
            result["room_name"] = session["room_name"]
            result["session_id"] = session["session_id"]
            result["status"] = "ACTIVE"

        else:
            result["course_name"] = None
            result["room_name"] = None
            result["session_id"] = None
            result["status"] = "NO_SESSION"


        return jsonify(result)


    except Exception as e:

        return jsonify({"error": str(e)}), 500


    finally:

        cursor.close()
        db.close()

# ---------------------------------
# Get Active Sessions For Student
# ---------------------------------
@student_bp.route("/student_active_sessions/<int:student_id>", methods=["GET"])
def student_active_sessions(student_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # Get student batch
        cursor.execute(
            "SELECT batch_id FROM students_new WHERE student_id=%s",
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            return jsonify([])


        batch_id = student["batch_id"]


        # Get active sessions for this batch
        cursor.execute(
            """
            SELECT
                se.session_id,
                c.course_name,
                cl.room_name,

                CASE
                    WHEN a.attendance_id IS NOT NULL
                    THEN 1
                    ELSE 0
                END AS already_marked

            FROM sessions_new se

            JOIN courses c
              ON se.course_id = c.course_id

            JOIN classrooms cl
              ON se.classroom_id = cl.classroom_id

            LEFT JOIN attendance_new a
              ON a.session_id = se.session_id
             AND a.student_id = %s

            WHERE se.status='ACTIVE'
              AND c.batch_id = %s

            ORDER BY se.start_time DESC
            """,
            (student_id, batch_id)
        )

        data = cursor.fetchall()

        return jsonify(data)


    except Exception as e:

        return jsonify({"error": str(e)}), 500


    finally:

        cursor.close()
        db.close()
