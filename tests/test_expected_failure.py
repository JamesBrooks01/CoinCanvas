import pytest
import requests

def test_update():
  base_url = 'http://127.0.0.1:5000'
  auth = 2
  headers = {"Authorization": f"Bearer {auth}"}
  data = {'query': "BTC", 'user': 'brooksjamesk01@gmail.com', 'type': 'Crypto'}
  actual = requests.post(f'{base_url}/update',data=data,headers=headers)
  assert actual.status_code == 401 