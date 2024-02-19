#!/usr/bin/env python3
import cv2
import numpy as np

cap = cv2.VideoCapture(0) # 0은 기본 웹캠, 다른 카메라면 인덱스 바꾸면 됨

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

src_points = np.array([[0,0],[640,0],[640,480],[0,480]], dtype=np.float32)
dst_points = np.array([[320,0],[320,480],[960,480],[960,0]], dtype=np.float32)
M = cv2.getPerspectiveTransform(src_points, dst_points)

while True:
    ret, frame = cap.read() #ret은 성공 여부를 나타내는 부울 값
    # frame은 캡쳐된 카메라 프레임(화면)


    # failed occur
    if not ret:
        print("Failed") 
        break

    cv2.imshow('Video', frame) #Frame이라는 창 이름, frame을 보여줌
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0) #이미지,커널사이즈,표준편차

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0,0,180), (255,255,255))

    edge = cv2.Canny(blur,150,200,5)
    edge2 = cv2.Canny(mask, 150,200,5)

    bev = cv2.warpPerspective(frame, M, (1280, 720))
    #cv2.imshow('filter', mask)
    cv2.imshow('Canny', edge) #Frame이라는 창 이름, frame을 보여줌
    cv2.imshow('BEV', bev)
    #cv2.imshow('Canny2', edge2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break; # 'q' 누르면 종료

cap.release()
cv2.destroyAllWindows()