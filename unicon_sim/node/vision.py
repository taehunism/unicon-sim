#!usr/bin/env python3
# -*- coding:utf-8 -*-

import rospy
import numpy as np
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image


class Unicon_CV():
    def __init__(self):
        self.camera_sub = rospy.Subscriber("/camera/rgb/image_raw", Image, self.camera_callback)
        self.bridge = CvBridge() 

    def camera_callback(self,data):
        try:
            # ROS 이미지 메시지를 OpenCV 이미지로 변환
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            
            # 여기에 이미지 처리 및 차선 인식 알고리즘을 적용

            #src_points = np.array([[0,0],[640,0],[640,480],[0,480]], dtype=np.float32)
            #dst_points = np.array([[320,0],[320,480],[960,480],[960,0]], dtype=np.float32)
            #M = cv2.getPerspectiveTransform(src_points, dst_points)

            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray,(5,5),0) #이미지,커널사이즈,표준편차

            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, (0,0,180), (255,255,255))

            edge = cv2.Canny(blur,150,200,5)
            edge2 = cv2.Canny(mask, 150,200,5)

            #bev = cv2.warpPerspective(frame, M, (1280, 720))
            #cv2.imshow('filter', mask)
                    
            cv2.imshow('Video', cv_image) #Frame이라는 창 이름, frame을 보여줌
            cv2.imshow('Canny', edge) #Frame이라는 창 이름, frame을 보여줌qqqqq
            #cv2.imshow('BEV', bev)
            #cv2.imshow('Canny2', edge2)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                rospy.signal_shutdown("User exit with 'q' key")  # Shutdown ROS node
                cv2.destroyAllWindows()  # Close OpenCV windows
                return

        except CvBridgeError as e:
            print(e)

    def main(self):
        rospy.spin()


if __name__ == "__main__":
    try:
        rospy.init_node("unicon_cv")
        unicon_cv = Unicon_CV()
        unicon_cv.main()
        
    except KeyboardInterrupt:
        print("sorry. don't execute")