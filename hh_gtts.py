import io
import os
import time
from threading import Thread
import cv2                                         #video feed
import requests
import matplotlib.pyplot as plt
import vlc

from google.cloud import texttospeech as tts       #text-to-speech

from google.cloud import vision                    #text extraction
from google.cloud.vision import types

from PIL import Image                              #activity identification
from io import BytesIO
from pprint import pprint

texts_prev = []      #for text extraction
activity_prev = []   #for activity identification
c = 0

class custom_thread(Thread):
	def __init__(self, function):
		self.running = False
		self.function = function
		super(custom_thread,self).__init__()

	def start(self):
		self.running = True
		super(custom_thread,self).start()

	def run(self):
		while self.running:
			self.function()

	def stop(self):
		self.running = False


def text_extraction():
	global texts_prev
	global c
	with io.open('cam_img.jpg', 'rb') as image_file:
		content = image_file.read()
	# content = content.tobytes()
	client = vision.ImageAnnotatorClient()	
	image = vision.types.Image(content=content)
	response = client.text_detection(image=image)
	texts = response.text_annotations
	if (len(texts)!=0) and (texts[0].description not in texts_prev) and (c<10):
		print('\nText Extraction')
		try:
			print(texts[0].description)
			texts_prev.append(texts[0].description)
			input_txt = texts[0].description
			client = tts.TextToSpeechClient()
			txt = tts.types.SynthesisInput(text=input_txt)
			voice = tts.types.VoiceSelectionParams(language_code='en-US', ssml_gender = tts.enums.SsmlVoiceGender.FEMALE)
			config =  tts.types.AudioConfig(audio_encoding = tts.enums.AudioEncoding.MP3)
			res = client.synthesize_speech(txt, voice, config)
			# os.remove("output.mp3")
			with open('output1.mp3', 'wb') as out:
				out.write(res.audio_content)
				print('Audio content written to file "output1.mp3"')
				# p = vlc.MediaPlayer("output1.mp3")
				# p.play()
			c=c+1

		except:
			pass
	elif c>=10:
		texts_prev = []  
		c=0



def activity_identification():
	global activity_prev
	global c
	subscription_key = "d8f3b13c24b648469975ccda75e690ed"
	assert subscription_key
	vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/"
	analyze_url = vision_base_url + "analyze"
	image_path = "cam_img.jpg"
	image_data = open(image_path, "rb").read()
	headers= {'Ocp-Apim-Subscription-Key': subscription_key,'Content-Type': 'application/octet-stream'}
	params = {'visualFeatures': 'Categories,Description,Color'}
	response = requests.post(analyze_url, headers=headers, params=params, data=image_data)
	response.raise_for_status()

	analysis_first = response.json()
	image_caption = analysis_first["description"]["captions"][0]["text"].capitalize()
	if (image_caption not in activity_prev) and (c<10):
		print('\nActivity detection:')
		try:
			print(image_caption)
			activity_prev.append(image_caption)
			client = tts.TextToSpeechClient()
			txt = tts.types.SynthesisInput(text=image_caption)
			voice = tts.types.VoiceSelectionParams(language_code='en-US', ssml_gender = tts.enums.SsmlVoiceGender.FEMALE)
			config =  tts.types.AudioConfig(audio_encoding = tts.enums.AudioEncoding.MP3)
			res = client.synthesize_speech(txt, voice, config)
			# os.remove("output.mp3")
			with open('output2.mp3', 'wb') as out:
				out.write(res.audio_content)
				print('Audio content written to file "output2.mp3"')
				# p = vlc.MediaPlayer("output2.mp3")
				# p.play()
		except:
			pass
	elif c>=10:
		activity_prev = [] 
		c=0 

	image = Image.open(BytesIO(image_data))
	plt.imshow(image)
	plt.axis("off")
	_ = plt.title(image_caption, size="x-large", y=-0)


# def text_to_speech(input_txt):
# 	client = tts.TextToSpeechClient()
# 	txt = tts.types.SynthesisInput(text=input_txt)
# 	voice = tts.types.VoiceSelectionParams(language_code='en-US', ssml_gender = tts.enums.SsmlVoiceGender.FEMALE)
# 	config =  tts.types.AudioConfig(audio_encoding = tts.enums.AudioEncoding.MP3)
# 	res = client.synthesize_speech(txt, voice, config)
# 	# os.remove("output.mp3")
# 	with open('output.mp3', 'wb') as out:
# 		out.write(res.audio_content)
# 		print('Audio content written to file "output.mp3"')

	

camera = cv2.VideoCapture(0)
time.sleep(0.1)

while True:
	return_value, content = camera.read()
	cv2.imshow('image',content)
	cv2.waitKey(1)
	cv2.imwrite('cam_img.jpg',content)
	t1 = custom_thread(text_extraction)
	t2 = custom_thread(activity_identification)
	t1.start()
	t2.start()
	time.sleep(5)
	p = vlc.MediaPlayer("output1.mp3")
	p.play()
	time.sleep(3)
	q = vlc.MediaPlayer("output2.mp3")
	q.play()
	t1.stop()
	t2.stop()

cv2.destroyAllWindows()







