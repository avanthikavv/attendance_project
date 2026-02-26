from flask import Flask, jsonify
from flask_cors import CORS

from routes.student_routes import student_bp
from routes.attendance_routes import attendance_bp
from routes.session_routes import session_bp
from routes.auth_routes import auth_bp


app = Flask(__name__)

# Enable CORS safely
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

# Register Blueprints
app.register_blueprint(student_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(session_bp)
app.register_blueprint(auth_bp)


# ---------------------------------
# Health Check Route
# ---------------------------------
@app.route("/")
def home():
    return "Backend Running Successfully!", 200


# ---------------------------------
# Setup Sessions Table
# ---------------------------------
@app.route("/setup-sessions", methods=["GET"])
def setup_sessions():

    from database.db_connection import get_connection

    try:
        db = get_connection()
        db.autocommit = True
        cur = db.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions_new (
            session_id SERIAL PRIMARY KEY,
            course_id INT NOT NULL,
            classroom_id INT NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            status VARCHAR(20) DEFAULT 'INACTIVE'
        );
        """)

        cur.close()
        db.close()

        return jsonify({"message": "sessions_new table created!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------
# Setup Master Tables
# ---------------------------------
@app.route("/setup-master", methods=["GET"])
def setup_master():

    from database.db_connection import get_connection

    try:
        db = get_connection()
        db.autocommit = True
        cur = db.cursor()

        # Batches
        cur.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            batch_id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        );
        """)

        # Courses
        cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id SERIAL PRIMARY KEY,
            batch_id INT NOT NULL
        );
        """)

        # Classrooms
        cur.execute("""
        CREATE TABLE IF NOT EXISTS classrooms (
            classroom_id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        );
        """)

        # Insert default data safely
        cur.execute("""
        INSERT INTO batches (batch_id, name)
        VALUES (1, 'Batch A')
        ON CONFLICT (batch_id) DO NOTHING;
        """)

        cur.execute("""
        INSERT INTO courses (course_id, batch_id)
        VALUES (1, 1)
        ON CONFLICT (course_id) DO NOTHING;
        """)

        cur.execute("""
        INSERT INTO classrooms (classroom_id, name)
        VALUES (1, 'Room 101')
        ON CONFLICT (classroom_id) DO NOTHING;
        """)

        cur.close()
        db.close()

        return jsonify({"message": "Master tables created!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------
# IMPORTANT: No app.run()
# Gunicorn handles server on Render
# ---------------------------------