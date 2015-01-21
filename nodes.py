from decorators import *
from usernodes import *
from synth import SynthParameters
import numpy as np

@registerFunction
def sin(params:SynthParameters=None, frequencyShift:np.ndarray=0.0, frequency:float=440, amplitude:float=1.0):
	t = np.linspace(0.0, params.length, params.samples)
	return amplitude*np.sin(2 * np.pi * (frequency+frequencyShift)*t)
	
@registerFunction
def rectangle(params:SynthParameters=None, frequency:float=440, amplitude:float=1.0, duty:float=0.5):
	t = np.linspace(0.0, params.length, params.samples)*frequency
	t -= np.floor(t)
	return np.where(t <= duty, amplitude, -amplitude)
	
@registerFunction
def clamp(channel:np.ndarray=0.0, level:float=1.0):
	return np.clip(channel, -level, level)
	
@registerFunction
def mix(channelA:np.ndarray=0.0, channelB:np.ndarray=0.0, mixA:float=0.5, mixB:float=0.5):
	return (channelA*mixA + channelB*mixB)
	
#sawtooth, triangle, whistle, whiteNoise, rectangle (frequency, duty cycle)
#delay, cheapReverb
#mix
#step -> rectangle, linear, exponential, 