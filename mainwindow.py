import sys
import traceback
import contextlib

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
		
		self.glFlowEditor = GLFlowEditor(parent=self, functions=getRegisteredFunctions(), outputFunctions=getRegisteredOutputFunctions())
		self.glFlowEditor.signalEditNode.connect(self.tableProperties.loadProperties)
		
		self.setCentralWidget(self.glFlowEditor)
		
	def handleError(self, shortMessage, longMessage):
		self.statusBar.showMessage(shortMessage)
		
class QtLoggingHandler(QtCore.QObject):
	signalHandleError = QtCore.pyqtSignal([str, str])
	
	def __init__(self):
		QtCore.QObject.__init__(self)
	
	def __call__(self, type, value, tb):
		short = "".join(traceback.format_exception_only(type, value))
		long = "".join(traceback.format_exception(type, value, tb))
		print(long, file=sys.stderr)
		self.signalHandleError.emit(short, long)
		
@contextlib.contextmanager
def excepthook(func):
	tmp = sys.excepthook 
	sys.excepthook = func
	yield func
	sys.excepthook = tmp
	
if __name__=="__main__":
	handler = QtLoggingHandler()
	with excepthook(handler):
		app = QtWidgets.QApplication(sys.argv)
		window = MainWindow()
		handler.signalHandleError.connect(window.handleError)
		window.show()
		sys.exit(app.exec_())
	