from threading import Semaphore

import pyaudio
import numpy as np

import sys

_pA = None
_stream = None
_playQueue = b""
_playQueueSemaphore = Semaphore()

def streamCallback(input, frame_count, time_info, status_flags):
	global _playQueue
	
	frame_count *= 4 # convert frames to bytes
	
	with _playQueueSemaphore:
		l = len(_playQueue)
		playBuf = None
		if l <= frame_count:
			playBuf = _playQueue[:l] + b"\x00"*(frame_count - l)
			_playQueue = b""
		else:
			playBuf = _playQueue[:frame_count]
			_playQueue = _playQueue[frame_count:]
		
	return (playBuf, pyaudio.paContinue)

def reinitAudio(sampleRate):
	global _pA, _stream
	
	if _pA:
		_stream.stop_stream()
		_stream.close()
		_pA.terminate()

	_pA = pyaudio.PyAudio()
	_stream = _pA.open(channels = 1, rate = sampleRate, output = True, format = pyaudio.paFloat32, stream_callback = streamCallback)
	_stream.start_stream()

def play(buffer):
	global _playQueue
	
	with _playQueueSemaphore:
		_playQueue += buffer.astype(np.float32).tobytes()
