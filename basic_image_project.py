from bottle import run, post, route, request, static_file
from openai import OpenAI
import os, dotenv # for managing the openAI API key 
import sqlite3
import datetime
import requests

# directory for downloading file

pic_directory = 'dalle-pics'
try:
    os.mkdir(pic_directory)
except:
    pass

# loading dotenv (loads the environment variables into the python program)
dotenv.load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# header is a common thing which will be repeated across many projects hence it is kept as string
header = """
<h1> Open AI projects</h1>
<p> <a href="/">Home</a> <br> <a href="/search">Previous Search</a></p>
"""


# DB creation
def db_create():
    conn = sqlite3.connect("gallery.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS gallery(prompt,revised_prompt, filename)")
    conn.commit()
    conn.close()

#DB insert
def db_insert(prompt, revised_prompt, filename):
    conn = sqlite3.connect("gallery.db")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO gallery(prompt, revised_prompt, filename) VALUES (?,?,?)', (prompt, revised_prompt,filename))
    conn.commit()
    conn.close()
    
# fetching the query from the database
def db_query(query):
    conn = sqlite3.connect("gallery.db")
    cursor = conn.cursor()
    query = f"%{query}%"
    query = cursor.execute("SELECT * FROM gallery where revised_prompt like ?",(query,)) #TODO: Why I am searching revised_prompt 
    query = query.fetchall()
    conn.close()
    return query

# Master Query for image generation
def ai_query(query):
   images = client.images.generate(model='dall-e-3',prompt=query, n=1, quality="standard", size="1024x1024",) 
   image_url = images.data[0].url 
   revised_prompt = images.data[0].revised_prompt
   return image_url, revised_prompt

#image download
def download(url):
    '''Downloads tde image and saves on local and returns filename'''
    file_response = requests.get(url)
    filename = f'{str(datetime.datetime.now())}.png'
    file_path = os.path.join(pic_directory, filename)
    with open(file_path, 'wb') as file:
        file.write(file_response.content)
    return filename
    

# the index page of the application
@route("/")
def index():
    form = """
<form action="/process" method="post">
Imagine a picture: <input type="text" name="query">
<br>
<input type="submit">
</form>
"""
    page = f"{header}<br>{form}"  # combining the header and form in a string with the <br> element, so that they appear above and below
    return page

#this is the main process of running the query from the index page and getting a response from OpenAI API
@post("/process")
def index_process():
    query = request.forms.get("query")
    response = ai_query(query)
    filename = download(response[0])
    db_insert(prompt=query, revised_prompt=response[1], filename=filename)
    body= f'''
    Prompt: {query} <br>
    <img style="height:400px; width:auto;" "src="{response[0]}">
    <br>
    Revised Prompt:{response[1]}
'''
    page = f'{header}<br>{body}' 
    return page

@route('/search')
def index():
   form = '''
   <form action="/process_search" method="post">
   Find: <input type="text" name="query">
   <br>
   <input type="submit">
   </form>
''' 
   response = db_query(' ') # This query will select everything that is stored in the gallery.db
   gallery = '<div style="vertical-align:top;">'

   for record in response:
       gallery = f'''
       {gallery}
       <div style="display:inline-block;width:300px;height:auto;vertical-align: top;">
                    <p>{record[0]}</p>
                    <img style="width:100%;height:auto;" src="/{pic_directory}/{record[2]}">
                    <p>{record[1]}</p>
                    </div>
'''
       gallery = f'{gallery} </div>'
       page = f'{header} <br> {form} <hr> {gallery}'
       return page

@post('/process_search')
def index_process():
    query = request.forms.get('query')
    response = db_query(query)
    gallery = '<div style="vertical-align:top">'

    for record in response:
        filename = os.path.join(pic_directory, record[2])
        
        gallery = f'''
                    {gallery} 
                    <div style="display:inline-block;width:300px;height:auto;vertical-align: top;">
                    <p>{record[0]}</p>
                    <img style="width:100%;height:auto;" src="{filename}">
                    <p>{record[1]}</p>
                    </div>
                    '''
    gallery = f'{gallery} </div>'
    body = f'''
    Search Prompt: {query}
    <hr>
   {gallery} 
'''
    page = f'{header} <br> {body}'
    
    return page

# route in the static path should be mentioned while working with the bottle framework because in this way all the static files can be served using the path /static (For reference: See project notes)
@route('/dalle_pics/<filename:path>')
def send_static(filename):
    return static_file(filename, root = './dalle-pics/' )

db_create()

run(host="127.0.0.1", port=8080, debug=True)
