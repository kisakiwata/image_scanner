#import pip

#pip.main(['install', 'protobuf==3.19.0'])

import numpy as np
import os
import sys
import tarfile
import tensorflow as tf
import pathlib
import argparse
import datetime

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

def show_inference(model, image_path, dir):
  image_np = np.array(Image.open(image_path))
  output_dict = run_inference_for_single_image(model, image_np)
  
  filename = os.path.basename(image_path).split(".")[0]
  image = cv2.imread(str(image_path))
  image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  if image is not None:
    print(True)
  (frame_height, frame_width) = image.shape[:2]
  tensor_img= tf.convert_to_tensor(image_np, dtype=tf.float32)
  if tensor_img is not None:
    print(True)

  display_str = []
  boxes = output_dict['detection_boxes']
  scores = output_dict['detection_scores']
  classes = output_dict['detection_classes']
  for i in range(len(boxes)): #min(max_boxes_to_draw, boxes.shape[0])
      if (scores[i] > .2) & (boxes[i] is not None):
          display_str.append(boxes[i])
          
          if boxes[i] is not None:
          # crop bb boxes
            ymin = int((np.squeeze(boxes)[i][0]*frame_height))
            xmin = int((np.squeeze(boxes)[i][1]*frame_width))
            ymax = int((np.squeeze(boxes)[i][2]*frame_height))
            xmax = int((np.squeeze(boxes)[i][3]*frame_width))
            cropped_img = tf.image.crop_to_bounding_box(tensor_img, ymin, xmin, ymax - ymin, xmax - xmin)

            img_name = r"{}/{}_imag{}.jpg".format(dir, filename, i)
            print(img_name)
            final_img = cv2.resize(np.array(cropped_img), (800, 600), interpolation = cv2.INTER_CUBIC)
            print(final_img)
            im_bgr = cv2.cvtColor(final_img, cv2.COLOR_RGB2BGR)

            if not cv2.imwrite(img_name, im_bgr):
              raise Exception("Could not write image")

          else:
            pass
  #print(display_str)

  # display(Image.fromarray(image_np))

def find_most_recent_files(image_folder):
    all_files = [os.path.join(image_folder, filename) for filename in os.listdir(image_folder)]
    
    if not all_files:
        return []  # No files found in the directory

    # Get the maximum timestamp among all files
    max_timestamp = max(os.path.getctime(file_path) for file_path in all_files)

    # Find all files with the maximum timestamp
    most_recent_files = [file_path for file_path in all_files if os.path.getctime(file_path) == max_timestamp]

    return most_recent_files


# put these in args
model_name = 'efficientdet_d0_coco17_tpu-32'
detection_model = load_model(model_name)


dirname = os.path.dirname(__file__)
image_directory = os.path.join(dirname,'images')

# PATH_TO_TEST_IMAGES_DIR = pathlib.Path(image_directory)#r'/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/object_detection/test_images
# types = ('*.jpg', '*.jpeg', '*.png')
# files_grabbed = []
# for files in types:
#     files_grabbed.extend(PATH_TO_TEST_IMAGES_DIR.glob(files))
# TEST_IMAGE_PATHS = sorted(files_grabbed)


#date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# save_dir_output = os.path.join(dirname,'inference_output', "output_{}".format(date))
# os.makedirs(save_dir_output, exist_ok=True)

if __name__ == '__main__':
  #def main(detection_model = detection_model, TEST_IMAGE_PATHS = TEST_IMAGE_PATHS):
  TEST_IMAGE_PATHS = find_most_recent_files(image_directory)

  if TEST_IMAGE_PATHS:
      print("Most recent files:")
      for file_path in TEST_IMAGE_PATHS:
          print(file_path)

# create output folder for each inference timing
# Define the directory where you want to save the JSON file
  save_directory = os.path.join(dirname,'inference_output')
  os.makedirs(save_directory, exist_ok=True)
  for image_path in TEST_IMAGE_PATHS:
    show_inference(detection_model, image_path, dir=save_directory)
  #main()
