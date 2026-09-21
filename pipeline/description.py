import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import json


load_dotenv()

API_KEY_REED = os.environ.get('API_KEY_REED')
headers = {'username': API_KEY_REED, 'password': ''}
test_url = "https://www.reed.co.uk/api/1.0/jobs/57173170"

print("contacting api")
response = requests.get(test_url, auth=HTTPBasicAuth(API_KEY_REED, ""))
print("no error from api")
print(response.status_code)

hopefully_json = response.json()

# with open('raw_data.json', 'w') as file:
#     json.dump(hopefully_json, file)

print(json.dumps(hopefully_json, indent=4, sort_keys=True))