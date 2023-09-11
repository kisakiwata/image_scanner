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
from retail_config import specific_source

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(r'--profile-directory=/Users/kisaki/Library/Application Support/Google/Chrome/Default')
driver = webdriver.Chrome(options=chrome_options) #r"/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/chromedriver"

load_dotenv(find_dotenv())
json_directory = r"/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/image_search_result/"

SCRAPER_API_KEY = os.getenv('SCRAPER_API_KEY')

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

def filter_results(most_recent_json_data, specific_source = specific_source): # add more filter e.g. Walmart, Costco, Wholefoods
            
    filtered_results = []
    # Iterate through the results for each image
    for image_key, image_data in most_recent_json_data.items():
        # Check if the specific source is in the visual matches for the image
        visual_matches = image_data.get("visual_matches", [])
        for match in visual_matches:
            source = match.get("source")

            if source in specific_source: # If the source matches the specific source, add the image_key and image_data to the list
                filtered_results.append({
                    "image_key": image_key,
                    "visual_matches": match
                })
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

def main():
    filtered_results = filter_results(most_recent_json_data=retrieve_json(json_directory))
    product_data = []
    for result in filtered_results:
        visual_matches = result.get("visual_matches", [])
        source = visual_matches.get("source", "")
        link = visual_matches.get("link", "")
        rating = visual_matches.get("rating", "")
        reviews = visual_matches.get("reviews", "")
        price = visual_matches.get("price", "")

        payload = {
        'api_key': SCRAPER_API_KEY,
        'url':link,
        'autoparse': 'true',
        }
        headers = {
        'tz': 'GMT+00:00',
        }
        print("this is the scraping URL: {}".format(link))

        try:
            # Send a GET request to the ScraperAPI endpoint
            response = requests.get('https://api.scraperapi.com', headers=headers, params=payload)
            response.raise_for_status()
            if (
            response.status_code != 204 and
            response.headers["content-type"].strip().startswith("application/json")
            ):
                product = response.json()

                # Check if 'Customer Reviews' is available in product_information
                product_review_info = product["product_information"].get("Customer Reviews", {})
                ratings_count = product_review_info.get("ratings_count", "")
                stars = product_review_info.get("stars", "")
                
                if price is not None: 
                    product_price = price.get("extracted_value", "")
                else:
                    product_price = product.get("pricing", "")

                product_data.append({
                "product_name": product.get("name", ""),
                "product_price": product_price,
                "product_brand_1": source,
                "product_brand_2": product.get("brand", ""),
                "product_item_weight": product["product_information"].get("Item Weight", ""),
                "product_dimensions": product["product_information"].get("Dimensions", ""),
                "product_review_rating_count": ratings_count, #product["product_information"]["Customer Reviews"]["ratings_count"],
                "product_review_stars": stars, #product["product_information"]["Customer Reviews"]["stars"],
                "product_review_stars": link
                })


            elif response.status_code != 204: # come up with better error catching for different error codes, not html versions # work on walmart/wholefoods scraping
                try:
                    driver.get(link)
                    time.sleep(10)
                    product_name = driver.find_elements(By.CLASS_NAME, "ProductDetails_main__title__14Cnm")[0].text
                    price = driver.find_elements(By.CLASS_NAME, "ProductPrice_productPrice__price__3-50j")[0].text
                    dim = driver.find_elements(By.CLASS_NAME, "ProductPrice_productPrice__unit__2jvkA")[0].text
                    product_data.append({
                    "product_name": product_name ,
                    "product_price": price,
                    "product_brand_1": source,
                    "product_brand_2": "",
                    "product_item_weight": "",
                    "product_dimensions": dim,
                    "product_review_rating_count": "",
                    "product_review_stars": "",
                    })
                    #print(driver.page_source.encode("utf-8")) # this prints out the scraped texts

                except Exception as e:
                    print(f"An error occurred while scraping: {e}")

                # finally:
                #     # Close the Selenium WebDriver
                #     driver.quit()

            else:
                print(f"Failed to scrape the website. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    
    # Clean the JSON data
    cleaned_json_data = clean_json(product_data)

    # sanity check
    # Convert the cleaned data back to a JSON string
    #cleaned_json_string = json.dumps(cleaned_json_data, ensure_ascii=False)

    # Print the cleaned JSON string
    #print(cleaned_json_string)

    return cleaned_json_data


if __name__ == "__main__":
    #main()
    results_data = main()

    # Define the directory where you want to save the JSON file
    save_directory = r"/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/webscrape_result"

    # Ensure the directory exists; create it if it doesn't
    os.makedirs(save_directory, exist_ok=True)
   
    date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    json_file_path = os.path.join(save_directory, "scrape_result_{}.json".format(date))

    with open(json_file_path, "w") as json_file:
        json.dump(results_data, json_file, indent=4, ensure_ascii=False)

    print(f"Scraped results have been saved to '{json_file_path}'.")