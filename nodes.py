import wave
import math

import numpy as np

from decorators import *
from usernodes import *
from synth import SynthParameters, SynthException

# Generators

@registerFunction
def sin(params:SynthParameters=None, modulation:StreamOrProperty(float)=0.0, frequency:StreamOrProperty(float)=440, amplitude:StreamOrProperty(float)=1.0):
	t = np.linspace(0.0, params.length, params.samples)
	return amplitude*np.sin(2 * np.pi * frequency * t + modulation)
	
@registerFunction
def rectangle(params:SynthParameters=None, frequency:StreamOrProperty(float)=440, amplitude:StreamOrProperty(float)=1.0, duty:StreamOrProperty(float)=0.5):
	t = np.linspace(0.0, params.length, params.samples)*frequency
	t -= np.floor(t)
	return np.where(t <= duty, amplitude, -amplitude)
	
@registerFunction
def step(params:SynthParameters=None, stepTime:StreamOrProperty(float)=0.5, fromValue:StreamOrProperty(float)=0.0, toValue:StreamOrProperty(float)=1.0):
	t = np.linspace(0.0, params.length, params.samples)
	return np.where(t < stepTime, fromValue, toValue)
	
@registerFunction	
def linear(params:SynthParameters=None, startTime:StreamOrProperty(float)=0.0, startValue:StreamOrProperty(float)=0.0, endTime:StreamOrProperty(float)=1.0, endValue:StreamOrProperty(float)=1.0):
	t = np.linspace(0.0, params.length, params.samples)
	slope = (endValue - startValue) / (endTime - startTime)
	return np.clip(startValue-startTime*slope + slope*t, min(startValue, endValue), max(startValue, endValue))
	
@registerFunction
def exponential(params:SynthParameters=None, amplitude:StreamOrProperty(float)=1.0, decayConstant:StreamOrProperty(float)=round(math.log(0.5), 2)):
	t = np.linspace(0.0, params.length, params.samples)
	return amplitude*np.exp(decayConstant*t)
	
@registerFunction
def sawtooth(params:SynthParameters=None, frequency:StreamOrProperty(float)=440, amplitude:StreamOrProperty(float)=1.0):
	t = np.linspace(0.0, params.length, params.samples)*frequency
	return ((t - np.floor(t)) * 2.0 - 1.0) * amplitude

@registerFunction	
def whistle(params:SynthParameters=None, frequency:StreamOrProperty(float)=440, mixValue:StreamOrProperty(float)=0.5, frequencyFactor:StreamOrProperty(float)=10.0, amplitude:StreamOrProperty(float)=1.0):
	t = np.linspace(0.0, params.length, params.samples)
	return amplitude*mix(np.sin(2*np.pi*frequency * t), np.sin(2*np.pi*frequency*frequencyFactor * t), mixValue)
	
@registerFunction	
def triangleSawtooth(params:SynthParameters=None, frequency:StreamOrProperty(float)=440, amplitude:StreamOrProperty(float)=1.0, risingTime:StreamOrProperty(float)=0.5):
	t = np.linspace(0.0, params.length, params.samples)*frequency
	t -= np.floor(t)
	up = None
	if risingTime < 1e-5:
		up = amplitude
	else:
		up = amplitude * (-1.0 + 2.0/risingTime*t)
	down = amplitude * (3.0 - 2.0/(1.0-risingTime)*t)
	return np.where(t < risingTime, up, down)
	
@registerFunction
def whiteNoise(params:SynthParameters=None, amplitude:StreamOrProperty(float)=1.0):
	return (np.random.rand(params.samples) * 2.0 - 1.0) * amplitude
	
@registerFunction
def fromWaveFile(params:SynthParameters=None, filename:str="testIn.wav", amplitude:StreamOrProperty(float)=1.0):
	with wave.open(filename) as file:
		if file.getnchannels() != 1:
			raise SynthException("Only files with one channel are supported.")
			return np.zeros(params.samples)
		else:
			n = file.getnframes()
			frames = file.readframes(n)
			
			sampTypes = {1: np.uint8, 2:np.int16, 4:np.int32}
			sampWidth = file.getsampwidth()
			if sampWidth not in sampTypes:
				raise SynthException("Only samplewidths of 1, 2 or 4 bytes are supported.")
			else:
				maxValue = 2**(sampWidth*8 - 1) - 1
				data = np.fromstring(frames, dtype = sampTypes[sampWidth]).astype(StreamOrProperty(float)) / maxValue
				if n > params.samples:
					data = data[:params.samples]
				elif n < params.samples:
					data = np.concatenate((data, np.zeros(params.samples - n)), axis = 0)
				
				# sample rate conversion
				rate = file.getframerate()
				if rate != params.sampleRate:
					x = np.linspace(0.0, n / rate, n)
					nx = np.linspace(0.0, params.length, params.samples)
					interpolator = interp1d(x, data)
					data = interpolator(nx)
					
				return data

	
# effects
	
@registerFunction
def constant(params:SynthParameters=None, constant:StreamOrProperty(float)=1.0):
	ret = np.ndarray(params.samples)
	ret.fill(constant)
	return ret
	
@registerFunction
def add(signalA:StreamOnly(np.ndarray)=0.0, signalB:StreamOnly(np.ndarray)=0.0):
	return signalA + signalB
	
@registerFunction
def multiply(signalA:StreamOnly(np.ndarray)=0.0, signalB:StreamOnly(np.ndarray)=0.0):
	return signalA * signalB
	
@registerFunction
def clamp(channel:StreamOnly(np.ndarray)=0.0, level:StreamOrProperty(float)=1.0):
	return np.clip(channel, -level, level)
	
@registerFunction
def mix(channelA:StreamOnly(np.ndarray)=0.0, channelB:StreamOnly(np.ndarray)=0.0, mixValue:StreamOrProperty(float)=0.5):
	return (channelA*(1-mixValue) + channelB*mixValue)
	
@registerFunction
def mix2(channelA:StreamOnly(np.ndarray)=0.0, channelB:StreamOnly(np.ndarray)=0.0, mixA:StreamOrProperty(float)=0.5, mixB:StreamOrProperty(float)=0.5):
	return (channelA*mixA + channelB*mixB)
	
@registerFunction
def delay(params:SynthParameters=None, signal:StreamOnly(np.ndarray)=0.0, delayTime:StreamOrProperty(float)=0.1):
	zeroLen = int(delayTime * params.sampleRate)
	return np.append(np.zeros(zeroLen), signal[zeroLen:params.samples])
	
#cheapReverb, exponential