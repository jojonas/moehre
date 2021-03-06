import wave

from scipy.interpolate import interp1d
import numpy as np

from decorators import *
import audio
		
class SynthParameters:
	def __init__(self, rate, length):
		self.sampleRate = rate
		self.length = length
		self.samples = int(length * rate)
	
class SynthException(Exception):
	pass
	
@registerOutputFunction # potential parameters: envelope, looping (ping-pong, forward)
def Output(synthParameters:SynthParameters=None, input:StreamOnly(np.ndarray)=0.0, sampleRate:PropertyOnly(int)=44100, length:PropertyOnly(float)=2.0, playbackSpeedFactor:PropertyOnly(float)=1.0):
	return input
	
class Synthesizer:
	def __init__(self):
		self.soundBuffer = None
		self.synthParameters = None
		self.playbackSpeedFactor = 1.0
		
	def _workNode(self, node, flowGraph, previous = []):
		inputs = {}
		for knob in node.knobs:
			if knob.type == knob.knobTypeInput:
				for connection in flowGraph.findConnections(knob):
					if connection.outputKnob.node in previous:
						raise SynthException("No loops allowed in graph.")
					else:
						# trim buffer in length
						inputs[knob.name] = self._workNode(connection.outputKnob.node, flowGraph, previous + [node])
		
		parameters = {}
		signature = inspect.signature(node.func)
		for parameter in signature.parameters.values():
			property = node.properties[parameter.name]
			if property.type == SynthParameters:
				parameters[parameter.name] = self.synthParameters
			elif property.name in inputs:
				parameters[parameter.name] = inputs[parameter.name]
			elif property.hasEditable:
				parameters[parameter.name] = node.properties[parameter.name].value
			elif property.hasKnob: # knob not connected, else it would be in inputs
				parameters[parameter.name] = np.ndarray(self.synthParameters.samples)
				parameters[parameter.name].fill(parameter.default)
				
		return node.func(**parameters)
		
	def synthesizeFromFlowGraph(self, flowGraph):
		outputNodes = [node for node in flowGraph.nodes if node.func in flowGraph.outputFunctions]
		if len(outputNodes) != 1:
			raise SynthException("Exactly one Output node required.")
		else:
			self.synthParameters = SynthParameters(outputNodes[0].properties["sampleRate"].value, outputNodes[0].properties["length"].value)
			self.playbackSpeedFactor = outputNodes[0].properties["playbackSpeedFactor"].value
			self.soundBuffer = self._workNode(outputNodes[0], flowGraph)
			
	def saveToFile(self, flowGraph, filename):
		self.synthesizeFromFlowGraph(flowGraph)
		with wave.open(filename, 'wb') as file:
			file.setnchannels(1)
			file.setsampwidth(2)
			file.setframerate(self.synthParameters.sampleRate)
			file.setnframes(self.synthParameters.samples)
			clamped = np.clip(self.soundBuffer, -1.0, 1.0)
			scaled = np.int16(clamped*32767)
			file.writeframesraw(scaled.tobytes()) # normal writeframes doesn't work even though written frames and nframes are equal?
	
	def play(self, flowGraph, additionalSpeedModifier=1.0):
		self.synthesizeFromFlowGraph(flowGraph)
		xUnscaled = np.linspace(0, self.synthParameters.length, self.synthParameters.samples)
		xScaled = np.linspace(0, self.synthParameters.length, self.synthParameters.samples / (self.playbackSpeedFactor*additionalSpeedModifier))
		interpolator = interp1d(xUnscaled, self.soundBuffer)
		playbackBuffer = interpolator(xScaled)
		audio.play(playbackBuffer, self.synthParameters.sampleRate)
		
	@staticmethod
	def noteToMultiplier(note):
		assert 2 <= len(note) <= 3, "Note format not understood"
		baseNotes = "cdefgab"
		modifiers = "b#"
		
		base = note[0].lower()
		if len(note) == 2:
			modifier = " "
		elif len(note) == 3:
			modifier = note[1]
		octave = int(note[-1])
	
		assert base and base in "cdefgab", "Illegal note"
		assert modifier in "b #", "Illegal note modifier"
		assert 0 <= octave <= 8, "Octave out of range"
		
		n = octave*12 + ("c d ef g a b".index(base)) + ("b #".index(modifier)-1) - 8
		factor = 2**((n-49)/12)
		return factor

	def playNote(self, flowGraph, note):
		factor = self.noteToMultiplier(note)
		self.play(flowGraph, additionalSpeedModifier=factor)
	