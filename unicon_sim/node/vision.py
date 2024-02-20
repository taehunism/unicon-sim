import rospy
import numpy as np
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

class Unicon_CV():
    def __init__(self):
        self.camera_sub = rospy.Subscriber("/camera/rgb/image_raw", Image, self.camera_callback)
        self.bridge = CvBridge()

        # 사용자가 선택한 점의 좌표 초기화
        self.selected_points = []

    def camera_callback(self, data):
        try:
            cv_image_raw = self.bridge.imgmsg_to_cv2(data, "bgr8")
            cv_image = cv_image_raw[0:640][240:480]

            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)  

            hsv = cv2.cvtColor(cv_image_raw, cv2.COLOR_BGR2HSV)

            # 흰색에 대한 HSV 범위
            lower_white = np.array([0, 0, 180])
            upper_white = np.array([255, 30, 255])

            # 노란색에 대한 HSV 범위
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([30, 255, 255])

            mask_white = cv2.inRange(hsv, lower_white, upper_white)
            mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

            img = cv2.bitwise_or(mask_white, mask_yellow)

            xx = 20  
            image = cv_image_raw.copy()  

            for i in range(15):
                yy = 460 - (i + 1) * 9  
                for j in range(32):  
                    area = img[yy:yy+5, j*20:(j+1)*20]
                    white_pixels = cv2.countNonZero(area)
                    yellow_pixels = cv2.countNonZero(mask_yellow[yy:yy+10, j*20:(j+1)*20]) 

                    if white_pixels > 30:  
                        image[yy:yy+5, j*20:(j+1)*20] = [0, 0, 255]  
                        print(white_pixels)
                    elif yellow_pixels > 80: 
                        image[yy:yy+5, j*20:(j+1)*20] = [0, 0, 255]  

            mask = cv2.inRange(hsv, (0, 0, 180), (255, 255, 255))
            edge = cv2.Canny(blur, 100, 200, 5)

            cv2.imshow('filter', mask)
            cv2.imshow('Video', image)
            cv2.imshow('Canny', edge)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                if len(self.selected_points) == 4:
                    transformed_image = self.birds_eye_view(cv_image)
                    cv2.imshow("Bird's Eye View", transformed_image)

                rospy.signal_shutdown("User exit with 'q' key")  
                cv2.destroyAllWindows()  
                return

            if len(self.selected_points) < 4:
                cv2.imshow('Video', cv_image)
                cv2.setMouseCallback('Video', self.mouse_callback)
            else:
                # 네 개의 점이 선택되면 원근 변환을 수행
                transformed_image = self.birds_eye_view(cv_image)
                cv2.imshow("Bird's Eye View", transformed_image)

        except CvBridgeError as e:
            print(e)

    def mouse_callback(self, event, x, y, flags, param):
        # 마우스 왼쪽 버튼 클릭 시 좌표를 저장
        if event == cv2.EVENT_LBUTTONDOWN:
            self.selected_points.append((x, y))
            print(f"Selected Points: {self.selected_points}")

    def birds_eye_view(self, image):
        # 사용자가 선택한 점의 좌표
        src_points = np.float32(self.selected_points)
        
        # 변환 후 좌표
        dst_points = np.float32([[0, 0], [400, 0], [400, 600], [0, 600]])

        # 변환 행렬 계산
        perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

        # 원근 변환 적용
        transformed_image = cv2.warpPerspective(image, perspective_matrix, (400, 600))

        return transformed_image

    def main(self):
        rospy.spin()

if __name__ == "__main__":
    try:
        rospy.init_node("unicon_cv")
        unicon_cv = Unicon_CV()
        unicon_cv.main()

    except KeyboardInterrupt:
        print("Sorry, don't execute.")
