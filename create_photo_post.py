#!/usr/bin/python3

'''

NOTES:
A full-width photo looks like this:
{% include post_image_full.html
   filename="20190303-135103-topanga-state-park-KXL00543.jpg"
   title="Topanga State Park"
   caption="" %}

A text-width photo looks like this:
{% include post_image_caption.html
   filename="CA-DMV-replacement-plates.png"
   title=""
   caption="Source: https://www.dmv.ca.gov/portal/dmv/detail/vr/checklists/dup_sub " %}
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



def create_local_file(args):
  # create the local post file
  TODO()


def create_post(args):
  # create the post!

  # 1. preprocess the images
  #    for example, resize them
  TODO('preprocess images')

  # 2. upload the images to the server
  #     1. ssh in
  #     2. make a new directory in the appropriate spot
  #     3. scp the images
  TODO('upload images')
  
  # 3. create the new post, complete with the images
  create_local_file(args)


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
