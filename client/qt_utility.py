from PyQt4 import QtCore


class NonBlockingProcessException(Exception):
    pass


class NonBlockingProcess(QtCore.QProcess):
    def __init__(self, name, finish_callback):
        super(NonBlockingProcess, self).__init__()
        NonBlockingProcess.register_process_name(name)
        self.name = name
        self.finish_callback = finish_callback
        
    def run(self, cmd):
        self.finished.connect(self._proc_finished)
        self.start(" ".join(cmd), QtCore.QIODevice.ReadOnly)

    def _proc_finished(self, exit_code, exit_status):
        NonBlockingProcess.unregister_process_name(self.name)
        if exit_status != 0 or exit_code != 0:
            self.finish_callback(self.name, False)
        else:
            self.finish_callback(self.name, True)
            
    @classmethod
    def register_process_name(cls, name):
        while True:
            try:
                if name in cls.process_names:
                    raise NonBlockingProcessException("Process named '{}' is already running.".format(name))
                cls.process_names.add(name)
                return
            except AttributeError:
                cls.process_names = set()

    @classmethod
    def unregister_process_name(cls, name):
        try:
            cls.process_names.remove(name)
        except AttributeError:
            cls.process_names = set()
        except KeyError:
            pass
