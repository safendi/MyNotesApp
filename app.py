from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'devsecret')


# MongoDB 
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(mongo_uri)
db = mongo_client["notesdb"]
notes_collection = db["notes"]


# OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# Routes

@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/Classes', methods=['GET', 'POST'])
def classes():

    if request.method == 'POST':
        #temp username
        session['username'] = 'admin'
        data = request.get_json()
        existing = notes_collection.find_one({
            "username": session['username'],
            "class": data
        })
        print(existing)
        if existing is None:
            notes_collection.insert_one({
                "username": session['username'],
                "class": data,
                "notes": {}
            })
            return json.dumps("Success")
        else:
            return json.dumps("Class already exists")

    if request.method == 'GET':
        session['username'] = 'admin'

        classes = notes_collection.find(
            {"username": session['username']},
            {"class": 1, "_id": 0}
        )

        retData = [doc["class"] for doc in classes]
        return json.dumps(retData)


@app.route('/home/classes', methods=['POST', 'GET'])
def classes_home():

    if request.method == 'POST':
        className = request.get_json()
        session['className'] = className
        return json.dumps(session['className'])

    if request.method == 'GET':
        className = session.get('className')

        doc = notes_collection.find_one({
            "username": session['username'],
            "class": className
        })

        if not doc or doc["notes"] == {}:
            return json.dumps("0")
        else:
            return json.dumps(doc["notes"])


@app.route('/class/<string:className>')
def class_notes(className):
    session['className'] = className
    return render_template('classNotes.html', className=className)


@app.route('/notesAPI', methods=['POST'])
def notesAPI():

    noteName = request.get_json()

    doc = notes_collection.find_one({
        "username": session['username'],
        "class": session['className']
    })

    notes = doc.get("notes", {})

    if noteName not in notes:
        notes[noteName] = ""

        notes_collection.update_one(
            {
                "username": session['username'],
                "class": session['className']
            },
            {"$set": {"notes": notes}}
        )

        return json.dumps("Note Created")
    else:
        return json.dumps("Note already exists")


@app.route('/redirect_to_notes', methods=['GET', 'POST'])
def redirect_to_notes():

    if request.method == 'POST':
        noteName = request.get_json()
        session["noteName"] = noteName
        return json.dumps(session['className'] + '/' + noteName)

    if request.method == 'GET':
        className = session.get('className')

        doc = notes_collection.find_one({
            "username": session['username'],
            "class": className
        })

        return json.dumps(doc["notes"])


@app.route('/class/<string:className>/<string:note>')
def class_note(className, note):
    session['className'] = className
    session['noteName'] = note
    return render_template('notePage.html', className=className, note=note)


@app.route('/updateNote', methods=['POST'])
def updateNote():

    contents = request.get_json()

    notes_collection.update_one(
        {
            "username": session['username'],
            "class": session['className']
        },
        {
            "$set": {
                f"notes.{session['noteName']}": contents
            }
        }
    )

    return json.dumps("success")


@app.route('/aiBot', methods=['POST'])
def aiBot():

    data = request.get_json()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are to make a medium length multiple choice quiz based on the notes I give you. Surround the quiz title with ### (before and after). Surround each question with ** (before and after). Each choice should have a ~~x~~y before it. The x is the choice letter (a,b,c,d) and the y is 0 if incorrect and 1 if correct. There should only be 1 correct answer. Add $$$ at the end."
            },
            {
                "role": "user",
                "content": data
            }
        ],
    )

    retVal = completion.choices[0].message.content
    return json.dumps(retVal)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
