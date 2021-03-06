import sys
import traceback
import contextlib
import os, os.path

from PyQt5 import QtCore, QtWidgets, QtGui, uic

from glfloweditor import *
from propertyeditor import *
from synth import *
from keymap import getKeyMap

from nodes import *
import audio

form, base = uic.loadUiType("mainwindow.ui")
class MainWindow(form,base):
	def __init__(self):
		base.__init__(self)
		self.setupUi(self)
		
		self.setWindowTitle("Möhre")
		self.setFocusPolicy(QtCore.Qt.StrongFocus)
		
		self.actionPlay.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
		self.actionPlay.triggered.connect(self.play)
		
		self.actionStop.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaStop))		
		
		self.actionSave.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton))
		self.actionSave.triggered.connect(self.save)		
		
		self.actionOpen.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton))
		self.actionOpen.triggered.connect(self.open)
		
		self.actionExport.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
		self.actionExport.triggered.connect(self.export)
		
		self.tableProperties = PropertyWidget(parent=self)
		self.layoutDockProperty.layout().addWidget(self.tableProperties)
		
		self.glFlowEditor = GLFlowEditor(parent=self, functions=getRegisteredFunctions(), outputFunctions=getRegisteredOutputFunctions())
		self.glFlowEditor.signalEditNode.connect(self.tableProperties.loadProperties)
		
		self.setCentralWidget(self.glFlowEditor)
		
		self.synthesizer = Synthesizer()
		audio.initAudio()
		
	def play(self):
		self.synthesizer.play(self.glFlowEditor)
	
	def export(self):
		fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export to file", filter="wave files (*.wav);;All files (*.*)")
		if fileName:
			self.synthesizer.saveToFile(self.glFlowEditor, fileName)
			
	def save(self):
		fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save to file", filter="Möhre Flow Graph (*.mfg);;All files (*.*)")
		if fileName:
			self.glFlowEditor.saveGraph(fileName)
			
	def open(self):
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", filter="Möhre Flow Graph (*.mfg);;All files (*.*)")
		if fileName:
			self.openFile(fileName)
			
	def openFile(self, fileName): # for command line passing
		self.glFlowEditor.loadGraph(fileName)
		
	def handleError(self, shortMessage, longMessage):
		self.statusBar.showMessage(shortMessage)
		
	def keyPressEvent(self, event):
		if event.matches(QtGui.QKeySequence.Delete):
			print("FOCUS", QtWidgets.QApplication.focusWidget())
			self.glFlowEditor.dialogDeleteNode()
			return
		elif not event.isAutoRepeat():
			keyMap = getKeyMap()
			if event.nativeScanCode() in keyMap:
				note = keyMap[event.nativeScanCode()]
				self.synthesizer.playNote(self.glFlowEditor, note)
				return
		QtWidgets.QWidget.keyPressEvent(self, event)
			
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
		logo = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logo.svg")
		app.setWindowIcon(QtGui.QIcon(logo))
		window = MainWindow()
		handler.signalHandleError.connect(window.handleError)
		if len(sys.argv) > 1:
			window.openFile(sys.argv[1])
		window.show()
		sys.exit(app.exec_())
	