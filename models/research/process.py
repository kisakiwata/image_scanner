import subprocess

# List of scripts to run in order
scripts_to_run = [
    "models/research/inference.py",
    "models/research/app.py",
    "models/research/image_search.py",
    "models/research/web_scraping.py"
]

# Loop through the scripts and run them one by one
for script in scripts_to_run:
    command = f"python {script}"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}: {e}")