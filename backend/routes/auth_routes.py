from flask import Blueprint, request, jsonify
from database.db_connection import get_connection

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():

    try:
        print("LOGIN HIT")

        data = request.get_json()
        print("DATA:", data)

        email = data.get("email")
        password = data.get("password")

        print("EMAIL:", email)

        db = get_connection()
        print("DB:", db)

        cursor = db.cursor(dictionary=True)
        print("CURSOR OK")

        query = "SELECT * FROM users WHERE email=%s AND password=%s"

        cursor.execute(query, (email, password))
        print("QUERY OK")

        user = cursor.fetchone()
        print("USER:", user)

        cursor.close()
        db.close()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({
            "user_id": user["user_id"],
            "role": user["role"],
            "student_id": user["student_id"]
        }), 200

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": str(e)}), 500


   