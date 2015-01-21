import sys
from PyQt5 import QtCore, QtWidgets, QtGui, uic

from decorators import *
from glfloweditor import *
from propertyeditor import *
from synth import *

form, base = uic.loadUiType("mainwindow.ui")
class MainWindow(form,base):
	def __init__(self):
		base.__init__(self)
		self.setupUi(self)
		
		self.setWindowTitle("Möhre")
		
		self.actionPlay.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
		self.actionStop.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaStop))
		
		self.tableProperties = PropertyWidget(parent=self)
		self.layoutDockProperty.layout().addWidget(self.tableProperties)
		
		self.glFlowEditor = GLFlowEditor(parent=self, functions=getRegisteredFunctions(), outputs=getRegisteredOutputFunctions())
		self.glFlowEditor.signalEditNode.connect(self.tableProperties.loadProperties)
		
		self.setCentralWidget(self.glFlowEditor)
		
		
if __name__=="__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
	