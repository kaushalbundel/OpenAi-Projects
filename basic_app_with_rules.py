from bottle import run, template, post, route, request, redirect
from openai import OpenAI
import os, dotenv

# loading dotenv (loads the environment variables into the python program)
dotenv.load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# header is a common thing which will be repeated across many projects hence it is kept as string
header = """
<h1> Open AI projects</h1>
<p> <a href="/">Home</a> <br> <a href="/rules">Rules</a></p>
"""


def injection():
    try:
        with open("rules.txt", "r") as file:
            content = file.read()
    except:
        content = ""
    return content


# standard function to query the openai api
def ai_query(query):
    injection_rules = injection()
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


@route("/rules")
def rules():
    try:
        with open("rules.txt", "r") as files:
            file = files.read()
    except:
        file = ""

    body = f"""
<form action="/process_rules" method="post">
<textarea rows="20" col="50" name="rules">{file}</textarea>
<br>
<input type="submit">
</form>
"""
    page = f"""{header} <br> {body}"""
    return page


@post("/process")
def index_process():
    query = request.forms.get("query")
    response = ai_query(query)
    body = f"Query: {query} <br> Response: {response}"
    page = f"{header}<br>{body}"
    return page


@post("/process_rules")
def process_rules():
    rules = request.forms.get("rules")
    with open("rules.txt", "w") as file:
        file.write(rules)
    redirect("/")


run(host="127.0.0.1", port=8080, debug=True)
