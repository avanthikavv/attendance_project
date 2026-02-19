from flask import Blueprint, request, jsonify
from database.db_connection import get_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json(force=True)

    email = data["email"]
    password = data["password"]

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT * FROM users
    WHERE email=%s AND password=%s
    """

    cursor.execute(query, (email,password))

    user = cursor.fetchone()

    db.close()

    if not user:
        return jsonify({"error":"Invalid credentials"}),401


    return jsonify({
        "user_id": user["user_id"],
        "role": user["role"],
        "student_id": user["student_id"]
    })
