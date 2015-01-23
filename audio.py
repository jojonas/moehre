import pyaudio
import numpy as np

_pA = None
		
def initAudio():
	global _pA
	_pA = pyaudio.PyAudio()
	
def getCallback(buffer):
	cursor = 0
	def streamCallback(input, frameCount, timeInfo, statusFlags):
		nonlocal cursor
		nonlocal buffer
	
		frameCount *= 4 # convert to bytes
		playBuf = buffer[cursor:]
		cursor += frameCount
		if len(playBuf) < frameCount:
			return (playBuf + b"\x00"*(frameCount - len(playBuf)), pyaudio.paComplete)
		else:
			return (playBuf[:frameCount], pyaudio.paContinue)
	return streamCallback
	
def play(buffer, sampleRate):
	stream = _pA.open(channels=1, rate=sampleRate, output=True, format=pyaudio.paFloat32, stream_callback=getCallback(buffer.astype(np.float32).tobytes()[:]))
	stream.start_stream()
