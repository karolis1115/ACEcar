import sys
sys.path.append('/usr/local/lib/python3.9/site-packages')
import cv2
cam = cv2.VideoCapture(0)
size = (480, 360)
while True:
	ret, image = cam.read()
	image = cv2.resize(image, size)
	cv2.imshow('Imagetest',image)
	k = cv2.waitKey(1)
	if k != -1:
		break
cam.release()
cv2.destroyAllWindows()
