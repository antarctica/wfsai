#!/usr/bin/env python

# Version: 2025-01-14: First version
#
# Author: matsco@bas.ac.uk

import argparse

__DESCRIPTION__ = "Command Line interface for Wildlife from Space AI package"

 
def main():
    """
    cli entry point
    """
    
    parser = argparse.ArgumentParser(description=__DESCRIPTION__)
    args = parser.parse_args()


    # Now kick off main


if __name__ == "__main__":
    main()
