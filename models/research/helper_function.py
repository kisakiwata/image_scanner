import requests
import json
import os
from glob import glob
from datetime import datetime, timedelta, timezone

# Sample authentication object
class Authentication:
    def __init__(self, json_directory):
        self.json_directory = json_directory
    def get_access_token(self):
        # Calculate the timestamp 18 minutes ago in UTC
        eighteen_hours_ago_utc = datetime.now(timezone.utc) - timedelta(minutes=18)
        
        # List JSON files in the specified directory
        json_files = glob(os.path.join(self.json_directory, "*.json"))
        
        if not json_files:
            return None  # No JSON files found
        
        # Filter JSON files produced within the last 18 minutes
        recent_json_files = [
            file for file in json_files
            if datetime.utcfromtimestamp(os.path.getmtime(file)).replace(tzinfo=timezone.utc) >= eighteen_hours_ago_utc
        ]
        
        if not recent_json_files:
            return None  # No recent JSON files found
        
        # Sort recent JSON files by modification time (most recent first)
        recent_json_files.sort(key=lambda file: os.path.getmtime(file), reverse=True)
        
        # Load the most recent JSON file
        most_recent_file = recent_json_files[0]
        
        with open(most_recent_file, "r") as json_file:
            try:
                token_data = json.load(json_file)
                return token_data.get("access_token")
            except json.JSONDecodeError:
                return None  # Failed to decode JSON

# Specify the directory where JSON files are stored
dirname = os.path.dirname(__file__)
json_directory = os.path.join(dirname,'token')

# Create an instance of the Authentication class
auth = Authentication(json_directory)

# Call the get_access_token method to retrieve the access token
access_token = auth.get_access_token()

if access_token is not None:
    print(f"Access token found")
else:
    print("No valid access token found within the last 18 minutes.")

def location_on_click():
    zip_code = input("Enter Zip Code: ")  # Assuming you get the Zip Code as user input
    access_token = auth.get_access_token()  # Assuming you have a method to get the access token
    locations = get_locations(zip_code, access_token)
    if locations:
        # Display locations
        display_locations(locations)
     # Save the JSON output to a file
        save_json_to_file(locations, filename)
    else:
        print("No locations found.")

def get_locations(zip_code, access_token):
    base_url = "https://api.kroger.com"
    endpoint = "/v1/locations"
    
    # Build location URL
    location_url = f"{base_url}{endpoint}?filter.zipCode.near={zip_code}"
    
    # Location request headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    location_response = requests.get(location_url, headers=headers)
    
    # Return JSON object
    return location_response.json()

# Define a function to display the locations
def display_locations(locations):
    print(f"Locations: {locations}")

def save_json_to_file(data, filename):
    try:
        with open(filename, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"JSON data saved to {filename}")
    except Exception as e:
        print(f"Error saving JSON data to {filename}: {str(e)}")

# Specify the path where you want to save the JSON file
# Define the directory where you want to save the JSON file
dirname = os.path.dirname(__file__)
save_directory = os.path.join(dirname,'location')
# Ensure the directory exists; create it if it doesn't
os.makedirs(save_directory, exist_ok=True)
date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
filename = os.path.join(save_directory, "location_{}.json".format(date))


if __name__ == "__main__":
    location_on_click()
