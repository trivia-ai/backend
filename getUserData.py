import functions_framework
from flask import jsonify
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
    request_args = request.args
    
    uri = "mongodb+srv://tanisha:tanisha@cluster0.pxmdv.mongodb.net/?retryWrites=true&w=majority"

    try:
        client = MongoClient(uri)
        db = client.demo  # Access the 'demo' database
        collection = db.collec  # Access the 'collec' collection

        if request_json and 'email' in request_json:
            email = request_json['email']
        elif request_args and 'email' in request_args:
            email = request_args['email']
        else:
            return "No email provided"

        # Query the collection based on the email field
        query = {"email": email}
        result = collection.find_one(query)
        
        if result:
            # Extract name and email from the result
            name = result.get('name', 'Name not found')
            email = result.get('email', 'Email not found')
            return jsonify({"name": name, "email": email})
        else:
            return "No data found for email: {}".format(email)

    except Exception as e:
        print(e)
        return "Error occurred: {}".format(e)
