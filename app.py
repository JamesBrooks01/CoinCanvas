from flask import Flask, render_template, request, make_response, redirect, session, url_for
from flask_migrate import Migrate
import os
from vercel_db import get_data, create_user, update_user, db
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
import requests
from datetime import date
import datetime
import orjson
import requests_cache


app = Flask(__name__)

# Note, the cache is memory only in this version due to Vercel being serverless. It can freely and easily be turned into a SQLite database in other implementations.
requests_cache.install_cache('requests_cache',backend='memory',expire_after=86400)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL2')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.environ.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

db.init_app(app)
migrate = Migrate(app,db)

def  fill_queries(user):
    if user == "guest@coincanvas.com":
        return [["F", "Stock"],["RACE", "Stock"]]
    data = get_data(user)
    if data == None:
        create_user(user)
        return []
    return_array = []
    for query in data.user_queries:
        if query not in return_array:
            return_array.append(query)
    return return_array

def api_grab(query,type):
    request_query = ''
    if type == 'Stock':
        request_query += f"{query}"
    elif type == 'Crypto':
        request_query += f'X:{query}USD'
    else:
        return 'Invalid Type'
    today = date.today()
    # The timedelta goes back 150 days to account for weekends which Polygon.io doesn't include for Stock Market Data so that the chart can always recieve a full 100 days of data.
    past = today - datetime.timedelta(150)
    base_url = 'https://api.polygon.io/v2/aggs/ticker/'
    end_url = f'/range/1/day/{past}/{today}?adjusted=true&sort=asc'
    auth = os.environ.get('POLYGON_API_KEY')
    header = {"Authorization": f'Bearer {auth}'}
    data = requests.get(f"{base_url}{request_query}{end_url}",headers=header)
    if data.status_code == 429:
        return 'Error'
    dict_converted_data = orjson.loads(data.text)
    if dict_converted_data['queryCount'] == 0:
        app_url = os.environ.get('APP_URL')
        user = session.get('user')
        user_auth = os.environ.get("APP_SECRET_KEY")
        user_header = {"Authorization": f"Bearer {user_auth}"}
        data = {
            "query": query,
            'user': user['userinfo']['email']
        }
        requests.delete(f'{app_url}/update',data=data,headers=user_header)
        return 'Invalid Query'
    sliced_data = dict_converted_data['results']
    # This is where the data gets santitized to include 100 days only. It just takes the last 100 entries from the response and returns it.
    sanitized_data = sliced_data[len(sliced_data)-100:]
    return sanitized_data

def graph(data):
    labels = [row['t'] for row in data]
    formatted_labels = []
    for label in labels:
        # This timestamp stuff is due to the return time being a nanosecond Unix timestamp which needs to be converted down to milliseconds for the converter to return the correct date.
        formatted_date = label // 1000
        timestamped_date = date.fromtimestamp(formatted_date)
        formatted_labels.append(str(timestamped_date))
    values = [row['c'] for row in data]

    return [formatted_labels,values]

@app.route("/")
def index():
    data = session.get('user')
    time_frame = request.args.get('timeframe',100)
    if data:
        user = fill_queries(data['userinfo']['email'])
        graphs = []
        for query in user:
            return_graph = api_grab(query[0],query[1])
            if return_graph == 'Error':
                error_message = "Too Many API Requests. Please wait a few minutes before trying again. If this error continues to appear, please contact the dev."
                return render_template('index.html',errortext=error_message, session=data)
            if return_graph == 'Invalid Query':
                error_message = "Invalid Query, Perhaps the name doesn't match the official name correctly or the type was selected wrong. Either refresh the page or try your query again. Thank You."
                return render_template('index.html',errortext=error_message, session=data)
            # This line appends the graphs to the list that gets passed to the template. It slices the graph according to the timeframe argument and returns the portion of the list that matches the desired timeframe.
            graphs.append(graph(return_graph[100-int(time_frame):]))
        return render_template("index.html", session=data, graphs=graphs, queries=user)
    else:
        # This line is to create a dummy user for the session when the site is first visited to create basic funtionaility for Guests.
        session['user'] = {'userinfo': {"email": 'guest@coincanvas.com', 'name': 'Guest', 'picture': 'https://cdn.pixabay.com/photo/2017/11/10/05/46/group-2935521_1280.png'}}
        return redirect('/')

@app.route("/login")
def login():
    data = session.get('user')
    # Due to the way the Guest user is implemented, when you "log in" as a user from a guest, the session needs to be cleared to make way for the new information.
    if data['userinfo']['name'] == "Guest":
        session.clear()
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    session['user'] = token
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        "https://" + os.environ.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("index", _external=True),
                "client_id": os.environ.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )        
    )

@app.route('/update',methods=["POST","DELETE"])
def update():
    user = request.form.get('user')
    if not user:
        return make_response('', 400)
    auth = request.authorization.token
    new_query = request.form.get('query')
    if auth == os.environ.get('APP_SECRET_KEY'):
        data = get_data(user)
        if not data:
            return make_response('', 400)
        if request.method == "POST":
            type = request.form.get('type')
            if type not in ['Stock', 'Crypto']:
                return make_response('', 400)
            new_array = [new_query,type]
            data_array = data.user_queries
            data_array.append(new_array)
            update_user(user,data_array)    
            return make_response('', 204)
        if request.method == "DELETE":
            data_array = data.user_queries
            for query in data_array:
                if query[0] == new_query:
                    data_array.remove(query)
            return_array = data_array
            update_user(user,return_array)
            return make_response('', 204)
    else:
        return make_response('', 401)

@app.route('/api', methods=['POST'])
def api():
    query = request.form.get('query')
    type = request.form.get('type')
    user = session.get('user')
    # This check is put in to prevent any requests being made to this route from outside the code.
    if not user:
        return make_response('', 400)
    if type not in ['Stock', 'Crypto']:
        return render_template('index.html', errortext="Invalid Type", session=user)
    new_query = [query,type]
    data = get_data(user['userinfo']['email'])
    if new_query not in data.user_queries:
        update_url = os.environ.get('APP_URL')
        user_auth = os.environ.get("APP_SECRET_KEY")
        user_header = {"Authorization": f"Bearer {user_auth}"}
        data = {
            "query": query,
            "type": type,
            'user': user['userinfo']['email']
        }
        requests.post(f'{update_url}/update',data=data,headers=user_header)

    return redirect(url_for('index'))

@app.route('/delete', methods=["POST"])
def delete():
    deletion_query = request.form.get('delete')
    update_url = os.environ.get('APP_URL')
    user = session.get('user')
    if not user:
        return make_response('', 400)
    user_auth = os.environ.get("APP_SECRET_KEY")
    user_header = {"Authorization": f"Bearer {user_auth}"}
    data = {
        "query": deletion_query,
        'user': user['userinfo']['email']
    }
    requests.delete(f'{update_url}/update',data=data,headers=user_header)
    return redirect(url_for('index'))
