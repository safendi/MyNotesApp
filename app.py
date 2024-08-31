from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import json
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = 'sheffg'

conn = sqlite3.connect('notes4.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS notes (
                    username text,
                    class text PRIMARY KEY,
                    notes text)""")




client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))



@app.route('/')
def landing():
    return render_template('landing.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')



@app.route('/home')
def home():  # put application's code here
    return render_template('home.html')



@app.route('/Classes', methods=['GET', 'POST'])
def classes():
    if request.method == 'POST':
        data = request.get_json()
        cursor.execute("SELECT * FROM notes WHERE class = ? AND username = ?", (data, session['username']))
        result = cursor.fetchone()
        print(result)
        if result is None:
            cursor.execute("INSERT INTO notes (username, class, notes) VALUES (?, ?, ?)", ("admin",data, json.dumps({})))
            conn.commit()
            return (json.dumps("Success"))
        else :
            return (json.dumps("Class already exists"))

    if request.method == 'GET':
        # Temporary user session
        session['username'] = 'admin'

        cursor.execute("SELECT * FROM notes")
        result = cursor.fetchall()
        print(result)
        cursor.execute("SELECT class FROM notes")
        data = cursor.fetchall()
        print(data)
        retData = []
        for key in data :
            retData.append(key[0])
        return (json.dumps(retData))



@app.route('/home/classes', methods=['POST', 'GET'])
def classes_home():
    if request.method == 'POST':
        className = request.get_json()
        session['className'] = className
        return (json.dumps(session['className']))
    if request.method == 'GET':
        className = session.get('className')
        cursor.execute("SELECT * FROM notes WHERE class = ? AND username = ?", (className, session['username']))
        data = cursor.fetchone()
        if data[2] == '':
            return (json.dumps("0"))
        else :
            return (json.dumps(data[2]))



@app.route('/class/<string:className>')
def class_notes(className):
    print(className)
    return render_template('classNotes.html', className = className)



@app.route('/notesAPI', methods=['GET', 'POST'])
def notesAPI():
    if request.method == 'POST':
        noteName = request.get_json()
        print(noteName)
        cursor.execute("SELECT * FROM notes WHERE class = ? AND username = ?", (session['className'], session['username']))
        data = cursor.fetchone()[2]
        data = json.loads(data)
        print(data)
        if data.get(noteName) is None:
            data[noteName] = ''
            print(data)
            cursor.execute("REPLACE INTO notes VALUES (?, ? ,?)", (session['username'], session['className'], json.dumps(data)))
            conn.commit()
            cursor.execute("SELECT * FROM notes WHERE class = ? AND username = ?", (session['className'], session['username']))
            return (json.dumps(cursor.fetchone()))
        else :
            return json.dumps("Note already exists")



@app.route('/redirect_to_notes', methods=['GET', 'POST'])
def redirect_to_notes():
    if request.method == 'POST':
        noteName = request.get_json()
        print(noteName)
        session["noteName"] = noteName
        return json.dumps(session['className'] + '/' + noteName)
    if request.method == 'GET':
        className = session.get('className')
        cursor.execute("SELECT * FROM notes WHERE class = ? AND username = ?", (className, session['username']))
        data = cursor.fetchone()
        print(data[2])
        return (data[2])



@app.route('/class/<string:className>/<string:note>')
def class_note(className, note):
    return render_template('notePage.html', className = className, note = note)

@app.route('/updateNote', methods=['GET', 'POST'])
def updateNote():
    if request.method == 'POST':
        contents = request.get_json()
        print(contents)
        cursor.execute("SELECT * FROM notes WHERE class = ? AND username = ?", (session['className'], session['username']))
        data = cursor.fetchone()
        data = json.loads(data[2])
        print(data[session['noteName']])
        data[session['noteName']] = contents
        cursor.execute("REPLACE INTO notes VALUES (?, ?, ?)", (session['username'], session['className'], json.dumps(data)))
        conn.commit()
        return (json.dumps("success"))




@app.route('/aiBot', methods=['POST'])
def aiBot():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are to make a medium length multiple choice quiz based on the notes I give you.  Surround the quiz title with ### (before and after).  Surround each question with ** (before and after). Each choice should have a ~~x~~y before it.  The x is the choice letter (a,b,c,d) and the y is 0 if incorrect and 1 if correct. There should only be 1 correct answer. Ex: ##a##1.  Don't use any other symbols like - or # or * besides the ones I instructed. Add a $$$ at the end of your entire response.  Make sure the answers are factually accurate and do not repeat answer choices/questions.  The notes for each topic will be UNDER/AFTER the topic name.  Don't mix up the topics.  MAKE SURE THE ANSWER CHOICES DON'T REPEAT IN DIFFERENT WORDING.  FOR EACH QUESTION, RUN THROUGH ALL THE ANSWER CHOICES AND MAKE SURE THAT THERE AREN'T 2 OR MORE CHOICES THAT JUST REPEAT THE SAME THING BUT IN DIFFERENT WORDS.  MAKE SURE THERE AREN'T ANSWER CHOICES THAT REPEAT AT ALL.  FOR EXAMPLE THERE SHOULDNT BE A CHOICE THAT SAYS SRAM AND ANOTHER CHOICE THAT SAYS STATIC RAM BECAUSE THOSE 2 ARE THE SAME THING.  FOR EACH QUESTION, ASK YOURSELF THE QUESTION AND THEN GO CHECK THROUGH THE ANSWER CHOICES AND MAKE SURE THAT THE CORRECT ANSWER CHOICE IS ACTUALLY THE BEST CHOICE. IF ITS NOT THE BEST CHOICE OR IF ITS NOT FACTUALLY ACCURATE, REDO THE ENTIRE QUESTION AND ITS ANSWER CHOICES.  IF NOT REDO THE QUESTION. Please double check the correct answer for the first question you produce multiple times.  You tend to set the answer to the first question incorrectly so make sure you dont do that."},
                {
                    "role": "user",
                    "content": data
                }
            ],
        )
        retVal = completion.choices[0].message.content
        return json.dumps(retVal)


if __name__ == '__main__':
    app.run()
