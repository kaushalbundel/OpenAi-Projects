from bottle import run, template, post, route, request

from openai import OpenAI
import os, dotenv

# loading dotenv (loads the environment variables into the python program)
dotenv.load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# header is a common thing which will be repeated across many projects hence it is kept as string
header = """
<h1> Open AI projects</h1>
<p> <a href="/">Home</a></p>
"""


# standard function to query the openai api
def ai_query(query):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Answer the query in 30 words or less.",
            },
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


@post("/process")
def index_process():
    query = request.forms.get("query")
    response = ai_query(query)
    body = f"Query: {query} <br> Response: {response}"
    page = f"{header}<br>{body}"
    return page


run(host="127.0.0.1", port=8080, debug=True)
