import io
import os
import pyaudio
import wave
import serial
import syslog
import time

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


#print('Credendtials from environ: {}'.format(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))

#port = '/dev/ttyACM0'
port = '/dev/serial/by-id/usb-Intel_ARDUINO_101_AE6642EK61900V0-if00'
ard = serial.Serial(port,9600,timeout=5)

FORMAT = pyaudio.paInt16

CHANNELS = 1
RATE = 16000
CHUNK = int(RATE / 10)
RECORD_SECONDS = 3


while True:
	# start Recording
	audio1 = pyaudio.PyAudio()
	stream = audio1.open(format=FORMAT, channels=CHANNELS,rate=RATE, input=True,frames_per_buffer=CHUNK)
	print "recording..."
	frames = []

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	    data = stream.read(CHUNK)
	    frames.append(data)
	print "finished recording"


	# stop Recording
	stream.stop_stream()
	stream.close()
	audio1.terminate()


	file = open("newfile.raw", "w")
	file.write(b''.join(frames))
	file.close()

	client = speech.SpeechClient()

	with io.open('newfile.raw', 'rb') as audio_file:
	    content = audio_file.read()
	    audio = types.RecognitionAudio(content=content)

	config = types.RecognitionConfig(encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16, sample_rate_hertz=16000, language_code='en-US')

	response = client.recognize(config, audio)

	for result in response.results:
		print('Transcript: {}'.format(result.alternatives[0].transcript))
		if result.alternatives[0].transcript == "lights on":
			s = "1"
		elif result.alternatives[0].transcript == "orange":
			s = "2"
		elif result.alternatives[0].transcript == "kitchen":
			s = "3"
		else:
			s = '4'
			print("ERROR!")
		print(s)
		ard.write(s)
		time.sleep(4)
		print('Sent')
		recv = ard.read()
		print("\nRecieved: ")
		print(recv)


