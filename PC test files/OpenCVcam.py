########### UNUSED CODE ################
#file = open("data.bin", "wb")
#file.close()
########################################
import os
import sys
#sys.path.append('/usr/local/lib/python3.8/site-packages')
os.add_dll_directory(r"C:/opencv/gst/1.0/msvc_x86_64/bin")
import cv2
from cv2 import aruco
import numpy as np
import codecs
#print(cv2.getBuildInformation())
'''
*pipeline works in command line but not in opencv
*gstreamer displays error that i have yet to determine the cause of
*possible problem with something other than the pipeline?
'''
########################MAIN##############################
dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters =  aruco.DetectorParameters_create()

cap = cv2.VideoCapture('fdsrc fd=0 ! h264parse ! avdec_h264 max-threads=1 skip-frame=(5) output-corrupt=true ! autovideoconvert ! autovideosink',cv2.CAP_GSTREAMER)
#cap = cv2.VideoCapture('fdsrc fd=0 ! h264parse ! avdec_h264  ! videoconvert ! appsink sync=false',cv2.CAP_GSTREAMER)
#cap = cv2.VideoCapture('filesrc location=dat.bin ! avdec_h264 max-threads=1 ! videoconvert ! appsink sync=false', cv2.CAP_GSTREAMER)
#cap = cv2.VideoCapture('filesrc location=dat.bin ! h264parse ! avdec_h264 ! videoconvert !queue !appsink sync=false eos=false', cv2.CAP_GSTREAMER)
#cap = cv2.VideoCapture('tcpclientsrc host=172.16.10.1 port=8888 ! videorate ! h264parse ! avdec_h264 ! videoconvert ! appsink sync=false',cv2.CAP_GSTREAMER)
#cap = cv2.VideoCapture('videotestsrc ! videoconvert ! appsink sync=false',cv2.CAP_GSTREAMER)
while (True):
    Mat,frame = cap.read()
    if not Mat:
        #print("no valid frame")
        continue
    markerCorners, markerIds, rejectedCandidates = aruco.detectMarkers(frame, dictionary, parameters=parameters)
    aruco.drawDetectedMarkers(frame, markerCorners, markerIds,borderColor=(0, 255, 0))
    aruco.drawDetectedMarkers(frame, rejectedCandidates, borderColor=(0, 0, 255))
    cv2.imshow("yeets", frame)
    cv2.waitKey(5)

#cap.release()
#cv2.destroyAllWindows()