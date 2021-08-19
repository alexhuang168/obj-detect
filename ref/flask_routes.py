from flask import Flask, request
from flask_restful import Resource, Api
#from dsrDetection import Camera
from threading import Thread
import jetson.inference
import jetson.utils

#api = Api(app)

# Assign camera streams
print("111111111111111111111111111111111111111111111")
#left_camera = Camera("left", "csi://0")
#p1 = Thread(target = left_camera.start())
#right_camera = Camera("right", "csi://1")

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

class Camera:
	def __init__(self, cameraLocation, videoSource):
		print("CREATED")
		self.side = cameraLocation
		self.uri = jetson.utils.videoSource(videoSource)
		#self.display = jetson.utils.videoOutput("display://0")		
		
		self.running = False
	
	def start(self):
		print("RUNNING")
		self.running = True
		while self.running:
			img = self.uri.Capture()
			detections = net.Detect(img)
			for detection in detections:
				if detection.ClassID == 1:
					print(self.side + " camera. Person detected")


app = Flask(__name__)

@app.route('/')
def main():
	return {"application": "dsr-detection"}

@app.route('/status')
def state():
	return {"left_cam": left_camera.running}

@app.route('/detections')
def results():
	return {"objects": "123"}


left_camera = Camera("left", "csi://0")
p1 = Thread(target = left_camera.start())

""" Main """
if __name__ == "__main__":
	
	p0 = Thread(target = app.run(debug=True, use_reloader=False))

	#p2 = Thread(target = app.run(port=3000, debug=False, host='0.0.0.0', use_reloader=False))
	
	#p1 = Thread(target = left_camera.start())
	#p2 = Thread(target = right_camera.run())
	p0.start()
	p1.start()
	#p2.start()
	
