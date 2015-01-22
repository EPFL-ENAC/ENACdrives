#!/usr/bin/env python3

# Bancal Samuel

import sys
from PyQt5 import QtWidgets
 
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    button = QtWidgets.QPushButton("Hello, PyQt!")
    window.setCentralWidget(button)
    window.show()
    app.exec_()
 
if __name__ == '__main__':
    main()

