import pytest
import requests
from flask import Flask
from flask_testing import TestCase
import os
from models import db
from vercel_db import get_data, create_user, update_user
from dotenv import load_dotenv

load_dotenv()

fake_user = 'fake_user@pytest.net'
production_user= os.environ.get('TEST_USER')
app_url = os.environ.get('APP_URL')
auth = os.environ.get('APP_SECRET_KEY')
headers = {"Authorization": f"Bearer {auth}"}


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
    create_user(fake_user)

  def tearDown(self):
    db.session.remove()
    db.drop_all()

class dbTests(IntendedTests):

  # @pytest.mark.skip("TODO")
  def test_create_user(self):
    actual = get_data(fake_user)
    assert actual

  # @pytest.mark.skip("TODO")
  def test_get_data(self):
    data = get_data(fake_user)
    actual = data.user_queries
    expected = []
    assert actual == expected

  # @pytest.mark.skip("TODO")
  def test_update_user(self):
    update_user(fake_user,[["TSLA",'Stock']])
    data = get_data(fake_user)
    actual = data.user_queries
    expected = [['TSLA','Stock']]
    assert actual == expected



# @pytest.mark.skip("TODO")
def test_index():
  actual = requests.get(app_url)
  assert actual.status_code == 200

# @pytest.mark.skip("TODO")
def test_update():
  data = {'query': "BTC", 'user': production_user, 'type': 'Crypto'}
  actual = requests.post(f'{app_url}/update',data=data,headers=headers)
  assert actual.status_code == 204

# @pytest.mark.skip("TODO")
def test_delete():
  data = {'query': "BTC", 'user': production_user, 'type': 'Crypto'}
  actual = requests.delete(f'{app_url}/update',data=data,headers=headers)
  assert actual.status_code == 204

# @pytest.mark.skip("TODO")
def test_logout_redirect():
    response = requests.get(f'{app_url}/logout')
    assert len(response.history) == 2
    assert b'<h1>Coin Canvas</h1>' in response.content 
