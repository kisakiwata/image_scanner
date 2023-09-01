import numpy as np
import os
import sys
import tarfile
import tensorflow as tf
import pathlib
import argparse

from collections import defaultdict
from io import StringIO
import cv2
from PIL import Image
from IPython.display import display

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
#from object_detection.utils import visualization_utils as vis_util

# patch tf1 into `utils.ops`
utils_ops.tf = tf.compat.v1

# Patch the location of gfile
tf.gfile = tf.io.gfile

PATH_TO_LABELS = r'/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/object_detection/data/mscoco_label_map.pbtxt'
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

# Model Preparation

def load_model(model_name):
  ## URL updated
  base_url = 'http://download.tensorflow.org/models/object_detection/tf2/20200711/'
  model_file = model_name + '.tar.gz'
  model_dir = tf.keras.utils.get_file(
    fname=model_name,
    origin=base_url + model_file,
    untar=True)

  model_dir = pathlib.Path(model_dir)/"saved_model"

  model = tf.saved_model.load(str(model_dir))

  return model

def run_inference_for_single_image(model, image):
  image = np.asarray(image)
  # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
  input_tensor = tf.convert_to_tensor(image)
  # The model expects a batch of images, so add an axis with `tf.newaxis`.
  input_tensor = input_tensor[tf.newaxis,...]

  # Run inference
  model_fn = model.signatures['serving_default']
  output_dict = model_fn(input_tensor)

  # All outputs are batches tensors.
  # Convert to numpy arrays, and take index [0] to remove the batch dimension.
  # We're only interested in the first num_detections.
  num_detections = int(output_dict.pop('num_detections'))
  output_dict = {key:value[0, :num_detections].numpy()
                 for key,value in output_dict.items()}
  output_dict['num_detections'] = num_detections

  # detection_classes should be ints.
  output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

  # Handle models with masks:
  if 'detection_masks' in output_dict:
    # Reframe the the bbox mask to the image size.
    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
              output_dict['detection_masks'], output_dict['detection_boxes'],
               image.shape[0], image.shape[1])
    detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
                                       tf.uint8)
    output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()

  return output_dict

def show_inference(model, image_path, dir=r'/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/outputs'):
  image_np = np.array(Image.open(image_path))
  output_dict = run_inference_for_single_image(model, image_np)
  
  filename = os.path.basename(image_path).split(".")[0]
  image = cv2.imread(str(image_path))
  image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  (frame_height, frame_width) = image.shape[:2]
  tensor_img= tf.convert_to_tensor(image_np, dtype=tf.float32)

  display_str = []
  boxes = output_dict['detection_boxes']
  scores = output_dict['detection_scores']
  classes = output_dict['detection_classes']
  for i in range(len(boxes)): #min(max_boxes_to_draw, boxes.shape[0])
      if (scores[i] > .4) & (boxes[i] is not None):
          display_str.append(boxes[i])
          
          if boxes[i] is not None:
          # crop bb boxes
            ymin = int((np.squeeze(boxes)[i][0]*frame_height))
            xmin = int((np.squeeze(boxes)[i][1]*frame_width))
            ymax = int((np.squeeze(boxes)[i][2]*frame_height))
            xmax = int((np.squeeze(boxes)[i][3]*frame_width))
            cropped_img = tf.image.crop_to_bounding_box(tensor_img, ymin, xmin, ymax - ymin, xmax - xmin)

            img_name = r"{}/{}_imag{}.jpg".format(dir, filename, i)

            final_img = cv2.resize(np.array(cropped_img), (800, 600), interpolation = cv2.INTER_CUBIC)
            im_bgr = cv2.cvtColor(final_img, cv2.COLOR_RGB2BGR)

            if not cv2.imwrite(img_name, im_bgr):
              raise Exception("Could not write image")

          else:
            pass
  #print(display_str)

  # display(Image.fromarray(image_np))


# put these in args
model_name = 'efficientdet_d0_coco17_tpu-32'
detection_model = load_model(model_name)

PATH_TO_TEST_IMAGES_DIR = pathlib.Path(r'/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/object_detection/test_images')
types = ('*.jpg', '*.jpeg', '*.png')
files_grabbed = []
for files in types:
    files_grabbed.extend(PATH_TO_TEST_IMAGES_DIR.glob(files))
TEST_IMAGE_PATHS = sorted(files_grabbed)

def main(detection_model = detection_model, TEST_IMAGE_PATHS = TEST_IMAGE_PATHS):
  for image_path in TEST_IMAGE_PATHS:
    show_inference(detection_model, image_path)

if __name__ == '__main__':
  main()
  
# save bounding box result as json file?



# result = run_inference(TEST_IMAGE_PATHS, model=detection_model)
# save_results(result)

# download images to filepath (TEST_IMAGE_PATHS) or directly grabbing from dropbox URL?
# after the inference, upload cropped images with AWS EC2 (?) + FAST API 
# convert to base64

# use serpa API to upload images to google API
# use scrapeAI to scrape the first match from google API result (image search)
# use beautiful soup to scrape price, prodcut name, and brannd

# try this UI with streamlit

