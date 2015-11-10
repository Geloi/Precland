import sys
if '/usr/bin' in sys.path:
	sys.path.remove('/usr/bin')
import usb.core, usb.util
import numpy as np
import struct


#Make the PX4Flow sensor behave as a webcam
#Thanks to Kevin Mehall for his contribution
class FlowCamera():
	def __init__(self):
		#consts
		self.SIZE = 352
		self.HEADER_SIZE = 16
		self.READ_SIZE = self.HEADER_SIZE + self.SIZE*self.SIZE

		self.timestamp = 0
		self.distance_mm = 0
		self.exposure = 0

		#create image
		image = np.zeros((self.SIZE, self.SIZE), dtype='uint8')

		#open connection
		self.dev, self.endpoint = None, None
		try:
			self.dev = usb.core.find(idVendor=0x26ac, idProduct=0x0015)
			self.endpoint = self.dev[0][(2,0)][0]
		except:
			pass

	def isOpened(self):
		return (self.dev is not None) and (self.endpoint is not None)

	def read(self):
		#read from USB
		data = self.endpoint.read(64 * (1 + (self.READ_SIZE) / 64), timeout=2000)
		ret = None

		#check for full data transfer
		if len(data) == self.READ_SIZE:
			(self.timestamp, self.exposure, self.distance_mm) = struct.unpack('<QII', data[:self.HEADER_SIZE])
			image = np.frombuffer(data[self.HEADER_SIZE:], dtype='uint8').reshape(self.SIZE, self.SIZE)
			ret = True

		else:
			image = np.zeros((self.SIZE, self.SIZE), dtype='uint8')
			ret = False

		return (ret, image)

	def get_timestamp(self):
		return self.timestamp

	def get_lidar(self):
		return self.distance_mm /1000.0




if __name__ == "__main__":
	import cv2
	# create a single global object
	flow_cam = Flow_Camera()
	if flow_cam.isOpened():

		while True:
			ret , img = flow_cam.read()
			cv2.imshow("flow",img)
			cv2.waitKey(1)
	else:
		print "No camera found!!"
