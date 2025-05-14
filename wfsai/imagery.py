#!/usr/bin/env python

# File Version: 2025-05-14: First version
#
# Author: matsco@bas.ac.uk

import sys
import os
import shutil
import yaml
import glob
from pathlib import Path
from wfsai.configuration import _check_config_path_
from wfsai.configuration import _load_

"""
This library is for handling imagery for pre or post AI tasks.
"""

class maxar:

    """
    This class is specifically for operations when handling Maxar satellite imagery.
    """

    def __init__():
        pass

    def basic_test(test_string: str) -> str:
        ret_string = "The test string provided was: '"+test_string+"'"
        return ret_string

    #TODO What do I want the maxar data handling to actually do?
    # 1. Take in a single satellite image and ortho-rectify.
    # 2. Take in both PAN and MUL ortho-rectified images and output
    #    a pan sharpened image.
    