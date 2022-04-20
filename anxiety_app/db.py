import os
import psycopg2
import psycopg2.extras as ext

DATABASE_URL = os.environ.get("DATABASE_URL")

# Establish connection to the database
def connect_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def single_query(query, parameters=None, fetchall=False):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=ext.DictCursor)

    if parameters == None:
        cursor.execute(query)
    else:
        cursor.execute(query, parameters)

    if fetchall == True:
        result = cursor.fetchall()
    else:
        result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result
