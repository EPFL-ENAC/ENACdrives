#!/usr/bin/env python3

# Bancal Samuel

# ENACdrives : Main Python File
# used for Windows & Linux

import argparse
from cli import main_CLI
from gui import main_GUI
from utility import CONST, Output


if __name__ == '__main__':
    ui = "GUI"
    if CONST.OS_SYS == "Linux":
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-v", "--verbose",
            action="count", default=0,
            help="increase Verbosity level (max is -vvv)")
        parser.add_argument(
            "-s", "--summary",
            action="store_true",
            help="show Summary")
        parser.add_argument(
            "-u", "--umount",
            action="store_true",
            help="Umount instead of default mount")
        parser.add_argument(
            "-a", "--all",
            action="store_true",
            help="(u)mount All entries")
        parser.add_argument(
            "-n", "--named",
            action="append",
            help="(u)mount Named entries")
        parser.add_argument(
            "-b", "--bookmarked",
            action="store_true",
            help="(u)mount Bookmarked entries")
        parser.add_argument(
            "--add-bookmark",
            action="append",
            help="Add a bookmark")
        parser.add_argument(
            "--rm-bookmark",
            action="append",
            help="Remove a bookmark")
        args = parser.parse_args()
        
        if (args.summary or args.umount or args.all or args.named is not None or
           args.bookmarked or args.add_bookmark is not None or args.rm_bookmark is not None):
            ui = "CLI"
            args.verbose -= 1
        
        if args.verbose == -1:
            output_level = "cli"
        elif args.verbose == 0:
            output_level = "normal"
        elif args.verbose == 1:
            output_level = "verbose"
        else:
            output_level = "debug"
    else:
        output_level = "debug"
    with Output(level = output_level):
        if ui == "GUI":
            main_GUI()
        else:
            main_CLI(args)
