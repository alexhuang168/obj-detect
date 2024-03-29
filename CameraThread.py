import threading
import time
import cv2
import jetson.inference
import jetson.utils

class CSI_Camera:

	def __init__ (self, stream) :
		self.video_capture = None #OpenCV reference
		#self.uri = jetson.utils.videoSource(stream) # jetson.utils reference
        
		# Last frame captured from the camera
		self.frame = None
		self.grabbed = False
		self.img = None
        
		# Thread that runs video capture
		self.read_thread = None
		self.read_lock = threading.Lock()
		self.running = False


	def open(self, gstreamer_pipeline_string):
		try:
			self.video_capture = cv2.VideoCapture(
				gstreamer_pipeline_string, cv2.CAP_GSTREAMER
			)
            
		except RuntimeError:
			self.video_capture = None
			print("Unable to open camera")
			print("Pipeline: " + gstreamer_pipeline_string)
			return
		# Grab the first frame to start the video capturing
		self.grabbed, self.frame = self.video_capture.read()

	def start(self):
		if self.running:
			print('Video capturing is already running')
			return None
		# create a thread to read the camera image
		if self.video_capture != None:
			self.running = True
			self.read_thread = threading.Thread(target=self.updateCamera)
			self.read_thread.start()
		return self

		def stop(self):
			self.running=False
			self.read_thread.join()

	def updateCamera(self):
		# This is the thread to read images from the camera
		while self.running:
			try:
				grabbed, frame = self.video_capture.read()
				with self.read_lock:
					self.grabbed = grabbed
					self.frame = frame
					self.img = jetson.utils.cudaFromNumpy(frame)
			except RuntimeError:
				print("Could not read image from camera")
				# FIX ME - stop and cleanup thread
				# Something bad happened
        

	def read(self):
		with self.read_lock:
			frame = self.frame.copy()
			grabbed = self.grabbed
			image = self.img
		return image #grabbed

	def release(self):
		if self.video_capture != None:
			self.video_capture.release()
			self.video_capture = None
		# Now kill the thread
		if self.read_thread != None:
			self.read_thread.join()
