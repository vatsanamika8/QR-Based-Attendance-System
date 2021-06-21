import cv2
class VideoCameraMob(object):
	def __init__(self):
		self.video=cv2.VideoCapture("http://172.26.197.19:8080/video")		
	def __del__(self):
		self.video.release()
	def get_frame(self):
		success,image=self.video.read()
		return image
