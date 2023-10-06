## Use Case of AI Computer Vision to detect product information for grocery deliveries
This repo showcases the use case of object detection technology to identify products (crop pictures) and detect product information using Google Lens APIs.
On top of that logic, I added additional grocery retail APIs (Walmart, Target, and Kroger) to detect the most accurate and helpful information for grocery delivery shoppers.
This flow was built as POC to identify alternative products from pictures for customers will be a better communication method for shoppers when the requested items are out of stock.
The interface is enabled with Streamlit. You can see the streamlit io-hosted website [here](https://demo-image-scan.streamlit.app/)

Please see below for the flow:
1. Detect objects inside pictures
  - Object Detection (efficientdet) was used to identify objects inside a picture and crop bounding boxes surrounding each object.
  - You can tune the confidence threshold to modify the accuracy of the model, depending on the needs of the use case.
3. 
4.
5.
6.
7.
8.
9.
10. Upload a picture , type your zipcode to find a nearest store and identify products
11. Streamlist
# 
