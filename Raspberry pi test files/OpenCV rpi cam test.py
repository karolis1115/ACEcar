import os
import sys
sys.path.append('/usr/local/lib/python3.9/site-packages') #linuxx
#os.add_dll_directory(r"C:/opencv/gst/1.0/msvc_x86_64/bin") #windows
import cv2
import numpy as np
import codecs
#print(cv2.getBuildInformation())



########################MAIN##############################
cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 426)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
dim = (426,240)
while (True):
    Ret,frame = cap.read()
    if not Ret:
        print("no valid frame")
        break

    markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(frame, dictionary, parameters=parameters)
    frame = cv2.resize(frame,dim)
    cv2.imshow("yeets", frame)
    cv2.waitKey(0)

cap.release()
cv2.destroyAllWindows()

