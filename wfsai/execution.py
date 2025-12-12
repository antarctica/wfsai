#!/usr/bin/env python

# File Version: 2025-08-05: First version
#
# Author: 155652843+matscorse@users.noreply.github.com

import yaml
from pathlib import Path
from typing import Union

from wfsai.configuration import _check_config_path_
from wfsai.configuration import _load_
from wfsai.setup_logging import logger


def pipeline_element_enabled(element_name: str, config_yaml_path: Union[Path, str]) -> bool:
    """
    Checks the provided config_yaml to see if the specified element name is
    enabled or disabled.  

    Returns False if enabled == false in the config.
    Returns True otherwise.  

    **Params:**  
     - element_name **`str`**  
     - config_yaml_path **`Path`** or **`str`**    
    **Returns:** **`bool`**    
    
    ---  
    
    """
    return_value = True

    if type(element_name) != type(""):
        logger.error("element_name is NOT of type str!")
        return return_value
    
    if type(config_yaml_path) not in [Path, str]:
        logger.error("config_yaml_path is NOT of type Path or str!")
        return return_value
    
    if not _check_config_path_(config_yaml_path):
        logger.error("config_yaml_path INVALID!")
        return return_value
    else:
        yaml_content = _load_(config_yaml_path)
        if 'pipeline_elements' in yaml_content:
            elements_config = yaml_content['pipeline_elements']
            if 'elements' in elements_config.keys():
                elements = elements_config['elements']
                for element in elements:
                    if 'script' in element.keys() and 'enabled' in element.keys():
                        if element_name == element['script']:
                            if element['enabled'] == False:
                                return_value = False
                                break
    
    return return_value
