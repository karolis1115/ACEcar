import os
import sys
#sys.path.append('/usr/local/lib/python3.9/site-packages')
import cv2
import numpy as np
#print(cv2.getBuildInformation())


########################MAIN##############################


##############to be used with Gstreamer library#######################
#cap = cv2.VideoCapture('videotestsrc ! videoconvert ! appsink sync=false',cv2.CAP_GSTREAMER) #gstreamer test source
cap = cv2.VideoCapture('souphttpsrc location=http://raspberrypi.local:8080/?action=stream ! decodebin ! videoconvert ! sync=false',cv2.CAP_GSTREAMER)
###################Only needs base opencv library#############################
cap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')
while (True):
    Ret,frame = cap.read()
    if not Ret:
        #print("no valid frame")
        break
    cv2.imshow("Output", frame)
    cv2.waitKey(5)

cap.release()
cv2.destroyAllWindows()