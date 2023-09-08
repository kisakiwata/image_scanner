import os
from flask import Flask, render_template, request, redirect, url_for
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

# Amazon S3 Configuration
S3_BUCKET = "kiwi-cropped-image"
S3_REGION = "us-west-1"

# File to store URLs
URLS_FILE = r"/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/result_urls/uploaded_urls.txt"

def save_url_to_file(url):
    with open(URLS_FILE, "a") as file:
        file.write(url + "\n")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if a file was uploaded
        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            return redirect(request.url)

        try:
            # Upload the file to Amazon S3
            s3 = boto3.client(
                "s3",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"), # set in .zshrc
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"), # set in .zshrc
                region_name=S3_REGION,
            )
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                file.filename,
                ExtraArgs={"ACL": "public-read"},
            )

            url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"

            # Save the URL to the text file
            save_url_to_file(url)

            return render_template("index.html", url=url)

        except NoCredentialsError:
            return "AWS credentials not available."

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)