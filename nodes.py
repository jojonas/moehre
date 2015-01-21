from usernodes import *
from synth import SynthParameters, SynthBuffer
import numpy as np

@registerFunction
def sin(params:SynthParameters=None, frequencyShift:SynthBuffer=0.0, frequency:float=440, amplitude:float=1.0)
	buf = SynthBuffer([params.length, params.sampleRate)
	return np.sin(np.linspace(0.0, params.length, params.samples) + frequencyShift)
	
#sawtooth, triangle, whistle, whiteNoise, rectangle (frequency, duty cycle)
#delay, cheapReverb
#mix
#step -> rectangle, linear, exponential, 