import pytest
import requests
from flask import Flask
from flask_testing import TestCase
import os
from models import db
from vercel_db import get_data, create_user, update_user
from dotenv import load_dotenv

load_dotenv()

user = 'fake_user@pytest.net'


class IntendedTests(TestCase):

  render_templates = False

  def create_app(self):
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_db.sqlite3'
    db.init_app(app)
    return app

  def setUp(self):
    db.create_all()
    create_user(user)

  def tearDown(self):
    db.session.remove()
    db.drop_all()

class dbTests(IntendedTests):

  # @pytest.mark.skip("TODO")
  def test_create_user(self):
    actual = get_data(user)
    assert actual

  # @pytest.mark.skip("TODO")
  def test_get_data(self):
    data = get_data(user)
    actual = data.user_queries
    expected = []
    assert actual == expected

  # @pytest.mark.skip("TODO")
  def test_update_user(self):
    update_user(user,[["TSLA",'Stock']])
    data = get_data(user)
    actual = data.user_queries
    expected = [['TSLA','Stock']]
    assert actual == expected



# @pytest.mark.skip("TODO")
def test_index():
  actual = requests.get('https://coin-canvas-eight.vercel.app/')
  assert actual.status_code == 200

# @pytest.mark.skip("TODO")
def test_update():
  base_url = 'http://127.0.0.1:5000'
  auth = os.environ.get('APP_SECRET_KEY')
  headers = {"Authorization": f"Bearer {auth}"}
  data = {'query': "BTC", 'user': 'brooksjamesk01@gmail.com', 'type': 'Crypto'}
  actual = requests.post(f'{base_url}/update',data=data,headers=headers)
  assert actual.status_code == 204

# @pytest.mark.skip("TODO")
def test_delete():
  base_url = 'http://127.0.0.1:5000'
  auth = os.environ.get('APP_SECRET_KEY')
  headers = {"Authorization": f"Bearer {auth}"}
  data = {'query': "BTC", 'user': 'brooksjamesk01@gmail.com', 'type': 'Crypto'}
  actual = requests.delete(f'{base_url}/update',data=data,headers=headers)
  assert actual.status_code == 204

# @pytest.mark.skip("TODO")
def test_logout_redirect():
    response = requests.get('http://127.0.0.1:5000/logout')
    assert len(response.history) == 2
    print(response.content)
    assert b'<h1>Coin Canvas</h1>' in response.content 
