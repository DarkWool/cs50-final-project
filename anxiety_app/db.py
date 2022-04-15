import sqlite3
from anxiety_app import app

# Establish connection to the database
def connect_db():
    conn = sqlite3.connect("anxiety.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with app.app_context():
        db = connect_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()
        db.close()

init_db()