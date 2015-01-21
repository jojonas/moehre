from collections import namedtuple, OrderedDict
import math
import inspect
import functools

from PyQt5 import QtOpenGL, QtGui, QtCore, QtWidgets, Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from synth import *
	
def glCircle(x,y, radius, segments=10):
	glBegin(GL_TRIANGLE_FAN)
	glVertex2f(x,y)
	t = 0.0
	for i in range(segments+1):
		glVertex2f(x+math.cos(t)*radius, y+math.sin(t)*radius)
		t += 2*math.pi/segments
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
	def __init__(self, func, parent=None):
		QtCore.QObject.__init__(self, parent)
		
		self.x = 20
		self.y = 20
		self.h = 70
		self.w = self.h*1.618 #goldener schnitt!
		self.func = func
		
		self.knobs = []
		
		if func not in self.parent().outputFunctions:
			self.knobs.append(FlowKnob(self, FlowKnob.knobTypeOutput, "Output"))
		
		self.properties = OrderedDict()
		
		self.title = func.__name__
		signature = inspect.signature(func)
		for parameter in signature.parameters.values():
			if parameter.annotation == SynthBuffer: # data
				# -1 because the first one is the output knob
				knob = FlowKnob(self, FlowKnob.knobTypeInput, parameter.name, self.getInputKnobCount())
				self.knobs.append(knob)
			elif parameter.annotation == SynthParameters:
				pass
			else:
				self.properties[parameter.name] = (parameter.annotation, parameter.default)		
				
	def getInputKnobCount(self):
		return len(list(filter(lambda x : x.type == FlowKnob.knobTypeInput, self.knobs)))

	def draw(self, selected=False):
		palette = self.parent().palette()
		
		qglColor(palette.color(QtGui.QPalette.Shadow))
		
		for knob in self.knobs:
			knob.draw()
		
		qglColor(palette.color(QtGui.QPalette.Dark))
		glRectf(self.x, self.y, self.x+self.w, self.y+self.h)
		
		if not selected:
			qglColor(palette.color(QtGui.QPalette.Button))
		else:
			qglColor(palette.color(QtGui.QPalette.Highlight))
			
		glRectf(self.x+1, self.y+1, self.x+self.w-1, self.y+self.h-1)
		
		qglColor(palette.color(QtGui.QPalette.Text))
		self.parent().renderText(self.x+4, self.y+15, self.title) # works only if parent is qglWidget ;)
		
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
		color = self.parent().palette().color(QtGui.QPalette.Highlight)
		x1, y1 = self.inputKnob.getPosition()
		x2, y2 = self.outputKnob.getPosition()
		self.drawLine(color, x1, y1, x2, y2)
		
	@staticmethod
	def drawLine(color, startX, startY, endX, endY):
		qglColor(color)
		glLineWidth(FlowConnection.width)

		glBegin(GL_LINES)
		glVertex2f(startX, startY)
		glVertex2f(endX, endY)
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
		
	def draw(self):
		x,y = self.getPosition()
		glCircle(x,y, self.radius)
		
	def getPosition(self): # relative to node coordinates
		if self.type == self.knobTypeInput:
			dist = self.node.h / (self.node.getInputKnobCount()+1)
			return self.node.x, self.node.y + (self.index+1)*dist
		elif self.type == self.knobTypeOutput:
			return self.node.x + self.node.w, self.node.y + self.node.h/2
		
	def isInShape(self, x,y):
		kx, ky = self.getPosition()
		if self.type == self.knobTypeInput:
			return kx-self.radius <= x <= kx and ky-self.radius <= y <= ky+self.radius
		elif self.type == self.knobTypeOutput:
			return kx <= x <= kx+self.radius and ky-self.radius <= y <= ky+self.radius
			
	def drawDrag(self, dragObject):
		color = self.node.parent().palette().color(QtGui.QPalette.Highlight)
		FlowConnection.drawLine(color, dragObject.startX, dragObject.startY, dragObject.x, dragObject.y)
		
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
		QtOpenGL.QGLWidget.__init__(self, parent)
		if not self.isValid():
			raise OSError("OpenGL not supported.")
			
		self.functions = functions
		self.outputFunctions = outputFunctions
		self.nodes = []
		self.connections = []
		
		self.dragObject = None
		self.selectedNode = None
		
		self.addNode(Output, 50, 50) # outputDummy should be a static function in the synthesizer
		
		
	def initializeGL(self):
		self.qglClearColor(self.palette().color(QtGui.QPalette.Base))
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
		self.updateGL()
		
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
					
	def findConnections(self, knob):
		for c in self.connections:
			if c.inputKnob == knob or c.outputKnob == knob:
				yield c
		
	def mousePressEvent(self, event):
		x, y = event.x(), event.y()	
		if event.button() & QtCore.Qt.LeftButton:
			for i, node in enumerate(self.nodes):
				if node.isInShape(x,y):
					self.dragObject = self.DragObject(x, y, node)
					self.nodes[0], self.nodes[i] = self.nodes[i], self.nodes[0]
					self.selectedNode = node
					self.signalEditNode.emit(node.properties)
					self.updateGL() # updateGL because z-order has changed
					return
			
			knob = self.pickKnob(x,y)
			if knob:
				self.dragObject = self.DragObject(x, y, knob)
				return
				
			self.selectedNode = None
			self.signalEditNode.emit(OrderedDict())
			self.updateGL()
				
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
		#menu.setTearOffEnabled(True)
		for i, func in enumerate(self.functions):
			if func not in self.outputFunctions:
				action = menu.addAction(func.__name__)
				x,y = event.x(), event.y()
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
			if self.selectedNode and QtWidgets.QMessageBox.question(self.parent(), "Delete Node", "Do you really want to delete this node?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:

				connectionsToDelete = []
				for knob in self.selectedNode.knobs:	
					connectionsToDelete.extend(self.findConnections(knob))	
				self.connections = [c for c in self.connections if c not in connectionsToDelete]
					
				self.nodes.remove(self.selectedNode)
				del self.selectedNode
				
				self.selectedNode = None				
				self.updateGL()
					
					
					
					
					
					
			