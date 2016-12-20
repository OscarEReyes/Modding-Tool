from PyQt4 import QtCore


class parseThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
    def __del__(self):
        self.wait()


    def open_file(self):
        self.emit(QtCore.SIGNAL('parse()'))

    def run(self):
        self.open_file()
        self.terminate()

class scanThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
    def __del__(self):
        self.wait()

    def parse(self):
        self.emit(QtCore.SIGNAL('scan()'))

    def run(self):
        self.parse()

class setFieldsThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
    def __del__(self):
        self.wait()

    def set_main_fields(self):
        self.emit(QtCore.SIGNAL('set_fields()'))


    def run(self):
        self.set_main_fields()
        self.terminate()




