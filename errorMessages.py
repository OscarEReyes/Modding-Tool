from PyQt4 import QtGui
from PyQt4.QtGui import *

def errorWhileSaving(self):
	NFmesgBox = QtGui.QMessageBox.warning(self, 'Warning',"An error occur while saving. Please verify your feature", QtGui.QMessageBox.Ok)
def errorAddingFeature(self):
	NFmesgBox = QtGui.QMessageBox.warning(self, 'Warning',"An error occur while adding a feature", QtGui.QMessageBox.Ok)
def errorCreatingMod(self):
	NFmesgBox = QtGui.QMessageBox.warning(self, 'Error',"Please list a name for your new Mod", QtGui.QMessageBox.Ok)
def showSaveError(self):
	NFmesgBox = QtGui.QMessageBox.warning(self, 'Warning',"Please write a name for your file", QtGui.QMessageBox.Ok)
def showSaveErrorTwo(self):
	NFmesgBox = QtGui.QMessageBox.warning(self, 'Warning',"Error,There is nothing to save here.", QtGui.QMessageBox.Ok)
def showNoFileError(self):
	NFmesgBox = QtGui.QMessageBox.warning(self, 'Warning',"The file does not exist", QtGui.QMessageBox.Ok)
def showNoFeatureNameError(self):
	NFmesgBox = QtGui.QMessageBox.warning(self, 'Warning',"Please provide a name for the new feature", QtGui.QMessageBox.Ok)
def showUnexpectedError(self):
	NFmesgBox = QtGui.QMessageBox.warning(self, 'Warning',"An Unexpected Error Has Occured", QtGui.QMessageBox.Ok)
def showNoSoftwareNoFeatureError(self):
	NFmesgBox = QtGui.QMessageBox.warning(self, 'Warning',"Please Do Not leave the Software or Feature Field Blank", QtGui.QMessageBox.Ok)
	
