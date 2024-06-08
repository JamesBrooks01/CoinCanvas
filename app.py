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
    past = today - datetime.timedelta(150)
    base_url = 'https://api.polygon.io/v2/aggs/ticker/'
    end_url = f'/range/1/day/{past}/{today}?adjusted=true&sort=asc'
    auth = os.environ.get('POLYGON_API_KEY')
    header = {"Authorization": f'Bearer {auth}'}
    data = requests.get(f"{base_url}{request_query}{end_url}",headers=header)
    if data.status_code == 429:
        return 'Error'
    dict_converted_data = orjson.loads(data.text)
    sliced_data = dict_converted_data['results']
    sanitized_data = sliced_data[len(sliced_data)-100:]
    return sanitized_data

def graph(data):
    labels = [row['t'] for row in data]
    formatted_labels = []
    for label in labels:
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
            graphs.append(graph(return_graph[100-int(time_frame):]))
        return render_template("index.html", session=data, graphs=graphs, queries=user)
    else:
        return render_template('index.html')


@app.route("/login")
def login():
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
    if type == None:
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
    user_auth = os.environ.get("APP_SECRET_KEY")
    user_header = {"Authorization": f"Bearer {user_auth}"}
    data = {
        "query": deletion_query,
        'user': user['userinfo']['email']
    }
    requests.delete(f'{update_url}/update',data=data,headers=user_header)
    return redirect(url_for('index'))
