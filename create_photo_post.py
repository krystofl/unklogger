#!/usr/bin/python3

'''
Create a new Klog post with photos
'''

import os
import sys
import argparse
import traceback
import datetime
import dateutil.parser
import json
import copy
import re # for title validation
import cv2 # for image resizing

# path to this file
UNKLOGGER_PATH = os.path.dirname(os.path.abspath(__file__))

# Krystof utils
KRYSTOF_UTILS_PATH = os.path.join(UNKLOGGER_PATH, 'krystof-utils', 'python')
sys.path.append(KRYSTOF_UTILS_PATH)
from krystof_utils import MSG, TODO


# path to the Klog repo on disk
KLOG_PATH = os.path.join(UNKLOGGER_PATH, 'krystofl.github.io')

POST_TEMPLATE = os.path.join(UNKLOGGER_PATH, 'post_template.md')
IMAGE_FULL_TEMPLATE = os.path.join(UNKLOGGER_PATH, 'image_full_template.md')

# files with these extensions are considered images
IMAGE_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']

# processed photos will be saved here
PROCESSED_IMG_DIR = os.path.join(UNKLOGGER_PATH, 'photos-processed')

# maximum width for the images
MAX_IMAGE_WIDTH_FULL = 900 # pixels

# json file containing server configuration
SERVER_CONFIG_FILE = 'server_config.json'


def get_image_filenames(folder_path):
  # get the filenames of all the images in folder folder_path
  # returns them as a list

  # also consider capitalized versions of all extensions
  all_extensions = copy.deepcopy(IMAGE_FILE_EXTENSIONS)
  all_extensions.extend([e.upper() for e in IMAGE_FILE_EXTENSIONS])

  fns = []
  for fn in os.listdir(folder_path):
    for ext in all_extensions:
      if fn.endswith(ext):
        fns.append(fn)
        break
  return fns



def process_images(args):
  '''
  Process / prepare photos for upload:
    1. resize, if appropriate

  saves the processed images to PROCESSED_IMG_DIR
  '''
  # make sure the folder for processed images exists
  try:
    os.makedirs(PROCESSED_IMG_DIR)
  except FileExistsError:
    pass

  # delete any files that were previously in PROCESSED_IMG_DIR
  try:
    for fn in os.listdir(PROCESSED_IMG_DIR):
      filepath = os.path.join(PROCESSED_IMG_DIR, fn)
      if os.path.isfile(filepath):
        os.unlink(filepath)
  except Exception as e:
    MSG("Exception while emptying PROCESSED_IMG_DIR: {}".format(e))

  MSG("Resizing the photos...")

  # get the image filenames
  fns = get_image_filenames(args.photos)

  for imgfn in fns:
    # open the image
    img = cv2.imread(os.path.join(args.photos, imgfn))
    #MSG("original dimensions of {}: {}".format(imgfn, img.shape))
    #MSG("width: {}".format(img.shape[1]))

    # this is where we'll save the file
    new_path = os.path.join(PROCESSED_IMG_DIR, imgfn)

    # if the image is smaller than the max width, just copy it
    orig_width = img.shape[1]
    if orig_width <= MAX_IMAGE_WIDTH_FULL:
      cv2.imwrite(new_path, img)

    # otherwise, resize it
    else:
      # scale factor
      neww   = MAX_IMAGE_WIDTH_FULL
      scalar = neww / orig_width
      newh   = int(img.shape[0] * scalar)
      #MSG("scalar: {}; new dims: {} x {}".format(scalar, neww, newh))

      # resize the image
      resized = cv2.resize(img, (neww, newh), interpolation = cv2.INTER_AREA)

      # save the new file
      cv2.imwrite(new_path, resized)



def create_local_file(args, photos_dict):
  # create the local post file
  # photos_dict is returned by upload_images() - see that function's def for spec

  # load the template
  with open(POST_TEMPLATE, 'r') as fp:
    post = fp.read()


  # replace the title
  post = post.replace('title: ""',
                      'title: {}'.format(args.title), 1)


  # replace the photos directory
  post = post.replace('photos_dir: ""',
                      'photos_dir: "{}"'.format(photos_dict['folder']))


  # add all the images
  with open(IMAGE_FULL_TEMPLATE, 'r') as fp:
    image_template = fp.read()

  for ifn in photos_dict['photos']:
    new_image = image_template.replace('filename=""',
                                       'filename="{}"'.format(ifn), 1)
    post = post + new_image



  # create the path of the newfile
  newfn   = '{}-{}.md'.format(args.date.strftime("%Y-%m-%d"),
                              args.title)
  newfile = os.path.join(KLOG_PATH, '_posts', newfn)
  #MSG("newfile: {}".format(newfile))

  # save the new file
  with open(newfile, 'w') as fp:
    fp.write(post)



def upload_images(args):
  '''
  Upload images to the server

  returns a dict like:
  {
    folder: name-of-folder-containing-the-photos,
    photos: ['1.jpg', 'two.jpg', 'third-filename.png']
  }
  '''

  # the dictionary we'll return
  retd = { 'folder': '', 'photos': [] }

  # get the image filenames
  retd['photos'] = get_image_filenames(PROCESSED_IMG_DIR)

  # get the name of the folder on the server where the photos will go
  retd['folder'] = '{}-{}'.format(args.date, args.title)

  # print out the commands the user needs to run to get stuff on the server
  try:
    # open the server config json file
    with open(SERVER_CONFIG_FILE, 'r') as f:
      server_config = json.load(f)
    #MSG("server_config: {}".format(server_config))

    # folder on server where the images will go
    server_folder_path = os.path.join(server_config['path_to_post_img_root'],
                                      retd['folder'])

    print("")
    MSG("I think you need to run the following commands " \
        "to get the photos on the server: ")
    print("ssh {}".format(server_config['host']))
    print("mkdir {}".format(os.path.join(server_folder_path)))
    print("<<< RUN THE BELOW BACK ON THE LOCAL MACHINE >>>")
    print("scp {}/* {}@{}:{}".format(PROCESSED_IMG_DIR,
                                     server_config['user'],
                                     server_config['host'],
                                     server_folder_path))
    print("")

  except Exception as e:
    MSG("Exception figuring out how to upload the images to the server: {}".format(e))

  #MSG("retd: {}".format(retd))
  return retd



def create_post(args):
  # create the post!

  # 1. preprocess the images
  #    for example, resize them
  process_images(args)

  # 2. upload the images to the server
  photos_dict = upload_images(args)

  # 3. create the new post, complete with the images
  create_local_file(args, photos_dict)



# returns true if title is a valid post title
# i.e. it contains only alphanumerics and dashes
def title_valid(title, search=re.compile(r'[^a-zA-Z0-9-]').search):
  return not bool(search(title))



def parse_command_line_args():
  # parse command line arguments

  parser = argparse.ArgumentParser(description = 'Create a new Klog post with photos')

  # date
  parser.add_argument('-d', '--date',
                      default = 'TODAY',
                      help = 'Date of the new post. Also accepts TODAY')

  # title
  # mandatory; make it by position rather than requiring the flag (how?)
  parser.add_argument('title',
                      help = 'Title of the new post')

  # path to image dir
  parser.add_argument('-p', '--photos',
                      default = 'photos',
                      help = 'Path to the folder on disk that contains ' \
                             'the images that should be included in the post. ' \
                             'Default: photos dir in the same directory as this script.')

  # full-width or text-width images?
  parser.add_argument('-n', '--narrow-images', action = 'store_true',
                      help = 'Make the images only as wide as the text, ' \
                             'rather than the width of the entire container.')

  args = parser.parse_args()


  # make sure the date is valid
  try:
    # catch the special case
    if args.date == 'TODAY':
      args.date = datetime.date.today()
      MSG("Setting date to today: {}".
          format(args.date.strftime("%Y-%m-%d")))

    else:
      # the normal case...
      args.date = dateutil.parser.parse(args.date)
      MSG("Setting date to {}".format(args.date.strftime("%Y-%m-%d")))

  except Exception as ex:
    MSG("Invalid date {} specified. Please specify the date of the post as " \
        "YYYY-MM-DD. Exiting.".format(args.date))
    MSG("Exception: {}".format(ex))
    sys.exit()


  # make sure the title is valid
  # how? what makes a valid title?
  try:
    if not title_valid(args.title):
      MSG("Invalid title {} specified. Titles can only contain alphanumerics and " \
          "dashes (hyphens). Exiting.".format(args.title))
      sys.exit()
  except Exception as ex:
    MSG("Exception while validating title: {}".format(ex))
    sys.exit()


  if args.narrow_images:
    MSG("NOTE: Sorry, but 'narrow images' aren't supported yet.")


  #MSG("args: {}".format(args))
  return args




if __name__ == '__main__':

  args = parse_command_line_args()

  try:
    create_post(args)
  except Exception as ex:
    MSG("Exception: {}".format(ex))

    # print more detailed info
    traceback.print_exc()
    print('')
