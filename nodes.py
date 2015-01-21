import numpy as np

from decorators import *
from usernodes import *
from synth import SynthParameters

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
def mix(channelA:np.ndarray=0.0, channelB:np.ndarray=0.0, mixValue:float=0.5):
	return (channelA*(1-mixValue) + channelB*mixValue)
	
@registerFunction
def sawtooth(params:SynthParameters=None, frequency:float=440, amplitude:float=1.0):
	t = np.linspace(0.0, params.length, params.samples)*frequency
	return ((t - np.floor(t)) * 2.0 - 1.0) * amplitude

@registerFunction
def whiteNoise(params:SynthParameters=None, amplitude:float=1.0):
	return (np.random.rand(params.samples) * 2.0 - 1.0) * amplitude

@registerFunction	
def whistle(params:SynthParameters=None, frequency:float=440, mixValue:float=0.5, frequencyFactor:float=10.0, amplitude:float=1.0):
	t = np.linspace(0.0, params.length, params.samples)
	return amplitude*mix(np.sin(2*np.pi*frequency * t), np.sin(2*np.pi*frequency*frequencyFactor * t), mixValue)
	
@registerFunction	
def triangleSawtooth(params:SynthParameters=None, frequency:float=440, amplitude:float=1.0, upLength:float=0.5):
	t = np.linspace(0.0, params.length, params.samples)*frequency
	t -= np.floor(t)
	up = None
	if upLength < 1e-5:
		up = amplitude
	else:
		up = amplitude * (-1.0 + 2.0/upLength*t)
	down = amplitude * (3.0 - 2.0/(1.0-upLength)*t)
	return np.where(t < upLength, up, down)
	
@registerFunction
def step(params:SynthParameters=None, stepTime:float=0.5, fromValue:float=0.0, toValue:float=1.0):
	t = np.linspace(0.0, params.length, params.samples)
	return np.where(t < stepTime, fromValue, toValue)
	
@registerFunction	
def linear(params:SynthParameters=None, startTime:float=0.0, startValue:float=0.0, endTime:float=1.0, endValue:float=1.0):
	t = np.linspace(0.0, params.length, params.samples)
	slope = (endValue - startValue) / (endTime - startTime)
	return np.clip(startValue-startTime*slope + slope*t, min(startValue, endValue), max(startValue, endValue))
	
@registerFunction
def delay(params:SynthParameters=None, signal:np.ndarray=0.0, delayTime:float=0.1):
	zeroLen = int(delayTime * params.sampleRate)
	return np.append(np.zeros(zeroLen), signal[zeroLen:params.samples])

#cheapReverb, exponential