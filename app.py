from flask import Flask, render_template, request, jsonify, make_response, redirect, session, url_for
from flask_migrate import Migrate
from models import db, User
import os
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
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

@app.route("/")
def index():
    data = session.get('user')
    return render_template("index.html", session=data)



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

@app.route('/delete')
def delete():
    id = request.form['id']
    result = User.query.filter_by(id=id).first()
    db.session.delete(result)
    db.session.commit()
    return make_response('', 410)

@app.route('/update')
def update():
    id = request.form['id']
    new_query = request.form['query']
    result = db.session.execute(db.select(User).filter_by(id=id)).scalar_one()
    array = [new_query]
    new_array = result.user_queries + array
    result.user_queries = new_array
    db.session.commit()
    return make_response('', 201)

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



