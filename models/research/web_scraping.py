from dotenv import load_dotenv, find_dotenv
import requests
import os
import glob
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import datetime
import codecs
import re
import re
from serpapi import GoogleSearch
import traceback
import subprocess
from helper_function import Authentication
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

nltk.download('punkt')
nltk.download('stopwords')

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(r'--profile-directory=/Users/kisaki/Library/Application Support/Google/Chrome/Default') # removing for streamlit issue
driver = webdriver.Chrome( options=chrome_options) #r"/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/chromedriver" #service=Service(ChromeDriverManager().install()),

load_dotenv(find_dotenv())
# Directory to store URLs
dirname = os.path.dirname(__file__)
json_directory = os.path.join(dirname,'image_search_result')

SCRAPER_API_KEY = os.getenv('SCRAPER_API_KEY')
SERP_API_KEY = os.getenv('SERP_API_KEY')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
RED_CIRCLE_API_KEY = os.getenv('RED_CIRCLE_API_KEY')
KROGER_API_BASE_URL = os.getenv('KROGER_API_BASE_URL')


# create kroger access token
dirname = os.path.dirname(__file__)
kroger_path = os.path.join(dirname,'kroger_authorization.py')

# Run the script using subprocess
try:
    subprocess.run(["python", kroger_path], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running the script: {e}")

# get access token
# Specify the directory where JSON files are stored
json_directory_token = os.path.join(dirname,'token')

# Create an instance of the Authentication class
auth = Authentication(json_directory_token)

# Call the get_access_token method to retrieve the access token
kroger_access_token = auth.get_access_token()


# Define the directory where you want to save the JSON file
dirname = os.path.dirname(__file__)
loc_directory = os.path.join(dirname,'location')
# Get a list of JSON files in the directory
location_json_files = glob.glob(os.path.join(loc_directory, "*.json"))

# Check if any JSON files were found
if location_json_files:
    # Sort JSON files by modification time (most recent first)
    location_json_files.sort(key=os.path.getmtime, reverse=True)
    
    # Get the path to the most recent JSON file
    most_recent_json_file_kroger = location_json_files[0]

    # Now, you can work with the most recent JSON file
    print(f"The most recent LOCATION JSON file is: {most_recent_json_file_kroger}")
    kroger_location_jsonpath = most_recent_json_file_kroger
else:
    print("No JSON files found in the directory.")


def retrieve_json(json_directory):
    # Get a list of JSON files in the directory
    json_files = glob.glob(os.path.join(json_directory, "*.json"))

    # Check if there are any JSON files
    if not json_files:
        print("No JSON files found in the directory.")
    else:
        # Find the most recently modified JSON file
        most_recent_json_file = max(json_files, key=os.path.getmtime)

        # Load and parse the JSON data from the most recent file
        try:
            with open(most_recent_json_file, "r") as json_file:
                most_recent_json_data = json.load(json_file)
                #print(f"Most recent JSON file: {most_recent_json_file}")
                return most_recent_json_data
            # You can now work with the most_recent_json_data dictionary as needed
        except Exception as e:
            print(f"Error loading JSON file: {e}")

def filter_results(most_recent_json_data): # add more filter e.g. Walmart, Costco, Wholefoods
            
    filtered_results = []
    # Iterate through the results for each image
    for image_key, image_data in most_recent_json_data.items():
        # Create a set to store unique sources for each image_key
        unique_sources = set()
        # Check if the specific source is in the visual matches for the image
        visual_matches = image_data.get("visual_matches", [])
        for match in visual_matches[:1]:
            source = match.get("source")
            # source in specific_source and # removing this condiiton 
            if source not in unique_sources: # If the source matches the specific source, add the image_key and image_data to the list
                # modify this logic to filter further to just get one retail link for each product
                filtered_results.append({
                    "image_key": image_key,
                    "visual_matches": match
                })
                unique_sources.add(source)
            else:
                pass
    return filtered_results

# Define a function to clean the strings
def clean_string(value):
    if isinstance(value, str):
        # Replace '\u' with spaces and remove '$' and leading/trailing whitespaces
        cleaned_str = re.sub(r'[\/\\uU+200E$]', '', codecs.decode(value.encode(), 'unicode_escape')).replace(r'/', '').replace('$', '').strip() #
        return cleaned_str
    else:
        return value

# Clean the JSON data
def clean_json(data):
    if isinstance(data, dict):
        return {key: clean_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_json(item) for item in data]
    else:
        return clean_string(data)


def retrieve_price_value(filtered_results, SCRAPER_API_KEY=SCRAPER_API_KEY):
    
    for result in filtered_result:
        visual_matches = result.get("visual_matches", [])
        for match_ in visual_matches:
            source = match_.get("source")
            link = match_.get("link")
            source = match_.get("source")
            rating = match_.get("rating")
            reviews = match_.get("reviews")
            price = match_.get("price")
            
            if price is not None:
                currency = price.get("currency") 
                value = price.get("extracted_value")
                if currency == '$':
                    match_["lens_price"] = value 

    return filtered_results

# Function to read the first "locationId" from a JSON file
def read_first_location_id_from_json(filename):
    try:
        with open(filename, "r") as json_file:
            data = json.load(json_file)
            if data.get("data"):
              if isinstance(data.get("data"), list):
                locationId = data.get("data")[0].get("locationId", "")
                print(f"location id is {locationId}")
                return locationId

              else:
                locationIdd = data.get("data").get("locationId", "")
                print(f"location id is {locationId}")
                return locationId
            else: 
              return ""
    except Exception as e:
        print(f"Error reading the first locationId from JSON file: {str(e)}")
        return None

# Retrieve the first locationId from the JSON file #update the file name
location_id = read_first_location_id_from_json(kroger_location_jsonpath)
print(location_id)
# term will be title here
def kroger_get_products(location_id, term):    
    # Use locationId as filter (if) selected by user
    #search_by_location = ""
    #term = ", ".join(term.split()[:7])
    if location_id:
        search_by_location = f"filter.locationId={location_id}&"
    print(location_id)
    # Building product URL
    # Query String (?filter.locationId={location_id}&filter.term={term})
    products_url = f"{KROGER_API_BASE_URL}/v1/products?{search_by_location}filter.term={term}"
    
    # Product request body

    # find most recent access token in token folder and retrive the token and embed it
    headers = {
        "Authorization": f"bearer {kroger_access_token}",
        "Accept": "application/json"
    }
    print(f"this is Kroger url: {products_url}")
    products_response = requests.get(products_url, headers=headers)
    
    # Return JSON object
    return products_response.json()

def process_title(title):
    # Tokenize and remove stop words
    rep = {"trader": "", "joe": ""} # define desired replacements here

    # use these three lines to do the replacement
    rep = dict((re.escape(k), v) for k, v in rep.items()) 
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], title.lower())

    stop_words = set(stopwords.words('english'))
    pattern = r'[^A-Za-z0-9]+'
    removed_title = re.sub(pattern, ' ', text).lower()
    word_tokens = word_tokenize(removed_title)
    filtered_tokens = [w for w in word_tokens if not w.lower() in stop_words][:7]

    # Join the filtered tokens into a string with '%20' between words
    processed_title = '%20'.join(filtered_tokens)

    return processed_title

def toggle_in_stock(in_stock):
    # Toggle the value: If True, change to False; if False, change to True
    return not in_stock

def main():
    filtered_results = filter_results(most_recent_json_data=retrieve_json(json_directory))
    product_data = []

    #source_values = ["Amazon", "Amazon.com"]
    walmart_sore_id = "2648"

    for result in filtered_results:
        visual_matches = result.get("visual_matches", [])
        title = visual_matches.get("title", "")
        print(f"title is {title}")
        source = visual_matches.get("source", "")
        print(f"source is {source}")
        link = visual_matches.get("link", "")
        rating = visual_matches.get("rating", "")
        reviews = visual_matches.get("reviews", "")
        price = visual_matches.get("price", "")

        try:
        # switiching from poduct_id search to organic query search
            # Define a regular expression pattern to match the last 9-10 digits
            # pattern = r'/(\d{9,10})$'

            # # Use re.search to find the pattern in the link
            # match = re.search(pattern, link)

            # # Check if a match is found
            # if match:
            #     # Extract the matched digits
            #     product_id = match.group(1)
            params = {
            # "engine": "walmart_product",
            # "product_id": product_id,
            "engine": "walmart",
            "query": title,
            "api_key": SERP_API_KEY,
            "store_id": walmart_sore_id #replace with requested store id /zipcode logic 
            }
            print("this is the scraping URL: {}".format(link))

            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract and save the first 5 items as a list of dictionaries
            organic_results = results.get("organic_results", [])
            first_4_results = organic_results[:3]

            store_info = results.get("search_information", "")
            for result in first_4_results:
                product_data.append({
                    "product_name": result.get("title", ""),
                    "product_id": result.get("product_id", ""),
                    "product_price": result.get("primary_offer", {}).get("offer_price", ""),
                    "product_brand_1": "Walmart",  # Change this as needed
                    "product_brand_2": result.get("seller_name", ""),
                    "product_item_weight": "",  # Add the appropriate field here
                    "product_dimensions": "",
                    "product_review_rating_count": result.get("reviews", ""),
                    "product_review_stars": result.get("rating", ""),
                    "product_link": result.get("product_page_url", ""),
                    "product_category_1": "",
                    "product_category_2": "",
                    "product_category_3": "",
                    "product_category_4": "",
                    "product_category_5": "",
                    "store_location_zipcode": store_info["location"].get("postal_code", ""),
                    "store_location_state": store_info["location"].get("province_code", ""),
                    "store_location_city": store_info["location"].get("city", ""),
                    "store_id": store_info["location"].get("store_id", ""),
                    "in_stock": toggle_in_stock(product_result.get("out_of_stock", ""))
                })
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred while scraping Walmart: {e}")
    
        try:
            # Target
            params = {
            'api_key': RED_CIRCLE_API_KEY,
            'search_term': title,
            'type': 'search',
            'delivery_type': 'buy_at_store',
            'include_out_of_stock': 'false'
            }

            # make the http GET request to RedCircle API
            target_result = requests.get('https://api.redcircleapi.com/request', params)

            # print the JSON response from RedCircle API
            #print(json.dumps(api_result.json()))

            api_result = target_result.json()
            categories = [category["name"] for category in api_result.get("categories", [])]
            zip = api_result.get("request_parameters", {}).get("customer_zipcode", "")
            product_result = api_result.get("search_results", [])

            # Extract desired information for each position
            for result in product_result:
                product_info = result.get("product", {})
                offers = result.get("offers", {}).get("primary", {})

                title = product_info.get("title", "")
                link = product_info.get("link", "")
                tcin = product_info.get("tcin", "")
                class_id = product_info.get("class_id")
                department_id = product_info.get("department_id")
                brand = product_info.get("brand","")
                brand_link = product_info.get("brand_link")
                rating = product_info.get("rating", "")
                ratings_total = product_info.get("ratings_total", "")
                price = offers.get("price", "")

                product_category_1 = categories[0] if len(categories) > 0 else None
                product_category_2 = categories[1] if len(categories) > 1 else None
                product_category_3 = categories[2] if len(categories) > 2 else None
                product_category_4 = categories[3] if len(categories) > 3 else None
                product_category_5 = categories[4] if len(categories) > 4 else None

                product_data.append({
                "product_name": title,
                "tcin": tcin, 
                "product_price": price,
                "product_brand_1": "Target",
                "product_brand_2": brand,
                "product_item_weight": "",
                "product_dimensions": "",
                "product_review_rating_count": ratings_total,
                "product_review_stars": rating,
                "product_link": link,
                "brand_link": brand_link,
                "product_category_1": product_category_1,
                "product_category_2": product_category_2,
                "product_category_3": product_category_3,
                "product_category_4": product_category_4,
                "product_category_5": product_category_5,
                "store_location_zipcode": zip,
                "store_location_state": "",
                "store_location_city": "",
                "store_id": "",
                "product_id": "",
                "in_stock": "in_stock", # only querying the in-stock items for Target as in params
                })


        except:
            traceback.print_exc()
            print(f"Failed to scrape Target website. Status code: {target_result.status_code}")

        # Kroger
        try: 
            processed_title = process_title(title)
            print(processed_title)
            kroger_result = kroger_get_products(location_id, processed_title)
            # Iterate through the data and create a dictionary for each product
            for product in kroger_result.get("data", [])[:3]:
                item = product.get("items", [])[0]
                product_categories = product.get("categories", [])
                product_category_1 = product_categories[0] if product_categories else ""
                product_dict = {
                    "product_id": product.get("productId", ""),
                    "upc": product.get("upc", ""),
                    "product_brand_1": "Kroger",
                    "product_brand_2": product.get("brand", ""),
                    "product_category_1": product_category_1,
                    "product_category_2": "",
                    "product_category_3": "",
                    "product_category_4": "",
                    "product_category_5": "",
                    "product_review_rating_count": "",
                    "product_review_stars": "",
                    "countryOrigin": product.get("countryOrigin", ""),
                    "product_name": product.get("description", ""),
                    "product_price": item.get("price", {}).get("regular", ""),
                    "product_price_promo": item.get("price", {}).get("promo", ""),
                    "product_dimensions": item.get("size", ""),
                    "product_item_weight": "",
                    "product_unit": item.get("soldBy", ""),
                    "store_location_zipcode": zip,
                    "store_location_state": "",
                    "store_location_city": "",
                    "store_id": "",
                    "product_link": link,
                    "brand_link": "",
                    #"in_stock": , # modify this based on the result below        
                    "inventory_stockLevel": item.get("inventory", {}).get("stockLevel", ""),
                }
                product_data.append(product_dict)
        except:
            traceback.print_exc()
            print(f"Failed to scrape Kroger website.")

    # Clean the JSON data
    cleaned_json_data = clean_json(product_data)

    return cleaned_json_data


if __name__ == "__main__":
    #main()
    results_data = main()

    # Define the directory where you want to save the JSON file
    save_directory = os.path.join(dirname,'webscrape_result')
    # Ensure the directory exists; create it if it doesn't
    os.makedirs(save_directory, exist_ok=True)
   
    date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    json_file_path = os.path.join(save_directory, "scrape_result_{}.json".format(date))

    with open(json_file_path, "w") as json_file:
        json.dump(results_data, json_file, indent=4, ensure_ascii=False)

    print(f"Scraped results have been saved to '{json_file_path}'.")


# figure out kroger API issue
# figure out why the original image is inserted into output folder

# why the output is []?
# limit the term up to 7
# add kroger results
# kroger why price doesn't show up?
