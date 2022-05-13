import cv2
import numpy as np
#print(cv2.getBuildInformation())

########################MAIN##############################


#Opens capture source which is simply a url to the video stream
cap = cv2.VideoCapture('http://acecar.local:8080/?action=stream')

#keep updating the frame FoReVeR
while (True):
    Ret,frame = cap.read()
    if not Ret:
        print("no valid frame")
        break
    #show the video output
    cv2.imshow("Output", frame)
    #waitkey has to be >0 to automatically update frame
    cv2.waitKey(5)

#Cleanup
cap.release()
cv2.destroyAllWindows()

'''
Take video data -> detect line + obstacles + end -> follow line + avoid obstacles + stop at end
'''