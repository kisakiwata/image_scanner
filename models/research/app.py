import os
#from flask import Flask, render_template, request, redirect, url_for
import boto3
#from botocore.exceptions import NoCredentialsError
import datetime

#app = Flask(__name__)

# Amazon S3 Configuration
S3_BUCKET = "kiwi-cropped-image"
S3_REGION = "us-west-1"

# Directory to retrieve images
dirname = os.path.dirname(__file__)
UPLOAD_DIRECTORY = os.path.join(dirname, 'outputs')
# Directory to store URLs
URLS_DIRECTORY = os.path.join(dirname,'result_urls')

def save_url_to_file(url):
    with open(URLS_FILE, "a") as file:
        file.write(url + "\n")

def main():
    uploaded_count = 0

    # Upload the file to Amazon S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"), # set in .zshrc
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"), # set in .zshrc
        region_name=S3_REGION,
    )

    for filename in os.listdir(UPLOAD_DIRECTORY):
        if filename.endswith(".jpg"):  # You can specify the file extension you want to upload
            file_path = os.path.join(UPLOAD_DIRECTORY, filename)
            with open(file_path, "rb") as file:
                s3.upload_fileobj(
                    file,
                    S3_BUCKET,
                    os.path.join("images", filename),  # Object key in S3, adjust as needed
                    ExtraArgs={"ACL": "public-read"},
                )

                url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/images/{filename}"

                # Save the URL to the text file
                print(url)
                save_url_to_file(url)

                uploaded_count += 1
    
    # Check if all files have been uploaded - add assert logic 

    return f"{uploaded_count} files  uploaded successfully."

        # except NoCredentialsError:
        #     return "AWS credentials not available."

if __name__ == "__main__":
    # Count the total number of files in the directory
    total_files = len([filename for filename in os.listdir(UPLOAD_DIRECTORY) if filename.endswith(".jpg")])

    date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    URLS_FILE = os.path.join(URLS_DIRECTORY, "uploaded_urls_{}.txt".format(date))

    main()