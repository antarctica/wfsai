#!/usr/bin/env python

# File Version: 2025-01-16: First version
#
# Author: matsco@bas.ac.uk

import sys
import yaml
import pathlib

def _check_config_path_(config_file_path):
    """
    Check that the config file path points to a file that exists and
    that the format is yaml
    """
    return pathlib.Path(config_file_path).exists() and not \
           pathlib.Path(config_file_path).is_dir() and \
           pathlib.Path(config_file_path).suffix == '.yaml'

 
def load(config_file_path):
    """
    Load workflow configuration from the supplied configuration yaml
    """
    try:
        if _check_config_path_(config_file_path):
            with open(config_file_path, 'r') as file:
                content_yaml = yaml.safe_load(file)
                return content_yaml
        else:
            print("Cannot read supplied path, .yaml file must exist")
            return None
    except Exception as e:
        print(e.message, e.args)


def display(config_file_path):
    """
    Display a summary of the supplied config file path
    """
    display_out = load(config_file_path)
    if display_out is not None:
        yaml.dump(display_out, sys.stdout)
    else:
        print(".yaml config file has no content")



# for the config.get() method we can do something like this:
# git archive --remote=git@gitlab.data.bas.ac.uk:digital-innovation-team/darwin-elephant-seal.git HEAD:configs/ test.yaml | tar -x
# which will get the single config file from the GitLab repo provided the user 
