import sys
from PyQt5 import QtCore, QtWidgets, QtGui, uic

from decorators import *
from glfloweditor import *
from propertyeditor import *

@registerFunction
def foo(data, x, y:int=0):
	print("Bar", x)
	
@registerFunction
def bar(koko, loo, aa, pepe:str="popo", nana:int=0):
	pass
	
@registerFunction
def bar2(koko, loo, aa, pepe:str="popo", nana:int=0):
	pass
	
@registerFunction
def bar3(koko, loo, aa, pepe:str="popo", nana:int=0):
	pass

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
		
		self.glFlowEditor = GLFlowEditor(parent=self, functions=getRegisteredFunctions())
		self.glFlowEditor.signalEditNode.connect(self.tableProperties.loadProperties)
		
		self.setCentralWidget(self.glFlowEditor)
		
		
if __name__=="__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
	