import cv2
class VideoCamera(object):
	def __init__(self):
		self.video=cv2.VideoCapture(0)
		self.video.set(3,300)
		self.video.set(4,400)
		
	def __del__(self):
		self.video.release()
	def get_frame(self):
		success,image=self.video.read()
		return image
