#!/usr/bin/env python

# File Version: 2025-01-14: First version
#
# Author: matsco@bas.ac.uk

import argparse
from wfsai import __version__
from wfsai import config

__DESCRIPTION__ = "Command Line interface for Wildlife from Space AI tools"

 
def main():
    """
    cli entry point
    """
    
    parser = argparse.ArgumentParser(description=__DESCRIPTION__)
    parser.add_argument('-v', '--version', help="show this package version and exit",
                        action='version', version=__version__)
    parser.add_argument("-d", "--display", help="display configuration",
                        action="store", dest='display', default=None)
    args = parser.parse_args()


    # Now kick off main
    if args.display is not None:
        config.display(str(args.display))


if __name__ == "__main__":
    main()
