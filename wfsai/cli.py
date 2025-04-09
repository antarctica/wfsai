#!/usr/bin/env python

# File Version: 2025-01-14: First version
#
# Author: matsco@bas.ac.uk

import argparse
import os
from wfsai import __version__
from wfsai import configuration

__DESCRIPTION__ = "Command Line interface for Wildlife from Space AI tools"


def _retrieve_remote():
    try:
        repo = os.environ['REMOTE_CONFIG_REPO']
    except KeyError:
        print("REMOTE_CONFIG_REPO environment variable not found")
        exit(1)
    try:
        conf = os.environ['CONFIG_FILE']
    except KeyError:
        print("CONFIG_FILE environment variable not found")
        exit(1)
    
    configuration.retrieve_gitlab(str(repo), str(conf))
 
def main():
    """
    cli entry point
    """
    
    parser = argparse.ArgumentParser(description=__DESCRIPTION__)
    parser.add_argument('-v', '--version', help="show this package version and exit",
                        action='version', version=__version__)
    parser.add_argument("-d", "--display", help="display configuration",
                        action="store", dest='display', default=None)
    parser.add_argument("--remote_config", help="retrieve the remote configuration file",
                        action="store_true", dest='remote_conf', default=False)
    args = parser.parse_args()


    # Now kick off main

    if args.remote_conf:
        _retrieve_remote()

    if args.display is not None:
        configuration.display(str(args.display))


if __name__ == "__main__":
    main()
