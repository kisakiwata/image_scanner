import datetime
import requests
import base64
import os
from dotenv import load_dotenv, find_dotenv
import json

load_dotenv(find_dotenv())

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
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

    # Create a dictionary to store the access token
    token_data = {
        "access_token": access_token
    }

    # Specify the path where you want to save the JSON file
    # Define the directory where you want to save the JSON file
    dirname = os.path.dirname(__file__)
    save_directory = os.path.join(dirname,'token')
    # Ensure the directory exists; create it if it doesn't
    os.makedirs(save_directory, exist_ok=True)

    date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_path = os.path.join(save_directory, "access_token_{}.json".format(date))

    # Write the access token data to the JSON file
    with open(file_path, "w") as json_file:
        json.dump(token_data, json_file)

    print(f"Access Token: {access_token}")
else:
    print("Token request failed.")
    print(f"Response Code: {response.status_code}")
    print(f"Response Content: {response.text}")



# save the results in json file - create a folder for token
# retrieve most recent access_token
# embed in localtion script (try with curl command)
# embed in product information script