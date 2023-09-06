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
            "engine": "google_lens",   # SerpApi search engine
            "url": image_url,             # image URL to perform a reverse search
            "hl": "en",                         # language of the search
        }
        
        search = GoogleSearch(params)           # where data extraction happens on the SerpApi backend
        results = search.get_dict()             # JSON -> Python dictionary

        if results.get("visual_matches"):
            google_reverse_image_data[f"results for image {index}"]["visual_matches"] = []

            for result in results["visual_matches"][:6]:  #  Save only the top 6 results
                visual_matches = {
                    "position": result.get("position"),
                    "title": result.get("title"),
                    "link": result.get("link"),
                    "source": result.get("source"),
                    "source_icon": result.get("source_icon"),
                    "rating": result.get("rating"),
                    "reviews": result.get("reviews"),
                    "price": result.get("price"),
                    "rating": result.get("rating"),
                    "reviews": result.get("reviews")
                }

                google_reverse_image_data[f"results for image {index}"]["visual_matches"].append(visual_matches)

        # Some queries may not include this information
        if results.get("text_results"):
            google_reverse_image_data[f"results for image {index}"]["text_results"] = []

            combined_text = []
            for result in results["text_results"]:  # [:3] Save only the top 3 results:                
                combined_text.append(result.get("text"))
            
            combined_text_dict = {"text": " ".join(combined_text)}
            google_reverse_image_data[f"results for image {index}"]["text_results"].append(combined_text_dict)
    
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