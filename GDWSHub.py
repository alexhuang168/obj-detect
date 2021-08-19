import time
import logging
import sys
from threading import *
import requests
import json
sys.path.append("./")
from signalrcore.hub_connection_builder import HubConnectionBuilder


class GDWSHub(Thread):
	
	def login_function(self, url):
		resp = requests.post(url)
		return resp.text # Returns the token

	def connect(self, login_url):
		hub = HubConnectionBuilder()\
			.configure_logging(logging_level=logging.DEBUG)\
			.with_url(self.server_url, options={
				"access_token_factory": lambda: self.login_function(login_url),
				"verify_ssl": False
			}).with_automatic_reconnect({
				"type": "interval",
				"keep_alive_interval": 10,
				"intervals": [1, 3, 5, 6, 7, 87, 3]
			}).build()
		return hub

	def set_lambdas(self):
		self.hub_connection.on_open(lambda: print("Connection established successfully"))
		self.hub_connection.on_close(lambda: print("Connection closed"))
		#self.hub_connection.on("PIR", print)
		self.hub_connection.start()
		self.hub_connection.send("PIR", ["ComInitSuccess", "True"])
		self.running = True
		return True

	def run(self):
		print("Establishing hub connection")
		myUrl = "http://192.168.99.3:5000/token?&email=DsrUser@Global&password=P@ssw0rd2021"

		self.server_url = "http://192.168.99.3:5000/NumberHub"
		self.hub_connection = self.connect(myUrl)		
		setup = self.set_lambdas() #Should be True

		if setup:
			self.keep_alive()

	# Universal send message
	def send_command(self, msg1, msg2):
		self.hub_connection.send("PIR", [msg1, msg2])
		
	def keep_alive(self):
		while self.running:
			print("Loop...\n")
			self.send_command("ComInitSuccess", "True")
			time.sleep(5)


		


