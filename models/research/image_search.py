from serpapi import GoogleSearch
import os
import json
import datetime


file_path = r"/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/result_urls/uploaded_urls.txt"

def read_uploaded_urls(file_path):
    urls = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                # Remove any leading/trailing whitespace and append to the list
                urls.append(line.strip())
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    return urls

image_urls = read_uploaded_urls(file_path)

def main():
    google_reverse_image_data = {}

    for index, image_url in enumerate(image_urls, start=1):
        google_reverse_image_data[f"results for image {index}"] = {}

        params = {
            "api_key": "635b7526a4291ddec12eba9c3bdad8c7fdacf6ea91fad10e3b3c93add91aee7c", # https://serpapi.com/manage-api-key
            "engine": "google_reverse_image",   # SerpApi search engine
            "image_url": image_url,             # image URL to perform a reverse search
            "location": "Dallas",               # location from where search comes from
            "hl": "en",                         # language of the search
            "gl": "us"                          # country of the search
            # other parameters
        }
        
        search = GoogleSearch(params)           # where data extraction happens on the SerpApi backend
        results = search.get_dict()             # JSON -> Python dictionary

        # Check if "knowledge_graph" information is present
        if "knowledge_graph" in results:
            knowledge_graph = {
                "title": results["knowledge_graph"].get("title"),
                "description": results["knowledge_graph"].get("description")
            }

            google_reverse_image_data[f"results for image {index}"]["knowledge_graph"] = knowledge_graph


        # Some queries may not include organic results
        if results.get("image_results"):
            google_reverse_image_data[f"results for image {index}"]["organic_results"] = []

            for result in results["image_results"][:3]:  # Save only the top 3 results
                image_results = {
                    "position": result.get("position"),
                    "title": result.get("title"),
                    "link": result.get("link"),
                    "snippet": result.get("snippet")
                }

                google_reverse_image_data[f"results for image {index}"]["organic_results"].append(image_results)

        # Some queries may not include this information
        if results.get("inline_images"):
            google_reverse_image_data[f"results for image {index}"]["inline_images"] = []

            for result in results["inline_images"]:  # [:3] Save only the top 3 results:
                google_reverse_image_data[f"results for image {index}"]["inline_images"].append({
                    "source": result.get("source"),
                    "thumbnail": result.get("thumbnail")
                })

    return google_reverse_image_data

if __name__ == "__main__":
    results_data = main()

    # Define the directory where you want to save the JSON file
    save_directory = r"/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/image_search_result"

    # Ensure the directory exists; create it if it doesn't
    os.makedirs(save_directory, exist_ok=True)
   
    date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    json_file_path = os.path.join(save_directory, "top_results_{}.json".format(date))

    with open(json_file_path, "w") as json_file:
        json.dump(results_data, json_file, indent=4, ensure_ascii=False)

    print(f"Top two results have been saved to '{json_file_path}'.")