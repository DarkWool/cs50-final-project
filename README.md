# No more anxiety, [see live](https://nomoreanxiety.herokuapp.com/)

#### Video Demo: https://youtu.be/5jbnPkORRPU

## Tech used:
1. Python (Flask)
1. Javascript
1. HTML, CSS
1. SQLITE for development and then migrated to PostgreSQL.

## Description:
This project was created for the CS50x Introduction to Programming course, it consists of a web application where anyone can take a 25 questions test to determine whether or not they have anxiety.
When the test is completed the user gets one of 4 possible results:
* No anxiety (only when user score is zero)
* Mild Anxiety
* Moderate Anxiety
* Severe anxiety

### Benefits of registered users:
When a user registers an account they can access some special features:
1. They can keep track of the tests they have made.
1. Their results become private, only the user that made the test can have access to his results. 
1. Once they completed the test they will have a special graph that provides them with a more complete result, it measures more specific anxiety disorders such as:
    1. Generalized anxiety.
    1. Social anxiety.
    1. Agoraphobia.
    1. Physical Symptoms.


## How to install?

It's recommended to first create a python virtual environment and then install the requirements with the following command:

```
pip3 install -r requirements.txt
```

### Main files
* auth.py - contains all related to the authentication process (sign up, log in, and logout).
* db.py - helper functions to connect to the database when you need to.
* forms.py - Forms used in the app.
* helpers.py - Helper functions used to calculate the results of the test, connect to the API to get a new quote, etc...
* views.py - All routes that do not belong to the authentication process. The errors are included here.
    
### Project key

This project **requires** a secret key under the name of SECRET_KEY.

You can set it using the python-dotenv module.

```
# Create a file called: '.env' inside the anxiety_app folder
# Store the key using the following syntax replacing 'KEY' with your key after the equal sign.

SECRET_KEY=KEY
```

You also need to load the module, the code for that is located inside **views.py** but the syntax is basically:

```
from dotenv import load_dotenv

load_dotenv()  # taken from the official page
```

For more information check the [documentation](https://github.com/theskumar/python-dotenv).

### Database

To see the initial schema needed for the database creation you may want to take a look at the file: "**anxiety-db.sql**".

In order to connect to a database you need to create a special environment variable called: **DATABASE_URL** (in my project the URL is from Heroku). 

Again, you can do this with the dotenv module.

#### SQLite and PostgreSQL
The repo has 2 branches as you may have seen, the development branch is just a previous version of the project where I was using SQLite entirely but to be able to successfully deploy the project on Heroku I changed it to Postgre, the reason why this branch still exists is just that I wanted to preserve a "copy" of the work made with SQLite.


## Credits

* The illustrations from the index and the test information pages were taken from [UnDraw](https://undraw.co/)
* [ZenQuotes API](https://zenquotes.io/)
