'''
The code will work in the following manner:
- The db will store all the queries and responses
- The injection will be specified by using "I want you " keywords. If a sentence has these words then the sentence will be treated as an injection.
- All this information will be stored in the database
'''
from bottle import run, template, post, route, request, redirect
from openai import OpenAI
import os, dotenv
import sqlite3

# loading dotenv (loads the environment variables into the python program)
dotenv.load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# header is a common thing which will be repeated across many projects hence it is kept as string
header = """
<h1> Open AI projects</h1>
<p> <a href="/">Home</a> <br> <a href="/memory">Previous Search</a></p>
"""


# DB creation
def db_create():
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS memory(query, response)")
    conn.commit()
    conn.close()

#DB insert
def db_insert(query, response):
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO memory(query, response) VALUES (?,?)', (query, response))
    conn.commit()
    conn.close()
    print(f'Added: {query}, {response}')
    
#DB fetch injection
def db_injection():
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    query = cursor.execute('SELECT query FROM memory where query like "%I want you%"')
    query.fetchall() 
    conn.close()
    return query

# DB fetch
def db_fetch():
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    query = cursor.execute("SELECT * FROM memory")
    query= query.fetchall()
    conn.close()
    return query


# Since we are storing the injection rules in the database we do not need to use this injection funcytion
# def injection():
#     try:
#         with open("rules.txt", "r") as file:
#             content = file.read()
#     except:
#         content = ""
#     return content


# standard function to query the openai api
def ai_query(query):
    injection_rules = str(db_injection())
    #checking the type of db_injection so that I can do the type conversion later
    print(injection_rules)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": injection_rules},
            {"role": "user", "content": query},
        ],
    )
    response = completion.choices[0].message.content
    return response


# the index page of the application
@route("/")
def index():
    form = """
<form action="/process" method="post">
Question: <input type="text" name="query">
<br>
<input type="submit">
</form>
"""
    page = f"{header}<br>{form}"  # combining the header and form in a string with the <br> element, so that they appear above and below
    return page


#creating a page for memory
@route("/memory")
def rules(): # This is an interesting way to achieve desired objective of integrating html with pycode. 
    response = db_fetch()
    body = '<table>'
    for value in response:
        body = f'{body}<tr><td>{value[0]}</td><td>{value[1]}</td></tr>'
    body = f'{body} </table>'
    page = f"""{header} <br> {body}"""
    return page


@post("/process")
def index_process():
    query = request.forms.get("query")
    response = ai_query(query)
    db_insert(query, response)
    body = f"Query: {query} <br> Response: {response}"
    page = f"{header}<br>{body}"
    return page

#This is no longer needed as we are saving the queries in the db
# @post("/process_rules")
# def process_rules():
#     rules = request.forms.get("rules")
#     with open("rules.txt", "w") as file:
#         file.write(rules)
#     redirect("/")

db_create()
run(host="127.0.0.1", port=8080, debug=True)
