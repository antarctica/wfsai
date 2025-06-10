#!/usr/bin/env python

# File Version: 2025-04-11: First version
#
# Author: matsco@bas.ac.uk

import os
import shutil
import glob
from pathlib import Path
from wfsai.configuration import _check_config_path_
from wfsai.configuration import _load_


def retrieve(directory_path: str, config_file: str, data_type: str) -> None:
    """
    Retrieve a specific data type according to specifics in the
    yaml config file.
    The retrieved data will be stored in the location specified
    in the yaml config file.
    This method always returns None.
    """
    yaml_path = Path.joinpath(Path(str(directory_path)), str(config_file))

    if _check_config_path_(yaml_path):
        data_yaml = _load_(yaml_path)[str(data_type)]

        for dir_group in data_yaml:
            # Do specified source and destination directories exist
            if dir_group['source_dir'] is not None and dir_group['dest_dir'] is not None:
                if (not os.path.isdir(dir_group['source_dir'])) or (not os.path.isdir(dir_group['dest_dir'])):
                    print("Source or destination directory not found")
                    exit(1)

            # For each specified file, copy or link to destination
            for e in dir_group['sources']:
                # Check the source directory exists
                if os.path.isdir(Path.joinpath(Path(dir_group['source_dir']), e['dir'])):
                    src_directory = Path.joinpath(Path(dir_group['source_dir']), e['dir'])
                    for file in e['files']:
                        # Expand out any wildcards, i.e. *.*
                        for subfile in glob.glob(str(Path.joinpath(src_directory, file))):
                            # Make sure the source files each exist
                            if os.path.isfile(Path.joinpath(src_directory, os.path.basename(subfile))):
                                dest_directory = Path(dir_group['dest_dir'])
                                # Only copy if file isn't already in destination directory
                                if not os.path.isfile(Path.joinpath(dest_directory, os.path.basename(subfile))):
                                    shutil.copy(subfile, Path.joinpath(dest_directory, os.path.basename(subfile)))
    
    return None
