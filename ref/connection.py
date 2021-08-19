import jetson.inference
import jetson.utils

from flask import Flask
from flask_socketio import SocketIO, emit
import threading

# Object Detection model to be used for the program
net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

"""
app = Flask(__name__)
socketio = SocketIO(app)

thread = Thread()
thread_stop_event = Event()
"""

class Camera:
	def __init__(self, location):
		self.uri = None
		self.side = location
		self.img = None
		self.read_thread = None
		self.read_lock = threading.Lock()
		self.running = False

	def open(self, stream):
		try:
			self.uri = jetson.utils.videoSource(stream)
			test_img = self.uri.Capture()
		except RuntimeError:
			self.uri = None
			print("Unable to open the camera")
			return

	def start(self):
		if self.running:
			print("Video capture already in progress")
			return None
		if self.uri != None:
			self.running = True
			self.read_thread = threading.Thread(target=self.updateCamera)
			self.read_thread.start()
		return self

	def stop(self):
		self.running = False
		self.read_thread.join()

	def updateCamera(self):
		# Thread that reads images from the camera
		while self.running:
			try:
				frame = self.uri.Capture()
				with self.read_lock:
					self.img = frame


			except RuntimeError:
				print("Could not read the image")

	def read(self):
		with self.read_lock:
			img = self.uri.Capture()
		return img

	def release(self):
		if self.uri != None:
			self.uri.release()
			self.uri = None
		# Kill the thread
		if self.read_thread != None:
			self.read_thread.join()

def start_cameras():
	left_camera = Camera("left")
	left_camera.open("csi://0")
	left_camera.start()

	right_camera = Camera("right")
	right_camera.open("csi://1")
	right_camera.start()

	if (not left_camera.running or not right_camera.running):
		print("Unable to open one of the cameras")
		SystemExit(0)

	while True:
		left_cam = left_camera.read()
		right_cam = right_camera.read()
		
		detections_left = net.Detect(left_cam)
		detections_right = net.Detect(right_cam)

		for detection_l in detections_left:
			if detection_l.ClassID == 1:
				print("Person detected left")

		for detection_r in detections_right:
			if detection_r.ClassID == 1:
				print("Person detected right")


		if KeyboardInterrupt:
			break
		
		left_camera.stop()
		left_camera.release()
		
		right_camera.stop()
		right_camera.release()

"""	
	while True:
		img = self.uri.Capture()
		detections = net.Detect(img)
		for detection in detections:
			if detection.ClassID == 1:
				socketio.emit("detection", "person")



@app.route('/')
def index():
	return {"application": "dsr-detection"}

@socketio.on('connect', namespace='/test')
def test_connection():
	global thread
	print("Client connected")
	
	if not thread.isAlive():
		print("Starting Thread")
		thread = socketio.start_background_task(connectCameras)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

@socketio.on('detection', namespace='/detections')
def display_detection(value):
	return {"data": value}
"""

if __name__ == '__main__':
	#socketio.run(app)
	start_cameras()







