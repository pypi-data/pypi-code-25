import time
import random
#from PIL import Image,ImageFilter,ImageOps,ImageChops,ImageDraw,ImageFont
import string
import os
import sys
import cv2
import matplotlib
import numpy as np
from collections import defaultdict

def resource_path(relative_path):
	return os.path.join(os.path.dirname(__file__), relative_path)


def outer_path(relative_path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath("..")
	return os.path.join(base_path, relative_path)

def id_generator(size=24):
	chars=string.ascii_uppercase.lower()*2+string.ascii_uppercase+string.digits*3
	return ''.join(random.choice(chars) for _ in range(size))


#index_file = open("index.txt","w+")
three_days = 3*24*60*60
hashlist = defaultdict(lambda: 0)
def run_jo():
	narrative_file = open(resource_path("narrative.txt"),"r")
	narrative = narrative_file.readlines()
	narrative_file.close()
	narrative_index = 0
	print("Jo v0.1.0")
	print("Copyright John Lhota 2018.")
	print("Welcome to Jo, an experiment in digital narrative.")
	print("When prompted, enter a full path to an image file")
	print("on your computer. This file will be sacrificed.")
	print("-Do not submit the same image more than once.")
	print("-Do not submit GIFs.")
	print("")
	while True:
		t = time.time()
		if t % 12 == 0:
			greeting = "The portal is open. Please enter a sacrifice."
			fname = raw_input(greeting).strip()

			if time.time() > t + 45:
				print("Sorry, portal has closed.")
				time.sleep(2)
				continue

			if ".gif" in fname:
				print("Do not submit GIFs.")
				continue
			img = cv2.imread(fname)
			gray = cv2.imread(fname, 0)
			os.remove(fname)
			key = hash(str(img))
			hashlist[key] += 1

			if hashlist[key] >= 3 and hashlist[key] < 5:
				print("Do not submit the same image more than once.")

			if hashlist[key] > 8:
				continue

			faceCascade = cv2.CascadeClassifier(resource_path("haarcascade_frontalface_alt.xml"))
			#eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')


			faces = faceCascade.detectMultiScale(gray, 1.3, 5)
			#print "Found {0} faces!".format(len(faces))

			# Draw a rectangle around the faces
			for (x, y, w, h) in faces:
			    #cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
			    #draw black scribbles in rect
			    pts = []
			    dir = random.randint(0,1)
			    for i in range(1,10):
			    	i2 = i+1
			    	if i % 2 == dir:
			    		cv2.line(img, (x + w/10, y + h*i/10), (x + w*9/10, y + h*(i+1)/10), (0,0,0), 4)
			    	else:
			    		cv2.line(img, (x + w*9/10, y + h*i/10), (x + w/10, y + h*(i+1)/10), (0,0,0), 4)
			    cv2.polylines(img, pts, False, (0,0,0), 5)

			kernel = np.ones((5,5),np.uint8)
			img = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)

			w = np.size(img, 1)
			h = np.size(img, 0)
			for row in range(0,h):
			    	if random.randint(0,5)==0:
				    	shift = (random.randint(0,4)-2)
				    	print(shift)
				    	for col in range(0, w):
				    		img[row][col] = img[row][(col+shift) % w]

			if np.size(img, 1) < np.size(img, 0) and random.randint(0,2) == 0:
				img = cv2.resize(img, (0,0), fx=2,fy=1)

			line = narrative[narrative_index]
				
			if random.randint(0,1)==0:
				shift = random.randint(0, len(line))
				line = line[shift:] + line[:shift]

			if hashlist[key] > 5:
				line = "Do not submit the same image more than once."

			if random.randint(0,5) > 1:
				narrative_index += 1
			elif random.randint(0,3)==0:
				narrative_index += 2
			elif random.randint(0,2)>0:
				narrative_index -=2
			narrative_index = max(0, narrative_index)
			narrative_index = narrative_index % np.size(narrative)


			img = np.int16(img)  

			contrast   = 140
			brightness = -80

			img = img*(contrast/127 + 1) - contrast + brightness

			blur = cv2.medianBlur(img,5)
			cv2.addWeighted(img, 4, blur, -3, 0, img)

			# we now have an image that has been adjusted for brightness and
			# contrast, but we need to clip values not in the range 0 to 255
			img = np.clip(img, 0, 255)  # force all values to be between 0 and 255

			# finally, convert image back to unsigned 8 bit integer
			img = np.uint8(img)

			for x in range(0,h):
				for y in range(0, w):
					img[x][y][0] = (img[x][y][0] + 20) % 255
					im2 = img[x][y][2]
					img[x][y][2] = (img[x][y][1] + 20) % 255
					img[x][y][1] = (im2 + 20) % 255
					


			# draw.text((x, y),"Sample Text",(r,g,b))
			font=cv2.FONT_HERSHEY_COMPLEX_SMALL
			ext = fname.split(".")[1]
			for y in range(0,h,15):
				cv2.putText(img, line, (w/2-1,y+4), font, 0.8, (0,0,0), 2, cv2.LINE_AA)
				if random.randint(0,2)>0:
					cv2.putText(img, line, (w/2,y), font, 0.8, (0,0,255), 2, cv2.LINE_AA)
			
			time.sleep(4)
			enclosing = ""
			path = fname.split("/")
			for i in range(len(path)-1):
				enclosing += "/" + path[i]
			cv2.imwrite(enclosing + "/" + id_generator() + "." + ext, img)