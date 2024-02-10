import functions_framework
from flask import jsonify, request
from pymongo import MongoClient
from datetime import datetime


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
        
        if request_json and 'topic' in request_json:
            topic_to_find = request_json['topic']
        else:
            return "No topic provided"
        
        if request_json and 'timestamp' in request_json:
            timestamp_to_find = request_json['timestamp']
        else:
            return "No timestamp provided"
        
        if request_json and 'score' in request_json:
            score = request_json['score']
        else:
            return "No score provided"

        # Query the collection based on the email field
        query = {"email": email}
        result = collection.find_one(query)
        # Get the current timestamp
        current_timestamp = datetime.utcnow().isoformat()

        if result:
            # Search for the quiz within the specified subject, topic, and timestamp
            saved_quizzes = result.get('saved_quizzes', [])
            for quiz in saved_quizzes:
                if quiz['subject'] == subject_to_find:
                    for t in quiz['topics']:
                        if t['topic_name'] == topic_to_find:
                            for q in t['quizzes']:
                                if q.get('questions'):
                                    if q['timestamp'] == timestamp_to_find:
                                        if 'attempts' not in q:
                                            q['attempts'] = []
                                        q['attempts'].append({"timestamp": current_timestamp, "score": score})
                                        # Update the document in the collection
                                        collection.update_one({"email": email}, {"$set": {"saved_quizzes": saved_quizzes}})
                                        return "Attempt added successfully."
                            return "No quiz found for the provided timestamp."
                    return "No topic found for the provided subject."
            return "No quiz found for the provided subject."
        else:
            return "No data found for email: {}".format(email)

    except Exception as e:
        print(e)
        return "Error occurred: {}".format(e)
