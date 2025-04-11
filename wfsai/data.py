#!/usr/bin/env python

# File Version: 2025-04-11: First version
#
# Author: matsco@bas.ac.uk

import sys
import os
import shutil
import yaml
import git
from pathlib import Path
from configuration import _check_config_path_
from configuration import _load_


def retrieve(directory_path: str, config_file: str, data_type: str) -> None:
    """
    Retrieve a specific data type according to specifics set out in the yaml config file.
    The retrieved data will be stored in the location specified in the yaml config file.
    This method always returns None.
    """
    yaml_path = Path.joinpath(Path(str(directory_path)), str(config_file))

    if _check_config_path_(yaml_path):
        data_yaml = load(yaml_path)[str(data_type)]

        for e in data_yaml:
            pass
    
    return None
