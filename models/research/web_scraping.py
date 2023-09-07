# come up with the strucuture to filter "source" to credible large supermarkets/grocery manufacturers
# after finding appropriate image results that match the above criteria -> is there "price" or null? -> go to "link"
# in the link, scrape the website with scrapeAPI
# scrape price information 

from dotenv import load_dotenv, find_dotenv
import requests
import os
import glob
import json

# Define the directory where your JSON files are stored
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

def filter_results(most_recent_json_data, specific_source = ["Amazon.com", "Trader Joe's"]): # add more filter e.g. Walmart, Costco, Wholefoods
            
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
        source = visual_matches.get("source")
        link = visual_matches.get("link")
        source = visual_matches.get("source")
        rating = visual_matches.get("rating")
        reviews = visual_matches.get("reviews")
        price = visual_matches.get("price")

        payload = {
        'api_key': SCRAPER_API_KEY,
        'url':link,
        'autoparse': 'true',
        }
        print("this is the scraping URL: {}".format(link))

        try:
            # Send a GET request to the ScraperAPI endpoint
            response = requests.get('https://api.scraperapi.com', params=payload)
            response.raise_for_status()
            if (
            response.status_code != 204 and
            response.headers["content-type"].strip().startswith("application/json")
            ):
                product = response.json()

                product_data.append({
                "product_name": product["name"],
                "product_price": product["pricing"],
                "product_brand": product["brand"],
                "product_item_weight": product["product_information"]["Item Weight"],
                "product_dimensions": product["product_information"]["Dimensions"],
                "product_review_rating_count": product["product_information"]["Customer Reviews"]["ratings_count"],
                "product_review_stars": product["product_information"]["Customer Reviews"]["stars"],
                })


            elif response.status_code != 204:
                print(response.text)

            else:
                print(f"Failed to scrape the website. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    
    print(product_data)
    #return product_data


# if no pricing info in scraped info, use the pricing info in serpAPI

if __name__ == "__main__":
    main()
