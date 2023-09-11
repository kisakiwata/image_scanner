import subprocess
import os
import shutil

# List of scripts to run in order
scripts_to_run = [
    ("models/research/inference.py", "models/research/outputs/"),
    ("models/research/app.py", "models/research/result_urls/"),
    ("models/research/image_search.py", "models/research/image_search_result/"),
    ("models/research/web_scraping.py", "models/research/webscrape_result/")
]

# Create output directories if they don't exist
for output_dir in set(output_dir for _, output_dir in scripts_to_run):
    os.makedirs(output_dir, exist_ok=True)

# Loop through the scripts and run them one by one
for script, output_dir in scripts_to_run:
    command = f"python {script}"
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    # Move or copy the generated files to the specified directory
    # for root, _, files in os.walk('.'):
    #     for file in files:
    #         if file.endswith(('.jpg', '.txt', '.json')):
    #             source_path = os.path.join(root, file)
    #             destination_path = os.path.join(output_dir, file)
    #             shutil.move(source_path, destination_path)