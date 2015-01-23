import pyaudio
import numpy as np
import sys
import time

_pA = None
_streams = []
		
def initAudio():
	global _pA
	_pA = pyaudio.PyAudio()
	
def getCallback(sound):
	buffer = (sound*32767).astype(np.int16).tobytes()[:]
	cursor = 0
	def streamCallback(input, frameCount, timeInfo, statusFlags):
		nonlocal cursor
		nonlocal buffer
	
		bytesCount = 2*frameCount 
		playBuf = buffer[cursor:]
		cursor += bytesCount
		
		if len(playBuf) < bytesCount:
			data = playBuf + b"\x00"*(bytesCount - len(playBuf))
			task = pyaudio.paComplete
		else:
			data = playBuf[:bytesCount]
			task = pyaudio.paContinue

		assert(len(data) == bytesCount)
		return (data, task)
		
	return streamCallback
	
def play(buffer, sampleRate):
	stream = _pA.open(channels=1, rate=sampleRate, output=True, format=pyaudio.paInt16, stream_callback=getCallback(buffer))
	stream.start_stream()
	
	_streams.append(stream)
	
	for stream in _streams:
		if not stream.is_active():
			stream.stop_stream()
			stream.close()
			_streams.remove(stream)
			del stream
