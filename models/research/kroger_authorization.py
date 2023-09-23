import requests
import base64
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

CLIENT_ID = os.getenv('CLIENT_ID')
print(CLIENT_ID)
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
print(CLIENT_SECRET)
SCOPE = os.getenv('SCOPE')

url = "https://api.kroger.com/v1/connect/oauth2/token"

# Replace with your actual values
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
base64_credentials = base64.b64encode(credentials.encode()).decode()

url = "https://api.kroger.com/v1/connect/oauth2/token"
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {base64_credentials}"
}
data = {
    "grant_type": "client_credentials",
    "scope": SCOPE
}

response = requests.post(url, headers=headers, data=data)

if response.status_code == 200:
    print("Token request successful.")
    access_token = response.json().get("access_token")
    print(f"Access Token: {access_token}")
else:
    print("Token request failed.")
    print(f"Response Code: {response.status_code}")
    print(f"Response Content: {response.text}")



# save the results in json file - create a folder for token
# retrieve most recent access_token
# embed in localtion script (try with curl command)
# embed in product information script