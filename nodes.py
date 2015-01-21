from decorators import *
from usernodes import *
from synth import SynthParameters
import numpy as np

@registerFunction
def sin(params:SynthParameters=None, modulation:np.ndarray=0.0, frequency:float=440, amplitude:float=1.0):
	t = np.linspace(0.0, params.length, params.samples)
	return amplitude*np.sin(2 * np.pi * frequency * t + modulation)
	
@registerFunction
def rectangle(params:SynthParameters=None, frequency:float=440, amplitude:float=1.0, duty:float=0.5):
	t = np.linspace(0.0, params.length, params.samples)*frequency
	t -= np.floor(t)
	return np.where(t <= duty, amplitude, -amplitude)
	
@registerFunction
def clamp(channel:np.ndarray=0.0, level:float=1.0):
	return np.clip(channel, -level, level)
	
@registerFunction
def mix2(channelA:np.ndarray=0.0, channelB:np.ndarray=0.0, mixA:float=0.5, mixB:float=0.5):
	return (channelA*mixA + channelB*mixB)
	
@registerFunction
def mix(channelA:np.ndarray=0.0, channelB:np.ndarray=0.0, mix:float=0.5):
	return (channelA*(1-mix) + channelB*mix)
	
@registerFunction
def sawtooth(params:SynthParameters=None, frequency:float=440, amplitude:float=1.0):
	t = np.linspace(0.0, params.length, params.samples)*frequency
	return ((t - np.floor(t)) * 2.0 - 1.0) * amplitude
	
	
#triangle, whistle, whiteNoise
#delay, cheapReverb
#step -> rectangle, linear, exponential