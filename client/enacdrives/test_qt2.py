import sys

from PyQt4 import QtGui, QtCore


def print_to_file(s):
    with open("Y:\\commun1\\ENACdrives\\src\\client\\build\\exe.win32-3.4\\output.log", "a") as f:
        f.write(s)

print_to_file("START")
proc = QtCore.QProcess()
proc.start("\"wmic\" logicaldisk")
# proc.start("ldconfig -v")
proc.waitForFinished()
result = proc.readAll()
print_to_file(bytes(result).decode("utf-8", "replace"))
proc.close()
print_to_file("FINISH")
