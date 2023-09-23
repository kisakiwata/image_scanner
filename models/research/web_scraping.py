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
import re
from serpapi import GoogleSearch
import traceback

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
KROGER_ACCESS_TOKEN = os.getenv('TOKEN_1')


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
        # Create a set to store unique sources for each image_key
        unique_sources = set()
        # Check if the specific source is in the visual matches for the image
        visual_matches = image_data.get("visual_matches", [])
        for match in visual_matches:
            source = match.get("source")

            if source in specific_source and source not in unique_sources: # If the source matches the specific source, add the image_key and image_data to the list
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

async def get_products(term):    
    # Use stored locationId
    location_id = localStorage.getItem("locationId")
    
    # Use locationId as filter (if) selected by user
    search_by_location = ""
    if location_id:
        search_by_location = f"filter.locationId={location_id}&"
    
    # Building product URL
    # Query String (?filter.locationId={location_id}&filter.term={term})
    products_url = f"{KROGER_API_BASE_URL}/v1/products?{search_by_location}filter.term={term}"
    
    # Product request body
    headers = {
        "Authorization": f"bearer {KROGER_ACCESS_TOKEN}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    products_response = requests.get(products_url, headers=headers)
    
    # Return JSON object
    return products_response.json()


def main():
    filtered_results = filter_results(most_recent_json_data=retrieve_json(json_directory))
    product_data = []

    source_values = ["Amazon", "Amazon.com"]
    walmart_sore_id = "2648"

    for result in filtered_results:
        visual_matches = result.get("visual_matches", [])
        title = visual_matches.get("title", "")
        source = visual_matches.get("source", "")
        link = visual_matches.get("link", "")
        rating = visual_matches.get("rating", "")
        reviews = visual_matches.get("reviews", "")
        price = visual_matches.get("price", "")

        if (
        source in source_values #and
        #response.headers["content-type"].strip().startswith("application/json")
        ):
        
            payload = {
            'api_key': SCRAPER_API_KEY,
            'url':link,
            'autoparse': 'true',
            }
            headers = {
            'tz': 'GMT+00:00',
            }
            print("this is the scraping URL: {}".format(link))

            # try: # this is only for Amazon URLs
            #     # Send a GET request to the ScraperAPI endpoint
            #     response = requests.get('https://api.scraperapi.com', headers=headers, params=payload)
            #     response.raise_for_status()
            #     product = response.json()

            #     if  response.status_code != 204:
            #         # Check if 'Customer Reviews' is available in product_information
            #         product_review_info = product["product_information"].get("Customer Reviews", {})
            #         ratings_count = product_review_info.get("ratings_count", "")
            #         stars = product_review_info.get("stars", "")
                    
            #         if price is not None: 
            #             product_price = price.get("extracted_value", "")
            #         else:
            #             product_price = product.get("pricing", "")

            #         product_data.append({
            #         "product_name": product.get("name", ""),
            #         "product_price": product_price,
            #         "product_brand_1": source,
            #         "product_brand_2": product.get("brand", ""),
            #         "product_item_weight": product["product_information"].get("Item Weight", ""),
            #         "product_dimensions": product["product_information"].get("Dimensions", ""),
            #         "product_review_rating_count": ratings_count, #product["product_information"]["Customer Reviews"]["ratings_count"],
            #         "product_review_stars": stars, #product["product_information"]["Customer Reviews"]["stars"],
            #         "product_link": link
            #         })
            # except requests.exceptions.RequestException as e:
            #     traceback.print_exc()
            #     print(f"An error occurred: {e}")

        elif source == "Walmart": # come up with better error catching for different error codes, not html versions # work on walmart/wholefoods scraping
            try:
                # Define a regular expression pattern to match the last 9-10 digits
                pattern = r'/(\d{9,10})$'

                # Use re.search to find the pattern in the link
                match = re.search(pattern, link)

                # Check if a match is found
                if match:
                    # Extract the matched digits
                    product_id = match.group(1)
                    params = {
                    "engine": "walmart_product",
                    "product_id": product_id,
                    "api_key": SERP_API_KEY,
                    "store_id": walmart_sore_id #replace with requested store id /zipcode logic 
                    }
                    print("this is the scraping URL: {}".format(link))

                    search = GoogleSearch(params)
                    results = search.get_dict()
                    product_result = results.get("product_result", "")

                    store_info = results.get("search_information", "")

                    if product_result:
                        # Extract the review
                        reviews = product_result['reviews']

                        if isinstance(reviews, dict):
                            count = reviews.get("count", "")
                            rating = reviews.get("rating", "")
                        else:
                            count = 0
                            rating = ""
                            
                    
                        # Extract the short description
                        short_description = product_result['short_description_html']

                        # Split the short description by "<br />"
                        split_description = short_description.split('<br />')

                        # Find and print the part after "Size"
                        for part in split_description:
                            if 'Size :' in part:
                                size_info = part.split('Size :')[1].strip()
                            else: size_info = ""


                        product_categories = product_result.get("categories", [])

                        product_category_1 = product_categories[0]["name"] if len(product_categories) > 0 else None
                        product_category_2 = product_categories[1]["name"] if len(product_categories) > 1 else None
                        product_category_3 = product_categories[2]["name"] if len(product_categories) > 2 else None
                        product_category_4 = product_categories[3]["name"] if len(product_categories) > 3 else None
                        product_category_5 = product_categories[4]["name"] if len(product_categories) > 4 else None


                        #print(f"walmart scraped results 2: {product_result}")
                        product_data.append({
                        "product_name": product_result.get("title", ""),
                        "product_price": product_result.get("price_map", "").get("price", ""),
                        "product_brand_1": source,
                        "product_brand_2": product_result.get("manufacturer", ""),
                        "product_item_weight": "",
                        "product_dimensions": size_info,
                        "product_review_rating_count": count,
                        "product_review_stars": rating,
                        "product_link": link,
                        "product_category_1": product_category_1,
                        "product_category_2": product_category_2,
                        "product_category_3": product_category_3,
                        "product_category_4": product_category_4,
                        "product_category_5": product_category_5,
                        "store_location_zipcode": store_info["location"].get("postal_code", ""),
                        "store_location_state": store_info["location"].get("province_code", ""),
                        "store_location_city": store_info["location"].get("city", ""),
                        "store_id": store_info["location"].get("store_id", ""),
                        "product_id": product_id,
                        "in_stock": product_result.get("in_stock", ""),

                        }) # if no info, go to different walmart or similar product close to the zipcode?
                else:
                    print(f"Walmart - There is no product id.")

            except Exception as e:
                traceback.print_exc()
                print(f"An error occurred while scraping Walmart: {e}")

        elif source == "Trader Joe's": # come up with better error catching for different error codes, not html versions # work on walmart/wholefoods scraping
            try:
                driver.get(link)
                time.sleep(10)
                print("this is the scraping URL: {}".format(link))
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
                traceback.print_exc()
                print(f"An error occurred while scraping: {e}")

            # finally:
            #     # Close the Selenium WebDriver
            #     driver.quit()
        
        else:
            try:
                # Target
                params = {
                'api_key': RED_CIRCLE_API_KEY,
                'search_term': title,
                'type': 'search',
                'delivery_type': 'buy_at_store',
                'include_out_of_stock': 'true'
                }

                # make the http GET request to RedCircle API
                api_result = requests.get('https://api.redcircleapi.com/request', params)

                # print the JSON response from RedCircle API
                print(json.dumps(api_result.json()))

                # Costco

                # Kroger 




            except:
                traceback.print_exc()
                print(f"Failed to scrape Target website. Status code: {response.status_code}")


    
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
    save_directory = os.path.join(dirname,'webscrape_result')
    # Ensure the directory exists; create it if it doesn't
    os.makedirs(save_directory, exist_ok=True)
   
    date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    json_file_path = os.path.join(save_directory, "scrape_result_{}.json".format(date))

    with open(json_file_path, "w") as json_file:
        json.dump(results_data, json_file, indent=4, ensure_ascii=False)

    print(f"Scraped results have been saved to '{json_file_path}'.")