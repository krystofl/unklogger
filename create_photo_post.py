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
import re # for title validation

# Krystof utils
KRYSTOF_UTILS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'krystof-utils', 'python')
sys.path.append(KRYSTOF_UTILS_PATH)
from krystof_utils import MSG, TODO


# path to the Klog repo on disk
KLOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'krystofl.github.io')

POST_TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'post_template.md')
IMAGE_FULL_TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'image_full_template.md')

# files with these extensions are considered images
IMAGE_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']



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
  TODO('replace photos dir path')


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
  for fn in os.listdir(args.photos):
    for ext in IMAGE_FILE_EXTENSIONS:
      if fn.endswith(ext):
        retd['photos'].append(fn)
        break

  # create the new folder on the server
  TODO('create folder on the server')

  # scp the photos
  TODO('scp the photos')

  MSG("retd: {}".format(retd))
  return retd



def create_post(args):
  # create the post!

  # 1. preprocess the images
  #    for example, resize them
  # TODO('preprocess images')

  # 2. upload the images to the server
  photos_dict = upload_images(args)

  # 3. create the new post, complete with the images
  create_local_file(args, photos_dict)



# returns true if title is a valid post title
# i.e. it contains only alphanumerics and dashes
def title_valid(title, search=re.compile(r'[^a-z0-9-]').search):
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
                      default = '',
                      help = 'Path to the folder on disk that contains ' \
                             'the images that should be included in the post')

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


  MSG("args: {}".format(args))

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
