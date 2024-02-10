import functions_framework
import vertexai
from vertexai.language_models import TextGenerationModel
import json
from pymongo import MongoClient
from datetime import datetime

TOKEN_COUNT = 2000
PAGE = TOKEN_COUNT * 4
URI = "mongodb+srv://tanisha:tanisha@cluster0.pxmdv.mongodb.net/?retryWrites=true&w=majority"

@functions_framework.http
def hello_http(request):
    request_json = request.get_json(silent=True)
    
    file_name = request_json['topic']
    subject = request_json['subject']
    email = request_json['email']
    input_data = request_json['data']
    total_questions = request_json['questions_number']
    questions_type = request_json['questions_type']
    
    iterations = (len(input_data)+PAGE-1)//PAGE
    questions_per_page = max(1,(total_questions+iterations-1)//iterations)
    questions = []
    for i in range(0,iterations) : 
        trimmed_input_data = input_data[PAGE* i: min(len(input_data), PAGE*(i+1))]
        while True :
            try : 
                if questions_type != 2 : 
                    page_questions = json.loads(generate_questions(trimmed_input_data, questions_per_page))
                    questions = questions + page_questions['Questions']
                else :
                    page_questions = json.loads(generate_true_false(trimmed_input_data, questions_per_page))
                    questions = questions + page_questions['Questions']
                break
            except Exception as e:
                print(e)      

    if len(questions) > total_questions : 
        questions = questions[:total_questions]
    
    quiz = {'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'), 'questions' : questions}
    print("quiz : \n", quiz)
    upload_quiz(file_name,quiz,subject,email)
    
    return str(quiz)

def generate_questions(input_data, questionsNumber):
    vertexai.init(project="plt-gcp-401119", location="us-central1")

    parameters = {
        "temperature": 0.9,
        "max_output_tokens": 1000,
        "top_p": 0.8,
        "top_k": 40,
    }

    model = TextGenerationModel.from_pretrained("text-bison@002")
    response = model.predict(
        input_data + '.  You are an instructor who wants to test the understanding of students on the above material. Generate ' + str(questionsNumber) + ' MCQ questions with options and answers to test the understanding of students. The output should be in json following the format {"Questions" : [{"Question" : "question1", "Options" : ["option1", "option2", "option3", "option4"], "Answer":"correct answer from the options"},{"Question" : "question2", "Options" : ["option1", "option2", "option3", "option4"], "Answer":"correct answer from the options"}]} Apply the brackets according to the rules of json defined in the previous sentence. Do not make a mistake here.',
        **parameters,
    )
    return response.text

def generate_true_false(input_data, questionsNumber):
    vertexai.init(project="plt-gcp-401119", location="us-central1")

    parameters = {
        "temperature": 0.9,
        "max_output_tokens": 1000,
        "top_p": 0.8,
        "top_k": 40,
    }

    model = TextGenerationModel.from_pretrained("text-bison@002")
    response = model.predict(
        input_data + '.  You are an instructor who wants to test the understanding of students on the above material. Generate ' + str(questionsNumber) + ' true and false questions with options and answer to test the understanding of students. The output should be in json following the format {"Questions" : [{"Question" : "question1", "Options" : ["True", "False"], "Answer":"correct answer from the options. True or False"},{"Question" : "question2", "Options" : ["True", "False"], "Answer":"correct answer from the options. True or False"}]}. Apply the brackets according to the rules of json defined in the previous sentence. Do not make a mistake here.',
        **parameters,
    )

    return response.text

def read_file_as_single_line(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        merged_line = ''.join(lines).strip()
    return merged_line


def upload_quiz(file_name, quiz, subject, email):
    client = MongoClient(URI)
    db = client.demo
    collection = db.collec

    query = {"email": email}
    result = collection.find_one(query)
    if str(result).find(file_name) != -1 : 
        query = {'email': email, 'saved_quizzes.subject': subject, 'saved_quizzes.topics.topic_name': file_name}
        update = {'$push': {'saved_quizzes.$.topics.$[topic].quizzes': quiz}}
        array_filters = [{'topic.topic_name': subject}]  # Specify the filter for the array element
        collection.update_one(query, update, array_filters=array_filters)
    else :
        new_topic = {
        'topic_name': file_name,
        'quizzes': [quiz]
        }

        # Update the document
        query = {'email': email}
        update = {'$push': {'saved_quizzes.$[subject].topics': new_topic}}
        array_filters = [{'subject.subject': subject}]  
        collection.update_one(query, update, array_filters=array_filters)
    
    # query = {"email": email}
    # result = collection.find_one(query)
    # print(result)

    client.close()

