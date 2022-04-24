import shortuuid
import requests
import psycopg2.extras as ext

from flask_login import current_user
from datetime import datetime

from anxiety_app import app
from anxiety_app.db import connect_db, single_query

# Object to request a new quote from the API
requestQuote = {
    "url": "https://zenquotes.io/api/random",
    "headers": {"content-type": "application/json"},
}

# Convert numbers to letters (used in the test)
@app.template_filter("getLetter")
def getLetter(number):
    return chr(int(number) + 96).upper() + ")"


def getTestResult(slug, formData):
    # Fetch general info about the test
    conn = connect_db()
    cursor = conn.cursor(cursor_factory=ext.DictCursor)
    cursor.execute("SELECT id FROM tests WHERE slug = %s", (slug,))
    testInfo = cursor.fetchone()

    # Get categories of the test (and the total questions)
    cursor.execute(
        "SELECT category_id FROM questions WHERE test_id = %s", (testInfo["id"],)
    )
    categoriesList = cursor.fetchall()

    # Get values from answers table
    cursor.execute(
        "SELECT array_agg(value) FROM answers WHERE test_id = %s", (testInfo["id"],)
    )
    answersValues = cursor.fetchone()[0]

    categoriesResults = {}
    totalQuestions = len(categoriesList) + 1
    userResult = 0

    maxValue = max(answersValues)

    for row in categoriesList:
        if row["category_id"] in categoriesResults:
            categoriesResults[row["category_id"]]["total"] += maxValue
        else:
            categoriesResults[row["category_id"]] = {
                "id": row["category_id"],
                "total": maxValue,
                "userResult": 0,
            }

    for index in range(1, totalQuestions):
        try:
            userAnswer = int(formData.get(f"question{index}"))
        except (TypeError, ValueError) as err:
            continue

        if userAnswer in answersValues:
            categoryId = categoriesList[index - 1]["category_id"]
            categoriesResults[categoryId]["userResult"] += userAnswer
            userResult += userAnswer

    # Generate a new UUID to associate with the id of the new test result
    uuid = shortuuid.uuid()

    # Get the percentage of the total result and get the appropriate keyword for it
    userResult = round(getPercentage(userResult, len(categoriesList) * maxValue))
    keyword = getKeyword(userResult)

    if current_user.is_authenticated:
        cursor.execute(
            """INSERT INTO results (test_id, test_result, hash, user_id, keyword) VALUES(%s, %s, %s, %s, %s) RETURNING ID""",
            (testInfo["id"], userResult, uuid, current_user.id, keyword),
        )
        userResultId = cursor.fetchone()["id"]

        finalResults = []
        for category in categoriesResults:
            result = round(
                getPercentage(
                    categoriesResults[category]["userResult"],
                    categoriesResults[category]["total"],
                )
            )
            finalResults.append(
                (userResultId, categoriesResults[category]["id"], result)
            )

        ext.execute_batch(
            cursor, "INSERT INTO category_results VALUES (%s, %s, %s)", finalResults
        )
    else:
        # Insert the results into the db and retrieve the id of the row inserted
        cursor.execute(
            """INSERT INTO results (test_id, test_result, hash, keyword) VALUES(%s, %s, %s, %s) RETURNING ID""",
            (testInfo["id"], userResult, uuid, keyword),
        )
        userResultId = cursor.fetchone()["id"]

    conn.commit()

    cursor.close()
    conn.close()

    return f"results/{userResultId}/{uuid}"


def getNextQuestion(slug, questionNumber):
    # First fetch general information about the test
    conn = connect_db()
    cursor = conn.cursor(cursor_factory=ext.DictCursor)
    cursor.execute(
        """SELECT t.id, COUNT(q.test_id) AS total_questions FROM tests t
    INNER JOIN questions q ON t.id = q.test_id WHERE t.slug = %s GROUP BY t.id""",
        (slug,),
    )
    testInfo = cursor.fetchone()

    # Get x question with answers of the current test
    cursor.execute(
        """SELECT q.question, a.answer, a.value FROM questions q INNER JOIN answers a 
    ON q.test_id=a.test_id WHERE q.question_number = %s AND q.test_id = %s ORDER BY a.value ASC""",
        (questionNumber, testInfo["id"]),
    )
    testData = cursor.fetchall()

    cursor.close()
    conn.close()

    formattedData = {
        "question": testData[0]["question"],
        "answers": {},
        "values": {},
        "totalQuestions": testInfo["total_questions"],
    }

    length = len(testData)
    for row in range(0, length):
        formattedData["answers"][row] = testData[row]["answer"]
        formattedData["values"][row] = testData[row]["value"]

    return formattedData


def getPercentage(num, total):
    return num / total * 100


def getKeyword(result):
    if result <= 0:
        return "No Anxiety"
    elif result < 40:
        return "Mild Anxiety"
    elif result < 70:
        return "Moderate Anxiety"
    else:
        return "Severe Anxiety"


def getQuote():
    today = datetime.today().day
    dbQuote = single_query("SELECT * FROM api_quote WHERE id = 1")

    if dbQuote == None:
        newQuote = fetchQuote(
            "INSERT INTO api_quote (quote, author, fetch_date) VALUES(%s, %s, %s)",
            today,
        )
    elif dbQuote["fetch_date"] != today:
        newQuote = fetchQuote(
            "UPDATE api_quote SET quote = %s, author = %s, fetch_date = %s WHERE id = 1",
            today,
        )
    else:
        return dbQuote

    if newQuote == False:
        return dbQuote

    return newQuote


def fetchQuote(query, today):
    response = requests.get(url=requestQuote["url"], headers=requestQuote["headers"])

    if response.status_code == 200:
        newQuote = response.json()[0]
        single_query(query, (newQuote["q"], newQuote["a"], today))

        return {
            "quote": newQuote["q"],
            "author": newQuote["a"],
        }
    else:
        single_query("UPDATE api_quote SET fetch_date = %s WHERE id = 1", (today,))

        return False
