# Unklogger

Scripts and utils that make The Klog easier to work with


# Getting Started

Make a virtualenv & install prerequisites

    mkvirtualenv unklogger
    pip install -r requirements.txt

Initialize submodules:

    git submodule init && git submodule update


# Make a post with photos

Using the `photos` subdirectory (make it, copy photos there):

    ./create_photo_post.py MY_POST_NAME

For more options, run

    ./create_photo_post.py --help
