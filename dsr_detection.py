# GlobalDWS - DSR Human Presence Detection
# Author: Keyan Fayaz
# November 2020

# Project runs on a Jetson Nano B01 and uses a combination of OpenCV and Jetson Nano Jetpack Deep Learning
# Jetson Utils github can be found at https://github.com/dusty-nv/jetson-inference/

# Class CSI Camera creates a camera reference on a thread and the main thread converts the image to CUDA memory, 

# detectNet documentation can be found here: https://rawgit.com/dusty-nv/jetson-inference/dev/docs/html/python/jetson.inference.html
# gstCamera and cudaMemory documentation found here: https://rawgit.com/dusty-nv/jetson-inference/dev/docs/html/python/jetson.utils.html
# Sample projects can be found here: https://github.com/dusty-nv/jetson-inference/blob/master/docs/detectnet-example-2.md and https://github.com/JetsonHacksNano/CSI-Camera (this guy has a lot of good video tutorials on CSI cameras on NVIDIA boards).

from GDWSHub import GDWSHub
from CameraThread import CSI_Camera as Camera

import cv2
import threading
import numpy as np
import jetson.inference
import jetson.utils
import time

left_camera = None
right_camera = None

detected = False
gdws_hub = None

# Object Detection model to be used for the program - can change the string here to use other models
net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

camera_error_string = "One or both of the cameras failed to start. Please check the camera cables or restart the device."

# Currently there are setting frame rate on CSI Camera on Nano through gstreamer
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

	left_camera = Camera("csi://0")
	left_camera.open(
		gstreamer_pipeline(
			sensor_id=0,
			sensor_mode=3,
			flip_method=0,
			display_height=540,
			display_width=960,
		)
	)
	left_camera.start()
	
	right_camera = Camera("csi://1")
	right_camera.open(
		gstreamer_pipeline(
			sensor_id=1,
			sensor_mode=3,
			flip_method=0,
			display_height=540,
			display_width=960,
		)
	)
	right_camera.start()

	cv2.namedWindow("CSI Cameras", cv2.WINDOW_AUTOSIZE)

	if (
		not left_camera.video_capture.isOpened()
		or not right_camera.video_capture.isOpened()
	):
		# Cameras did not open, or no camera attached

		print("Unable to open any cameras")
		gdws_hub.send_command("NanoErrors", camera_error_string)
		# TODO: Proper Cleanup
		SystemExit(0)


	while left_camera.running and right_camera.running:
		left_image = left_camera.read()
		right_image = right_camera.read()

		detected = False # Reset to False

		# Shows the cameras
		try:
			camera_images = np.hstack((left_image, right_image))
			cv2.imshow("CSI Cameras", camera_images)

			left_detections = net.Detect(left_image)
			right_detections = net.Detect(right_image)

			for l_detection in left_detections:
				if l_detection.ClassID == 1:
					detected = True

			for r_detection in right_detections:
				if r_detection.ClassID == 1:
					detected = True

		except Exception as error:
			gdws_hub.send_command("NanoErrors", camera_error_string)		
	

		if detected:
			print("Person detected\n")
			gdws_hub.send_command("PIRdetected", "True")
			time.sleep(1)
			gdws_hub.send_command("PIRdetected", "False")
			detected = False
		
		
		# This also acts as
		keyCode = cv2.waitKey(30) & 0xFF
		# Stop the program on the ESC key
		if keyCode == 27:
			break

	# Clean up
	left_camera.stop()
	left_camera.release()
	right_camera.stop()
	right_camera.release()
	cv2.destroyAllWindows()

if __name__ == "__main__":
	print("...Starting application...")
	
	gdws_hub = GDWSHub() # Thread subclass
	gdws_hub.start() # start the thread
		
	print("Starting Cameras")

	start_cameras()

