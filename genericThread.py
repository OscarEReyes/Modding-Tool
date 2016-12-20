from PyQt4 import QtCore


class WorkThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)


    def __del__(self):
        self.wait()

    def create_mod(self):
        self.emit(QtCore.SIGNAL('create_mod()'))

    def run(self):
        self.create_mod()

