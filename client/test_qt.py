from PyQt4 import QtGui
from PyQt4 import QtCore
import sys


class MyQProcess(QtCore.QProcess):     
    def __init__(self):    
        # Call base class method 
        QtCore.QProcess.__init__(self)
        # Create an instance variable here (of type QTextEdit)
        self.edit = QtGui.QTextEdit()
        self.edit.setWindowTitle("QTextEdit Standard Output Redirection")
        self.edit.show()   
   
    # Define Slot Here 
    @QtCore.pyqtSlot()
    def readStdOutput(self):
        self.edit.append(bytes(self.readAllStandardOutput()).decode("utf-8", "replace"))
    
    @QtCore.pyqtSlot()
    def _started(self):
        self.edit.append("Started")
        return True
    
    @QtCore.pyqtSlot(int, QtCore.QProcess.ExitStatus)
    def _finished(self, exit_code, exit_status):
        self.edit.append("Finished")
    
    @QtCore.pyqtSlot(QtCore.QProcess.ProcessError)
    def _error(self, err):
        self.edit.append("Error")
    
    @QtCore.pyqtSlot(QtCore.QProcess.ProcessState)
    def _stateChanged(self, p):
        self.edit.append("stateChanged")
    

def main():  
    app = QtWidgets.QApplication(sys.argv)
    qProcess = MyQProcess()
    
    qProcess.setProcessChannelMode(QtCore.QProcess.MergedChannels)    
    QtCore.QObject.connect(qProcess, QtCore.SIGNAL("readyReadStandardOutput()"), qProcess, QtCore.SLOT("readStdOutput()"))
    QtCore.QObject.connect(qProcess, QtCore.SIGNAL("started()"), qProcess, QtCore.SLOT("_started()"))
    QtCore.QObject.connect(qProcess, QtCore.SIGNAL("finished()"), qProcess, QtCore.SLOT("_finished(int, QtCore.QProcess.ExitStatus)"))
    QtCore.QObject.connect(qProcess, QtCore.SIGNAL("error()"), qProcess, QtCore.SLOT("_error(QtCore.QProcess.ProcessError)"))
    QtCore.QObject.connect(qProcess, QtCore.SIGNAL("stateChanged()"), qProcess, QtCore.SLOT("_stateChanged(QtCore.QProcess.ProcessState)"))
    # qProcess.start("ldconfig -v")    
    qProcess.start("wmic logicaldisk")
    
    return app.exec_()
    
if __name__ == '__main__':
    main()
    
