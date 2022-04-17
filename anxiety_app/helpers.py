import shortuuid

from calendar import c
from anxiety_app import app
from anxiety_app.db import connect_db
from flask_login import current_user

# Convert numbers to letters (used in the test)
@app.template_filter("getLetter")
def getLetter(number):
    return chr(int(number) + 96).upper() + ")"


def getTestResult(slug, formData):
    # Fetch general info about the test
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tests WHERE slug = ?", (slug,))
    testInfo = cursor.fetchone()

    # Get categories of the test (and the total questions)
    cursor.execute(
        "SELECT category_id FROM questions WHERE test_id = ?", (testInfo["id"],)
    )
    categoriesList = cursor.fetchall()

    # Get values from answers table
    cursor.execute("SELECT value FROM answers WHERE test_id = ?", (testInfo["id"],))
    testData = cursor.fetchall()

    answerValues = []
    categoriesResults = {}
    totalQuestions = len(categoriesList) + 1
    userResult = 0

    for row in testData:
        answerValues.append(row["value"])

    maxValue = max(answerValues)

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

        if userAnswer in answerValues:
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
            """INSERT INTO results (test_id, test_result, hash, user_id, keyword) VALUES(?, ?, ?, ?, ?)""",
            (testInfo["id"], userResult, uuid, current_user.id, keyword),
        )

        userResultId = cursor.lastrowid

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

        cursor.executemany(
            "INSERT INTO category_results VALUES (?, ?, ?)", (finalResults)
        )
    else:
        # Insert the results into the db and retrieve the id of the row inserted
        cursor.execute(
            """INSERT INTO results (test_id, test_result, hash, keyword) VALUES(?, ?, ?, ?)""",
            (testInfo["id"], userResult, uuid, keyword),
        )
        userResultId = cursor.lastrowid

    conn.commit()
    conn.close()

    return f"results/{userResultId}/{uuid}"


def getNextQuestion(slug, questionNumber):
    # First fetch general information about the test
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT t.id, COUNT(q.test_id) AS total_questions FROM tests t
    INNER JOIN questions q ON t.id = q.test_id WHERE t.slug = ?""",
        (slug,),
    )
    testInfo = cursor.fetchone()

    # Get x question with answers of the current test
    cursor.execute(
        """SELECT q.question, a.answer, a.value FROM questions q INNER JOIN answers a 
    ON q.test_id=a.test_id WHERE q.question_number = ? AND q.test_id = ? ORDER BY a.value ASC""",
        (questionNumber, testInfo["id"]),
    )
    testData = cursor.fetchall()

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
    if result < 40:
        return "Mild Anxiety"
    elif result < 70:
        return "Moderate Anxiety"
    else:
        return "Severe Anxiety"
