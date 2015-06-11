#!/usr/bin/env python3

# Bancal Samuel

# ENACdrives : Main Python File
# used for MacOSX

import argparse
from gui import main_GUI
from utility import CONST, Output


if __name__ == '__main__':
    if CONST.OS_SYS == "Linux":
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose",
                            action="count", default=0,
                            help="increase verbosity level")
        args = parser.parse_args()
        if args.verbose == 0:
            output_level = "normal"
        elif args.verbose == 1:
            output_level = "verbose"
        else:
            output_level = "debug"
    else:
        output_level = "debug"
    with Output(level = output_level):
        main_GUI()
