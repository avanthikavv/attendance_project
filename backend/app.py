from flask import Flask
from routes.student_routes import student_bp
from routes.attendance_routes import attendance_bp
from routes.session_routes import session_bp
from routes.auth_routes import auth_bp
from flask_cors import CORS


app = Flask(__name__)

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


@app.route("/")
def home():
    return "Backend Running Successfully!"

@app.route("/setup-sessions")
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

        return "sessions_new table created!"

    except Exception as e:
        return str(e), 500

@app.route("/setup-master")
def setup_master():

    from database.db_connection import get_connection

    try:
        db = get_connection()
        db.autocommit = True
        cur = db.cursor()

        # Courses
        cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id SERIAL PRIMARY KEY,
            batch_id INT NOT NULL
        );
        """)

        # Batches
        cur.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            batch_id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        );
        """)

        # Classrooms
        cur.execute("""
        CREATE TABLE IF NOT EXISTS classrooms (
            classroom_id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        );
        """)

        # Insert sample data
        cur.execute("""
        INSERT INTO batches (batch_id, name)
        VALUES (1, 'Batch A')
        ON CONFLICT DO NOTHING;
        """)

        cur.execute("""
        INSERT INTO courses (course_id, batch_id)
        VALUES (1, 1)
        ON CONFLICT DO NOTHING;
        """)

        cur.execute("""
        INSERT INTO classrooms (classroom_id, name)
        VALUES (1, 'Room 101')
        ON CONFLICT DO NOTHING;
        """)

        cur.close()
        db.close()

        return "Master tables created!"

    except Exception as e:
        return str(e), 500
# No app.run() here (Gunicorn handles it)
