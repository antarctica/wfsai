#!/usr/bin/env python

# File Version: 2025-01-16: First version
#               2025-09-26: Added argument retreival
#
# Author: matsco@bas.ac.uk

import sys
import os
import shutil
import yaml
import git
from pathlib import Path
from typing import Union
from wfsai.setup_logging import logger

# Base reusable methods
def _check_path_(file_path: Union[str, Path]) -> bool:
    """
    Check that the file of a path exists and that it
    is not a directory.
    """
    return Path(file_path).exists() and not \
           Path(file_path).is_dir()


def _check_config_path_(config_file_path: Union[str, Path]) -> bool:
    """
    Check that the config file path points to a file that exists and
    that the format is yaml.
    This method returns a boolean True if the path is valid,
    otherwise False.
    """
    return _check_path_(Path(config_file_path)) and \
           Path(config_file_path).suffix == '.yaml'

def _load_(config_file_path: str) -> Union[str, None]:
    """
    Load workflow configuration from the supplied configuration yaml.
    This method returns the loaded yaml content if successful, 
    otherwise returning None.
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
        return None

def retrieve_gitlab(gitlab_repository_url: str, 
                    config_file_name: str) -> Union[Path, None]:
    """
    Retrieve a single configuration file from a gitlab repository.
    This method expects the gitlab repository to have a directory 
    named 'config' containing the requested configuration file.

    The configuration file is retrieved and placed in the 
    current working directory.

    This method returns the Path to the downloaded configuration 
    file, or None if not successful.  

    **Params:**  
     - gitlab_repository_url **`str`**  
     - config_file_name **`str`**  
    **Returns:** path to retrieved config **`Path`** or *None*  
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


def setup_datastores(directory_path: str, config_file: str) -> None:
    """
    Set up the datastores using the provided root directory and
    yaml config file.
    This method always returns None.  

    **Params:**  
     - directory_path **`str`**  
     - config_file **`str`**  
    **Returns:** *None*  
    """
    yaml_path = Path.joinpath(Path(str(directory_path)), str(config_file))

    if _check_config_path_(yaml_path):
        data_yaml = _load_(yaml_path)['datastores']

        for e in data_yaml:
            if e['local_dir'] is not None:
                if e['remote_dir'] is not None:
                    if e['symbolic']:
                        if not os.path.islink(Path.joinpath(Path(str(directory_path)), e['local_dir'])):
                            os.symlink(e['remote_dir'], Path.joinpath(Path(str(directory_path)), e['local_dir']))
                else:
                    os.makedirs(Path.joinpath(Path(str(directory_path)), e['local_dir']), exist_ok = True)
    
    return None


def display(config_file_path: str) -> None:
    """
    Display a summary of the supplied config file.
    This method prints to sys.stdout and returns None.

    **Params:** config_file_path **`str`**  
    **Returns:** *None*  
    """
    display_out = _load_(config_file_path)
    if display_out is not None:
        yaml.dump(display_out, sys.stdout)
    else:
        print(".yaml config file has no content")
    
    return None


def populate_env_variables(argument_dict: dict) -> None:
    '''
    Clears any pre-existing environment variable of the same
    name, then populates it from the provided argument_dict.
    Returns None.  

    **Params:** argument_dict **`dict`**  
    **Returns:** *None*  
    '''
    for name in argument_dict.keys():
        value = argument_dict[name]
        try:
            _ = os.environ[str(name)]
            os.environ.pop(name)
            os.environ[str(name)] = str(value).strip('"')
        except KeyError:
            os.environ[str(name)] = str(value).strip('"')
        logger.info(f"configuration:arguments:export env variable: {name}={value}")

    return None


def get_arguments(yaml_config_file: Union[str, Path]) -> Union[dict, None]:
    """
    Gets global pipeline arguments as defined in the pipeline's
    'config.yaml' under section `pipeline_arguments`. Where no 
    arguments are defined, returns None.

    All pipeline_arguments defined are returned as a key:value 
    dictionary. All arguments which have 
    `export_environment_variable: true` will also export
    that argument into the environment.  

    **Params:** yaml_config_file **`str`** or **`Path`**  
    **Returns:** retrieved arguments **`dict`** or *None*  
    """
    yaml_path = Path(yaml_config_file)

    ret_dictionary = {}
    env_dictionary = {}

    if _check_config_path_(yaml_path):
        data_yaml = _load_(yaml_path)
        if 'pipeline_arguments' in data_yaml.keys():
            args_yaml = _load_(yaml_path)['pipeline_arguments']
            if 'arguments' in args_yaml.keys():
                args_list = args_yaml['arguments']
                if type(args_list) != type(list()):
                    args_list = [args_list, ]

                for each_arg in args_list:
                    if 'arg_name' in each_arg.keys() and \
                            'arg_value' in each_arg.keys():
                        ret_dictionary[each_arg['arg_name']] = each_arg['arg_value']
                        if 'export_environment_variable' in each_arg.keys():
                            if each_arg['export_environment_variable'] == True:
                                env_dictionary[each_arg['arg_name']] = each_arg['arg_value']
                
                #logger.info(f"configuration:arguments: {ret_dictionary}")
                if len(env_dictionary) > 0:
                    populate_env_variables(env_dictionary)

    return None if len(ret_dictionary) == 0 else ret_dictionary

