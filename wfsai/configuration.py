#!/usr/bin/env python

# File Version: 2025-01-16: First version
#
# Author: matsco@bas.ac.uk

import sys
import os
import shutil
import yaml
import git
from pathlib import Path

def _check_config_path_(config_file_path):
    """
    Check that the config file path points to a file that exists and
    that the format is yaml
    """
    return Path(config_file_path).exists() and not \
           Path(config_file_path).is_dir() and \
           Path(config_file_path).suffix == '.yaml'

def retrieve_gitlab(gitlab_repository_url: str, 
                    config_file_name: str) -> Path:
    """
    Retrieve a single configuration file from a gitlab repository.
    This method expects the gitlab repository to have a directory 
    named 'config' containing the requested configuration file.

    The configuration file is retrieved and placed in the 
    current working directory.

    This method returns the Path to the downloaded configuration 
    file, or None if not successful.
    """
    return_val = None
    rdir = 'configs'

    root_path = Path(os.getcwd())
    local_path = Path.joinpath(root_path, '.repo')
    if os.path.isdir(local_path):
        shutil.rmtree(local_path)

    # Clone the remote repository
    try:
        repo = git.Repo.clone_from(gitlab_repository_url, local_path)
        local_file = Path.joinpath(local_path, rdir, config_file_name)
        if os.path.isfile(local_file):
            shutil.move(local_file, Path.joinpath(root_path, config_file_name))
            return_val = Path.joinpath(root_path, config_file_name)
            shutil.rmtree(local_path)
    except Exception as e:
        print(e.message, e.args)

    return return_val

def load(config_file_path: str):
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

def setup_datastores(pipeline_directory_path: str, config_file: str):
    """
    Set up the datastores using the provided pipeline directory and yaml config file.
    """
    yaml_path = Path.joinpath(Path(str(pipeline_directory_path)), str(config_file))

    if os.path.isfile(yaml_path):
        with open(yaml_path) as yamlfile:
            data_yaml = yaml.safe_load(yamlfile)['datastores']

    for e in data_yaml:
        if e['local_dir'] is not None:
            if e['remote_dir'] is not None:
                if e['symbolic']:
                    if not os.path.islink(Path.joinpath(Path(str(pipeline_directory_path)), e['local_dir'])):
                        os.symlink(e['remote_dir'], Path.joinpath(Path(str(pipeline_directory_path)), e['local_dir']))
            else:
                os.makedirs(Path.joinpath(Path(str(pipeline_directory_path)), e['local_dir']), exist_ok = True)


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
