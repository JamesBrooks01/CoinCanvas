from flask import Flask, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app,db)

@app.route("/")
def index():
    return render_template("index.html")
 

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        email = request.form['email']
        query = request.form['query']
        formatted_query = [query]
        new_user = User(user_email=email, user_queries=formatted_query)
        db.session.add(new_user)
        db.session.commit()
        return f"Done!!"
    
@app.route('/create')
def create():
    email = request.form['email']
    query = request.form['query']
    formatted_query = [query]
    new_entry = User(user_email=email, user_queries=formatted_query)
    db.session.add(new_entry)
    db.session.commit()
    return make_response('', 201)

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