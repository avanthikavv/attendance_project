from db_connection import get_connection


db = get_connection()

if db.is_connected():
    print("Connected to MySQL successfully")

db.close()
