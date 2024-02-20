import rospy
import numpy as np
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

class Unicon_CV():
    def __init__(self):
        self.camera_sub = rospy.Subscriber("/camera/rgb/image_raw", Image, self.camera_callback)
        self.bridge = CvBridge()

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
            #init_velue=[0,0]
            #matrix_zeros = [[init_velue[:] for j in range(32)] for i in range(10)]
            matrix_zeros = np.zeros((10, 32, 2), dtype=int)

            for i in range(10): # line 
                yy = 460 - (i + 1) * 9  # 9간격으로 위로 이동
                for j in range(32):  # 최대로 가로 개수를 늘림
                    #area = img[yy:yy+5, j*20:(j+1)*20]
                    white_pixels = cv2.countNonZero(mask_white[yy:yy+5, j*20:(j+1)*20])
                    yellow_pixels = cv2.countNonZero(mask_yellow[yy:yy+10, j*20:(j+1)*20]) 

                    if white_pixels > 30:  
                        image[yy:yy+4, j*20:(j+1)*20] = [0, 0, 255]  # 
                        matrix_zeros[i][j]=[(j+1)*10,yy+2]
                        
                    elif yellow_pixels > 80: 
                        image[yy:yy+4, j*20:(j+1)*20] = [255, 0, 0]  
                        matrix_zeros[i][j]=[(j+1)*10,yy+2]

            non_zero_values = matrix_zeros[np.all(matrix_zeros != [0, 0], axis=-1)]
            print(non_zero_values)
            
            #non_zero_list = non_zero_values.tolist()
            #print(non_zero_list)
            
            #print(matrix_zeros)
            #mask = cv2.inRange(hsv, (0, 0, 180), (255, 255, 255))
            #edge = cv2.Canny(blur, 100, 200, 5)
            
            #cv2.imshow('yellow',mask_yellow)
            #cv2.imshow('white', mask_white)
            #cv2.imshow('Canny', edge)
            cv2.imshow('Video', image)


            if cv2.waitKey(1) & 0xFF == ord('q'):
                rospy.signal_shutdown("User exit with 'q' key")  
                cv2.destroyAllWindows()  
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