import pytest
import requests
import os
from dotenv import load_dotenv

load_dotenv()

production_user= os.environ.get('TEST_USER')
app_url = os.environ.get('APP_URL')

# @pytest.mark.skip("TODO")
def test_update_invalid_auth():
  auth = 2
  headers = {"Authorization": f"Bearer {auth}"}
  data = {'query': "BTC", 'user': production_user, 'type': 'Crypto'}
  actual = requests.post(f'{app_url}/update',data=data,headers=headers)
  assert actual.status_code == 401 

# @pytest.mark.skip("TODO")
def test_delete():
  data = {'delete': "BTC",}
  actual = requests.post(f'{app_url}/delete',data=data)
  assert actual.status_code == 400

# @pytest.mark.skip("TODO")
def test_new_query():
  data = {'query': "BTC", 'type': "Crypto"}
  actual = requests.post(f'{app_url}/api',data=data)
  assert actual.status_code == 400

def test_update_invalid_user():
  auth = os.environ.get('APP_SECRET_KEY')
  headers = {"Authorization": f"Bearer {auth}"}
  data = {'query': "BTC", 'user': 'invalid@email.com', 'type': 'Crypto'}
  actual = requests.post(f'{app_url}/update',data=data,headers=headers)
  assert actual.status_code == 400

# @pytest.mark.skip("TODO")
def test_update_invalid_type():
  auth = os.environ.get('APP_SECRET_KEY')
  headers = {"Authorization": f"Bearer {auth}"}
  data = {'query': "BTC", 'user': production_user, 'type': 'Invalid'}
  actual = requests.post(f'{app_url}/update',data=data,headers=headers)
  assert actual.status_code == 400 