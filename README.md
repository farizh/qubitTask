This app has been developed for Qubit Labs

Note: Python 3.11.4 was used for development

Steps to run:

1. Open terminal and Clone the repo by running "git clone https://github.com/farizh/qubitTask.git"
2. Switch to project root folder by running "cd qubitTask"
3. Run "python -m venv qubitEnv"
4. Activate qubitEnv by running "./qubitEnv/Scripts/activate"   (or "./qubitEnv/bin/activate")
6. Install required dependencies by running "pip install -r requirements.txt"
7. Run flask app by running "flask --app app run"
8. Validate flask server running on http://127.0.0.1:5000


API Endpoints Available:
1. http://127.0.0.1:5000/submit
    - POST:
        Inputs expected:
            title: string
            author: string
            text: string
            url: string
2. http://127.0.0.1:5000/search
    - GET:
        Input Expected:
            title - string (fuzzy)
            author - string (exact)
            size - string
3. http://127.0.0.1:5000/item/<submission_id>
    -GET:
        Input expected:
            submission_id
4. http://127.0.0.1:5000/rss
    - GET:
        Input Expected:
            title - string (fuzzy)
            author - string (exact)
            size - string

Sample requests provided in "postman/qubitTask.postman_collection.json"

Steps to play around with API using Postman:
1. Open postman app
2. File --> Import --> Upload postman/qubitTask.postman_collection.json

Steps to run generator app against the flask app:
1. Open new terminal window and run "./bin/generator --submit-url http://127.0.0.1:5000/submit"
2. Open new terminal window and run "./bin/generator --search-url  http://127.0.0.1:5000/search"


Things to improve in repo:
1. Add proper logger
2. Add input validation, sanitization. (marshmallow)
3. Add unit tests
4. Add swagger to play around with api endpoints



