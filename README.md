# unklogger
Scripts and utils that make The Klog easier to work with

## Getting Started

Prerequisites

    sudo apt update
    sudo apt install python3-opencv

Initialize submodules:

    git submodule init && git submodule update

Make sure you have a server_config.json file that has all of the
following info:

    "user": "name of user on server where images will be hosted",
    "host": "name of the host",
    "path_to_post_img_root": "path to the folder where a new folder for images for this post should be created"

