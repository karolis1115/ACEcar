import cv2
import numpy as np


#cap = cv2.VideoCapture('vid1.mp4')
cap = cv2.VideoCapture('http://acecar.local:8080/?action=stream') #For live video
cap.set(3, 160)
cap.set(4, 120)


while True:
    ret, frame = cap.read()

    low_b = np.uint8([255, 255, 255])  # color of background

    high_b = np.uint8([80, 80, 150])
    mask = cv2.inRange(frame, high_b, low_b)

    contours, hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            print("CX: " + str(cx) + " CY:" + str(cy))
            if cx >= 1200:
                print("Turn Left")
            if cx < 1200 and cx > 1000:  # NEED TO CHANGE VALUES DEPENDS OF CAMERA
                print("On track")
            if cx <= 1100:
                print("Turn Right")
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

    cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)
    cv2.imshow("Mask", mask)
    cv2.imshow("Grame", frame)
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xff == ord('q'):  # 1 is the time in ms
        break
cap.release()
cv2.destroyAllWindows()
