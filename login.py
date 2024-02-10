import functions_framework
from flask import jsonify, request
from pymongo import MongoClient
import bcrypt

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
    if request.method == 'POST':
        # Logic for POST request (Create User)
        request_json = request.get_json()
        if request_json and 'email' in request_json and 'password' in request_json:
            email = request_json['email']
            password = request_json['password']

            uri = "mongodb+srv://tanisha:tanisha@cluster0.pxmdv.mongodb.net/?retryWrites=true&w=majority"

            try:
                client = MongoClient(uri)
                db = client.demo  # Access the 'demo' database
                collection = db.auth_user  # Access the 'collec' collection

                # Check if user with the same email already exists
                existing_user = collection.find_one({"email": email})
                if not existing_user:
                    return "User with email {}  does not exist".format(email)

                if existing_user and bcrypt.checkpw(password.encode('utf-8'), existing_user['password']):
                    return jsonify({"email": existing_user["email"]})
                else:
                    return "Incorrect password"

            except Exception as e:
                print(e)
                return "Error occurred: {}".format(e)
        else:
            return "Incomplete user data provided"
    else:
        return "Method not allowed"


