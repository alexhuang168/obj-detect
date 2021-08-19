# GlobalDWS DSR Object Detection using Multiple Cameras
# Author: Keyan Fayaz

import threading
import jetson.inference
import jetson.utils

# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of each camera pane in the window on the screen

left_camera = None
right_camera = None

# Object Detection model to be used for the program
net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

class CSI_Camera:

	def __init__(self):
		self.stream = None
		self.img = None

		self.read_thread = None
		self.read_lock = threading.Lock()
		self.running = False

	def open(self, gstreamer_pipeline_string):
		try:
			self.stream = jetson.utils.videoSource(uri)
		except RuntimeError:
			self.stream = None
			return

		self.img = self.stream.Capture()

	def start(self):
		if self.running:
			print("Video capture already running")
			return None
		if self.stream != None:
			self.running = True
			self.read_thread = threading.Thread(target=self.updateCamera)
			self.read_thread.start()
		return self

	def stop(self):
		self.running = False
		self.read_thread.join()

	def updateCamera(self):
		while self.running:
			capture = self.stream.Capture()
			with self.read_lock:
				self.img = capture

	def read(self):
		with self.read_lock:
			image = self.img
		return image

	def release(self):
		if self.stream != None:
			self.stream.Close()
			self.stream = None
		# kill thread
		if self.read_thread != None:
			self.read_thread.join()

# Here we directly select sensor_mode 3 (1280x720, 59.9999 fps)
def gstreamer_pipeline(
    sensor_id=0,
    sensor_mode=3,
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d sensor-mode=%d ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            sensor_mode,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def start_cameras():
	left_camera = CSI_Camera()
	left_camera.open(
		gstreamer_pipeline(
			sensor_id=0,
			sensor_mode=3,
			flip_method=0,
			display_height=540,
			display_width=960,
		))
	left_camera.start()
	
	right_camera = CSI_Camera()
	right_camera.open(
		gstreamer_pipeline(
			sensor_id=0,
			sensor_mode=3,
			flip_method=0,
			display_height=540,
			display_width=960,
		))
	right_camera.start()
	
	if not left_camera.stream.IsStreaming() or not right_camera.stream.IsStreaming():

		print("Unable to open the cameras")
		SystemExit(0)

	while True:
		print("In loop")
		
		left_image = left_camera.read()
		right_image = right_camera.read()

		left_detections = net.Detect(left_image)
		right_detections = net.Detect(right_image)

		for detection in left_detections:
			if detection.ClassID == 1:
				print("Human detected left")
		
		for detection in right_detections:
			if detection.ClassID == 1:
				print("Human detected right")
		

		if KeyboardInterrupt:
			break

	left_camera.stop()
	left_camera.release()
	right_camera.stop()
	right_camera.release()

if __name__ == "__main__":
	start_cameras()


