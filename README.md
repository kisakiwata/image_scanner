# Use Case of AI Computer Vision to detect product information for grocery deliveries
This repo showcases the use case of object detection technology to identify products (crop pictures) and detect product information using Google Lens APIs.
On top of that logic, I added additional grocery retail APIs (Walmart, Target, and Kroger) to detect the most accurate and helpful information for grocery delivery shoppers.
This flow was built as a POC to identify alternative products from pictures for customers will be a better communication method for shoppers when the requested items are out of stock.
The interface is enabled with Streamlit. You can see the streamlet io-hosted website [here](https://demo-image-scan.streamlit.app/)

Please see below for the flow:
## 1. Upload images
  - Upload images to detect products. In the repo, the images are stored in ```models/research/images```
    (image type has to be jpeg/jpg/png)

## 2. Inference: Detect objects inside pictures
  - Object Detection *(efficientdet) was used to identify objects inside a picture and crop bounding boxes surrounding each object.
  - You can tune the confidence threshold to modify the accuracy of the model, depending on the needs of the use case.
  - Sample pictures;
![hope-hummus1](https://github.com/kisakiwata/image_scanner/assets/46466783/63a62ece-69db-4eb0-abee-ac8d6eb5741d)
![sample1](https://github.com/kisakiwata/image_scanner/assets/46466783/31eb1d01-9b59-454d-9438-478c29a3b41c)

* see details on efficient det model [here](https://github.com/google/automl/tree/master/efficientdet)

  
## 3. Create URLs for each cropped image
  - The reason this is necessary is that Google Lens API (via Serp APIs) only allows to uploading urls as opposed to actual images.
  - I resolved this issue by storing each image in AWS S3. Please configure your own credentials in your environment.
    
## 4. Identify and collect product information
  - Collect information from Google Lens results (1 - 5 product results are collected.)
  - Upload these results into Walmart, Kroger, and Target APIs to gain further details with specific geolocation (e.g. prices, sizes)
    
## 5. Finally, put that information into a data frame accessible to users
  - With the help of Streamlist, I display the detected results as a data frame. ```streamlit run models/research/scan.py```
  - You can see the results here as well: (https://image-scanner-demo.streamlit.app/)
  - Feel free to play around with the Streamlit io and let me know your feedback!
  - As the app is not interactive because of the repo retrieval, you can also refer to this demo video [here](https://www.loom.com/share/8e80bad453f341399f0837dd8e88cc62?sid=66043d0d-389c-43ac-9f75-d86af1dcca76)
