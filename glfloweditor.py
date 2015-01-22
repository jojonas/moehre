from collections import namedtuple, OrderedDict
import math
import inspect
import functools

from PyQt5 import QtOpenGL, QtGui, QtCore, QtWidgets, Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from synth import *
from propertyeditor import camelCaseToWords, Property
	
def glCircle(x,y, radius, segments=10):
	glBegin(GL_TRIANGLE_FAN)
	glVertex2f(x,y)
	t = 0.0
	for i in range(segments+1):
		glVertex2f(x+math.sin(t)*radius, y+math.cos(t)*radius)
		t += math.pi/segments
	glEnd()
	
def qglColor(c):
	glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())

	
class Draggable:
	def isInShape(self, x,y):
		raise NotImplementedError()
		
	def startDrag(self, dragObject):
		pass
		
	def updateDrag(self, dragObject):
		pass
		
	def drawDrag(self, dragObject):
		pass
		
	def dropDrag(self, dragObject):
		pass
	
	
class FlowNode(QtCore.QObject, Draggable):
	nodeFont = None # initialized on first construction

	def __init__(self, func, parent=None):
		QtCore.QObject.__init__(self, parent)
		
		self.x = 20
		self.y = 20
		self.h = 70
		self.w = self.h*1.618 #goldener schnitt!
		self.func = func
		
		self.knobs = []
		
		if not self.isOutput():
			self.knobs.append(FlowKnob(self, FlowKnob.knobTypeOutput, "Output"))
		
		self.properties = OrderedDict()
		
		self.title = camelCaseToWords(func.__name__)
		signature = inspect.signature(func)
		for parameter in signature.parameters.values():
			property = Property(name=parameter.name, type=parameter.annotation, value=parameter.default)
			
			if property.type == SynthParameters:
				property = property._replace(hasKnob=False, hasEditable=False)
			if property.type == np.ndarray:
				property = property._replace(hasKnob=True, hasEditable=False)
			elif property.type == float:
				property = property._replace(hasKnob=True, hasEditable=True)
				
			if property.hasKnob:
				knob = FlowKnob(self, FlowKnob.knobTypeInput, property.name, self.getInputKnobCount())
				self.knobs.append(knob)
				property = property._replace(knob=knob)
			
			self.properties[parameter.name] = property
				
		# cannot be intialized statically, because a QApplication must be started
		if not FlowNode.nodeFont:
			FlowNode.nodeFont = QtWidgets.QApplication.font()
			
		fontMetrics = QtGui.QFontMetrics(self.nodeFont)
		self.fontLineHeight = (fontMetrics.height()+fontMetrics.lineSpacing())
		self.fontHeight = fontMetrics.height()
		self.fontAscent = fontMetrics.ascent()
		self.h = self.fontLineHeight * (self.getInputKnobCount()+1)
				
	def getInputKnobCount(self):
		return len(list(filter(lambda x : x.type == FlowKnob.knobTypeInput, self.knobs)))

	def draw(self, selected=False):
		textOffset = 3
		shadowOffset = (1,1)
		
		qglColor(self.parent().nodeShadowColor)
		glRectf(self.x+shadowOffset[0], self.y+shadowOffset[1], self.x+self.w+shadowOffset[0], self.y+self.h+shadowOffset[1])
		
		qglColor(self.parent().nodeBorderColor if not selected else self.parent().nodeBorderColorSelected)
		glRectf(self.x, self.y, self.x+self.w, self.y+self.h)
		
		qglColor(self.parent().nodeBackgroundColor if not selected else self.parent().nodeBackgroundColorSelected)
		glRectf(self.x+1, self.y+1, self.x+self.w-1, self.y+self.h-1)
		
		for knob in self.knobs:
			knob.draw(textOffset=textOffset)
			
		qglColor(self.parent().nodeBorderColor if not selected else self.parent().nodeBorderColorSelected)
		glBegin(GL_LINES)
		glVertex2f(self.x + 3, self.y + self.fontLineHeight)
		glVertex2f(self.x + self.w - 3, self.y + self.fontLineHeight)
		glEnd()
		
		qglColor(self.parent().nodeTextColor if not selected else self.parent().nodeTextColorSelected)
		self.nodeFont.setBold(True)
		self.parent().renderText(self.x+textOffset, self.y+(self.fontLineHeight+self.fontAscent)*0.5, self.title, font=self.nodeFont) # works only if parent is qglWidget ;)
		self.nodeFont.setBold(False)
		
	def isInShape(self, x,y):
		return self.x <= x <= self.x+self.w and self.y <= y <= self.y+self.h
		
	def startDrag(self, dragObject):
		dragObject.custom = (dragObject.startX - self.x, dragObject.startY - self.y)
		
	def updateDrag(self, dragObject):
		self.x = dragObject.x - dragObject.custom[0]
		self.y = dragObject.y - dragObject.custom[1]
		
	def __str__(self):
		return "FlowNode '%s'" % self.title
		
	def __repr__(self):
		return "<FlowNode '%s'>" % self.title
		
	def isOutput(self):
		return self.func in self.parent().outputFunctions
		
class FlowConnectionError(Exception):
	pass
	
class FlowConnection(QtCore.QObject):
	width = 2
		
	def __init__(self, knobA, knobB, parent=None):
		QtCore.QObject.__init__(self, parent)
		if knobA.type == FlowKnob.knobTypeInput and knobB.type == FlowKnob.knobTypeOutput:
			self.inputKnob = knobA
			self.outputKnob = knobB
		elif knobB.type == FlowKnob.knobTypeInput and knobA.type == FlowKnob.knobTypeOutput:
			self.inputKnob = knobB
			self.outputKnob = knobA
		else:
			raise FlowConnectionError("Invalid connection.")
		
	def draw(self):
		x1, y1 = self.inputKnob.getPosition()
		x2, y2 = self.outputKnob.getPosition()
		self.drawLine(self.parent().connectionColor, x1, y1, x2, y2)
		
	@staticmethod
	def drawLine(color, startX, startY, endX, endY):
		qglColor(color)
		glLineWidth(FlowConnection.width)

		# Bezier Curve
		velocity = 100 # "roundness"
		segments = 20
		glBegin(GL_LINE_STRIP)
		for segment in range(segments+1):
			t = segment / segments
			u = 1-t
			tt = t*t
			uu = u*u
			uuu = uu*u
			ttt = tt*t
			# 
			x = uuu*startX + 3*uu*t*(startX-velocity) + 3*u*tt*(endX+velocity) + ttt*endX
			y = uuu*startY + 3*uu*t*(startY) + 3*u*tt*(endY) + ttt*endY
			glVertex2f(x, y)
		glEnd()
		
	def __str__(self):
		return "FlowConnection from '%s' to '%s'" % (self.outputKnob, self.inputKnob)
		
	def __repr__(self):
		return "<FlowConnection '%s' => '%s'>" % (self.outputKnob, self.inputKnob)
		
class FlowKnob(QtCore.QObject, Draggable):
	knobTypeInput = 1
	knobTypeOutput = 2
	
	radius = 10
	
	def __init__(self, node, type, name, index=-1):
		self.node = node
		self.type = type
		self.index = index
		self.name = name
		
	def draw(self, textOffset=0):
		x,y = self.getPosition()
		if not self.isConnected():
			qglColor(self.node.parent().knobColor)
		else:
			qglColor(self.node.parent().connectionColor)
		if self.type == self.knobTypeOutput:
			glCircle(x,y, self.radius)
		if self.type == self.knobTypeInput:
			glCircle(x,y, -self.radius) # negative radius to flip half circle
			qglColor(self.node.parent().nodeTextColor)
			self.node.parent().renderText(x+3, y+self.node.fontAscent*0.5, self.name, font=self.node.nodeFont) 
		
	def getPosition(self): # relative to node coordinates
		if self.type == self.knobTypeInput:
			dist = self.node.fontLineHeight
			#dist = self.node.h / (self.node.getInputKnobCount()+1)
			return self.node.x, self.node.y + (self.index+1.5)*dist
		elif self.type == self.knobTypeOutput:
			return self.node.x + self.node.w, self.node.y + self.node.h/2
		
	def isInShape(self, x,y):
		kx, ky = self.getPosition()
		if self.type == self.knobTypeInput:
			return kx-self.radius <= x <= kx and ky-self.radius <= y <= ky+self.radius
		elif self.type == self.knobTypeOutput:
			return kx <= x <= kx+self.radius and ky-self.radius <= y <= ky+self.radius
			
	def isConnected(self):
		return next(self.node.parent().findConnections(self), None) is not None
			
	def drawDrag(self, dragObject):
		# swap them if necessary, so the bezier curves won't look off (have the right control points)
		fromX, fromY = dragObject.startX, dragObject.startY
		toX, toY = dragObject.x, dragObject.y
		if self.type == self.knobTypeOutput:
			fromX, toX = toX, fromX
			fromY, toY = toY, fromY
		FlowConnection.drawLine(self.node.parent().connectionColor, fromX, fromY, toX, toY)
		
	def dropDrag(self, dragObject):
		knob = self.node.parent().pickKnob(dragObject.x, dragObject.y)
		if knob and knob is not self:
			connection = FlowConnection(self, knob, parent=self.node.parent())
			self.node.parent().addConnection(connection)
	
	def __str__(self):
		return "FlowKnob of '%s' (index %d, type %d)" % (self.node, self.index, self.type)
		
	def __repr__(self):
		return "<FlowKnob of '%s' (index %d, type %d)>" % (self.node, self.index, self.type)

class GLFlowEditor(QtOpenGL.QGLWidget):
	signalEditNode = QtCore.pyqtSignal(OrderedDict)
	
	dragModeDraggingEmpty = 0
	dragModeDraggingNode = 1
	dragModeDraggingConnectionInToOut = 2
	dragModeDraggingConnectionOutToIn = 3
	
	class DragObject:
		def __init__(self, startX, startY, draggable):
			self.startX = startX
			self.startY = startY
			self.draggable = draggable
			self.custom = None
			self.draggable.startDrag(self)
			
		def update(self, currentX, currentY):
			self.x = currentX 
			self.y = currentY 
			self.draggable.updateDrag(self)
			
		def drop(self):
			self.draggable.dropDrag(self)
			
		def draw(self):
			self.draggable.drawDrag(self)
	
	def __init__(self, parent=None, *, outputFunctions=(), functions=()):
		format = QtOpenGL.QGLFormat.defaultFormat()
		format.setSampleBuffers(True)
		format.setSamples(16)
		QtOpenGL.QGLWidget.__init__(self, format, parent)
		if not self.isValid():
			raise OSError("OpenGL not supported.")
			
		self.functions = functions
		self.outputFunctions = outputFunctions
		self.nodes = []
		self.connections = []
		
		self.dragObject = None
		self.selectedNode = None
		
		self.addNode(Output, 600, 300) # outputDummy should be a static function in the synthesizer
		
		# Fallback:
		palette = self.palette()
		self.backgroundColor = palette.color(QtGui.QPalette.Base)
		self.nodeBackgroundColor = palette.color(QtGui.QPalette.Button)
		self.nodeBackgroundColorSelected = palette.color(QtGui.QPalette.Light)
		self.nodeBorderColor = palette.color(QtGui.QPalette.Dark)
		self.nodeBorderColorSelected = palette.color(QtGui.QPalette.Dark)
		self.nodeShadowColor = palette.color(QtGui.QPalette.Shadow)
		self.nodeTextColor = palette.color(QtGui.QPalette.Text)
		self.nodeTextColorSelected = palette.color(QtGui.QPalette.Text)
		self.knobColor = palette.color(QtGui.QPalette.Button)
		self.connectionColor = palette.color(QtGui.QPalette.Dark)

		mode = "nohighcontrast"
		if mode == "highcontrast":
			self.backgroundColor = QtGui.QColor(QtCore.Qt.darkGray)
			self.nodeBackgroundColor = QtGui.QColor(QtCore.Qt.darkGreen)
			self.nodeBackgroundColorSelected = QtGui.QColor(QtCore.Qt.darkGreen)
			self.nodeBorderColor = QtGui.QColor(QtCore.Qt.black)
			self.nodeBorderColorSelected = QtGui.QColor(QtCore.Qt.green)
			self.nodeShadowColor = QtGui.QColor(QtCore.Qt.black)
			self.nodeTextColor = QtGui.QColor(QtCore.Qt.white)
			self.nodeTextColorSelected = QtGui.QColor(QtCore.Qt.white)
			self.knobColor = QtGui.QColor(QtCore.Qt.darkRed)
			self.connectionColor = QtGui.QColor(QtCore.Qt.yellow)
		
	def initializeGL(self):
		self.qglClearColor(self.backgroundColor)
		glEnable(GL_MULTISAMPLE)
		glEnable(GL_LINE_SMOOTH)
		
	def resizeGL(self, w, h):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0,w,h,0)
		glViewport(0,0,w,h)
		
	def paintGL(self):
		glClear(GL_COLOR_BUFFER_BIT)
		
		for node in reversed(self.nodes):
			node.draw(selected=(node is self.selectedNode))
		
		for connection in self.connections:
			connection.draw()
			
		if self.dragObject:
			self.dragObject.draw()
			
	def addNode(self, func, x,y):
		node = FlowNode(func, self)
		node.x = x
		node.y = y
		self.nodes.append(node)
		self.selectNode(node)
		
	def addConnection(self, connection):
		for c in self.findConnections(connection.inputKnob):
			if c.inputKnob == connection.inputKnob:
				raise FlowConnectionError("Knob already connected.")
		self.connections.append(connection)
		
	def pickKnob(self, x, y):
		for node in self.nodes:
			for knob in node.knobs:
				if knob.isInShape(x,y):
					return knob
					
	def pickNode(self, x, y):
		for node in self.nodes:
			if node.isInShape(x,y):
				return node
					
	def findConnections(self, knob):
		for c in self.connections:
			if c.inputKnob == knob or c.outputKnob == knob:
				yield c
				
	def selectNode(self, node):
		self.selectedNode = node
		if node:
			self.signalEditNode.emit(node.properties)
		else:
			self.signalEditNode.emit(OrderedDict())
		self.updateGL()
		
	def deleteNode(self, node):
		if node.isOutput():
			raise RuntimeError("Output node must not be deleted")		
		else:
			connectionsToDelete = []
			for knob in node.knobs:	
				connectionsToDelete.extend(self.findConnections(knob))	
			self.connections = [c for c in self.connections if c not in connectionsToDelete]
				
			self.nodes.remove(node)
			del node
								
		
	def mousePressEvent(self, event):
		x, y = event.x(), event.y()	
		if event.button() & QtCore.Qt.LeftButton:
			node = self.pickNode(x,y)
			if node:
				self.dragObject = self.DragObject(x, y, node)
				i = self.nodes.index(node)
				self.nodes[0], self.nodes[i] = self.nodes[i], self.nodes[0]
				self.selectNode(node)
				self.updateGL() # updateGL because z-order has changed
				return
			
			knob = self.pickKnob(x,y)
			if knob:
				self.dragObject = self.DragObject(x, y, knob)
				return
				
			self.selectNode(None)
				
		elif event.button() & QtCore.Qt.RightButton:
			knob = self.pickKnob(x,y)
			if knob:
				connections = list(self.findConnections(knob))
				if knob.type == FlowKnob.knobTypeOutput and len(connections) > 1:
					if QtWidgets.QMessageBox.question(self.parent(), "Delete Connection", "Do you really want to delete all connections from this output?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
						return
				for connection in connections:
					self.connections.remove(connection)
					del connection
				
	
	def contextMenuEvent(self, event):
		menu = QtWidgets.QMenu(parent=self.parent())
		
		x,y = event.x(), event.y()
		node = self.pickNode(x,y)
		if node:
			action = menu.addAction("Delete node")
			action.triggered.connect(functools.partial(self.deleteNode, node))
		else:	
			for i, func in enumerate(self.functions):
				if func not in self.outputFunctions:
					action = menu.addAction(camelCaseToWords(func.__name__))
					action.triggered.connect(functools.partial(self.addNode, func, x, y)) # lambda does not work in this case!! 
		menu.popup(event.globalPos())
			
	def mouseReleaseEvent(self, event):
		if self.dragObject:
			try:
				self.dragObject.update(event.x(), event.y())
				self.dragObject.drop()
			finally:
				self.dragObject = None
				self.updateGL()
		
	def mouseMoveEvent(self, event):
		if self.dragObject:
			self.dragObject.update(event.x(), event.y())
			self.updateGL()
	
	def keyPressEvent(self, event):
		if event.matches(QtGui.QKeySequence.Delete):
			if self.selectedNode:
				if self.selectedNode.isOutput():
					QtWidgets.QMessageBox.warning(self.parent(), "Delete Node", "Cannot delete output node.", QtWidgets.QMessageBox.Ok)
				elif QtWidgets.QMessageBox.question(self.parent(), "Delete Node", "Do you really want to delete this node?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
					self.deleteNode(self.selectedNode)		
					self.selectNode(None)
							
						
						
						
				