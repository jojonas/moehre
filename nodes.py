from decorators import *
from usernodes import *
from synth import SynthParameters
import numpy as np

@registerFunction
def sin(params:SynthParameters=None, frequencyShift:np.ndarray=0.0, frequency:float=440, amplitude:float=1.0):
	t = np.linspace(0.0, params.length, params.samples)
	return np.sin(2 * np.pi * frequency*t + frequencyShift)
	
#sawtooth, triangle, whistle, whiteNoise, rectangle (frequency, duty cycle)
#delay, cheapReverb
#mix
#step -> rectangle, linear, exponential, 