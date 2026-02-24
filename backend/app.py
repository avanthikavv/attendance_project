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


# No app.run() here (Gunicorn handles it)

@app.route("/add-teacher")
def add_teacher():
    from database.db_connection import get_connection

    try:
        db = get_connection()
        db.autocommit = True
        cur = db.cursor()

        cur.execute("""
        INSERT INTO users (email, password, role, student_id)
        VALUES ('teacher@gmail.com', '1234', 'teacher', NULL)
        ON CONFLICT (email) DO NOTHING;
        """)

        cur.close()
        db.close()

        return "Teacher added!"

    except Exception as e:
        return str(e), 500