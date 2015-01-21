from decorators import *
from scipy.interpolate import interp1d
import numpy as np

class SynthBuffer(np.ndarray):
	def __init__(self, value = None):
		if value:
			self.fill(value)
		
class SynthParameters:
	def __init__(self, rate, length):
		self.sampleRate = rate
		self.length = length
		self.samples = length * rate
	
class SynthException(Exception):
	pass
	
@registerOutputFunction # potential parameters: envelope, looping (ping-pong, forward)
def Output(synthParameters:SynthParameters=None, input:SynthBuffer=0.0, sampleRate:int=44100, length:float=2.0, playbackSpeedFactor:float=1.0):
	pass
	
class Synthesizer:
	def __init__(self):
		self.soundBuffer = None
		self.synthParameters = None
		self.playbackSpeedFactor = 1.0
		
	def _workNode(node, flowGraph, previous = []):
		inputs = []
		for knob in node.knobs:
			if knob.type == knob.knobTypeInput:
				for connection in flowGraph.findConnections(knob):
					if connection.outputKnob in previous:
						raise SynthException("No loops allowed in graph.")
					else:
						# trim buffer in length
						inputs[knob.name] = _workNode(connection.outputKnob.node, flowGraph, previous + [node])
		
		parameters = []
		signature = inspect.signature(node.func)
		for parameter in signature.parameters.values():
			if parameter.name in node.properties:
				parameters[parameter.name] = node.properties[parameter.name][1] # [1] = value
			else:
				if parameter.annotation() == SynthBuffer:
					parameters[parameter.name] = inputs[parameter.name] if parameter.name in inputs else SynthBuffer(parameter.default)
				elif parameter.annotation() == SynthParameters:
					parameters[parameter.name] = self.synthParameters
				
		return node.func(**parameters)
		
	def synthesizeFromFlowGraph(self, flowGraph):
		outputNodes = [node for node in flowGraph.nodes if x.func in flowGraph.outputFunctions]
		if len(outputNodes) != 1:
			raise SynthException("Exactly one Output node required.")
		else:
			self.synthParameters = SynthParameters(outputNodes[0].parameters["sampleRate"], outputNodes[0].parameters["length"])
			self.playbackSpeedFactor = outputNodes[0].parameters["playbackSpeedFactor"]
			self.soundBuffer = _workNode(outputNodes[0], flowGraph)
	
	def play(self, flowGraph):
		self.synthesizeFromFlowGraph(self, flowGraph)
		xUnscaled = np.linspace(0, self.length, self.rate * self.length)
		xScaled = np.linspace(0, self.length, self.rate * self.length * self.playbackSpeedFactor)
		interpolator = interp1d(xUnscaled, self.soundBuffer)
		playbackBuffer = interpolator(xScaled)
		# play self.soundBuffer
		pass