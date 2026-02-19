from database.db_connection import get_connection


def add_student(name, email, batch):

    db = get_connection()
    cursor = db.cursor()

    query = """
    INSERT INTO students (name, email, batch)
    VALUES (%s, %s, %s)
    """

    cursor.execute(query, (name, email, batch))

    db.commit()
    db.close()


def get_students():

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")

    data = cursor.fetchall()

    db.close()

    return data
