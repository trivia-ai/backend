import functions_framework
from flask import jsonify, request
from pymongo import MongoClient

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    uri = "mongodb+srv://tanisha:tanisha@cluster0.pxmdv.mongodb.net/?retryWrites=true&w=majority"

    try:
        client = MongoClient(uri)
        db = client.demo  # Access the 'demo' database
        collection = db.collec  # Access the 'collec' collection

        if request_json and 'email' in request_json:
            email = request_json['email']
        else:
            return "No email provided"
        
        if request_json and 'subject' in request_json:
            subject_to_find = request_json['subject']
        else:
            return "No subject provided"

        # Query the collection based on the email field
        query = {"email": email}
        result = collection.find_one(query)
        
        if result:
            # Extract topics from saved quizzes for the specified subject
            saved_quizzes = result.get('saved_quizzes', [])
            topics = []
            for quiz in saved_quizzes:
                if quiz['subject'] == subject_to_find:
                    for topic in quiz['topics']:
                        topics.append(topic['topic_name'])
            return jsonify(topics)
        else:
            return "No data found for email: {}".format(email)

    except Exception as e:
        print(e)
        return "Error occurred: {}".format(e)
