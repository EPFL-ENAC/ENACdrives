#!/usr/bin/env python3

# Bancal Samuel

# Mount_Filers : Main Python File

from gui import main_GUI
from cli import main_CLI
from utility import Output

if __name__ == '__main__':
    with Output():
        main_CLI()
        main_GUI()
