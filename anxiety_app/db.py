import os
import psycopg2
import psycopg2.extras as ext

DB_URL = os.environ.get("DB_URL")

# Establish connection to the database
def connect_db():
    conn = psycopg2.connect(DB_URL)
    return conn


def single_query(query, parameters, fetchall=False):
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor(cursor_factory=ext.DictCursor)
    cursor.execute(query, parameters)

    if fetchall == True:
        result = cursor.fetchall()
    else:
        result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result
