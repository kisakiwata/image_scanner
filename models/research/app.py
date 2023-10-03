import os
import boto3
import datetime
import re
import uuid

# Amazon S3 Configuration
S3_BUCKET = "kiwi-cropped-image"
S3_REGION = "us-west-1"

# Directory to retrieve images
dirname = os.path.dirname(__file__)
#UPLOAD_DIRECTORY = os.path.join(dirname, 'inference_output')
image_folder = os.path.join(dirname, 'images')
output_folder = os.path.join(dirname,'inference_output')
# Directory to store URLs
URLS_DIRECTORY = os.path.join(dirname,'result_urls')

def get_recent_tile_images(image_folder, output_folder):
    # Get the most recent image file from the 'image' folder
    image_extensions = ('.jpg', '.jpeg', '.png')
    image_files = [f for f in os.listdir(image_folder) if f.endswith(image_extensions)]
    if not image_files:
        return []  # No image files found in 'image' folder

    most_recent_image = max(image_files, key=lambda x: os.path.getctime(os.path.join(image_folder, x)))

    # Extract the tile pattern from the most recent image file name
    tile_info = re.search(r'([^/]+)\.(jpg|jpeg|png)', most_recent_image)
    if tile_info:
        tile_pattern = tile_info.group(1)
    else:
        return []  # Couldn't extract tile information from the image file name

    # Get the JPEG images from 'inference_output' folder with matching tile patterns
    matching_images = []
    for file_name in os.listdir(output_folder):
        if file_name.endswith('.jpg') and tile_pattern in file_name:
            matching_images.append(os.path.join(output_folder, file_name))

    return matching_images

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
    matching_images = get_recent_tile_images(image_folder, output_folder)
    # for filename in os.listdir(UPLOAD_DIRECTORY):
    #     if filename.endswith(".jpg"):  # You can specify the file extension you want to upload
    #         file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    
    for file_path in matching_images:
        # Extract the original filename from the file path
        original_filename = os.path.basename(file_path)

        # Generate a unique identifier (UUID)
        unique_id = str(uuid.uuid4())

        # Create a new unique filename by appending the UUID to the original filename
        unique_filename = f"{unique_id}_{original_filename}"

        with open(file_path, "rb") as file:
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                os.path.join("images", unique_filename),  # Object key in S3, adjust as needed
                ExtraArgs={"ACL": "public-read"},
            )

            url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/images/{unique_filename}"

            # Save the URL to the text file
            print(url)
            save_url_to_file(url)

            uploaded_count += 1
    
    # Check if all files have been uploaded - add assert logic 

    return f"{uploaded_count} files  uploaded successfully."

        # except NoCredentialsError:
        #     return "AWS credentials not available."

if __name__ == "__main__":

    date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    URLS_FILE = os.path.join(URLS_DIRECTORY, "uploaded_urls_{}.txt".format(date))

    main()