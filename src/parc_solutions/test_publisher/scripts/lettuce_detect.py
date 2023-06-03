#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

import cv2
import numpy as np

bridge = CvBridge()

def start_node():
    rospy.init_node('image_pub')
    rospy.loginfo('image_pub node started')
    print(rospy.get_published_topics())


def image_callback_l(msg):
    print("Got Left")
    global left_image

    try:
        # Convert your ROS Image message to OpenCV2
        left_image = bridge.imgmsg_to_cv2(msg, "bgr8")
        left_image = cv2.rotate(left_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    except CvBridgeError as e:
        print(e)

def image_callback_r(msg):
    print("Got Right")
    global right_raw_image

    try:
        right_raw_image = bridge.imgmsg_to_cv2(msg, "bgr8")
        right_raw_image = cv2.rotate(right_raw_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        combined_image = cv2.hconcat([left_image, right_raw_image])

        # convert to hsv colorspace
        hsv = cv2.cvtColor(combined_image, cv2.COLOR_BGR2HSV)

        # lower bound and upper bound for Green color
        lower_bound = np.array([40, 10, 15])	 
        upper_bound = np.array([80, 255, 255])

        # find the colors within the boundaries
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        #define kernel size  
        kernel = np.ones((7,7),np.uint8)

        # Remove unnecessary noise from mask
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        cv2.imshow("mask", mask)
        cv2.imshow("raw_combined", combined_image)
        cv2.waitKey(20)
    except CvBridgeError as e:
        print(e)

if __name__ == '__main__':
    left_image = None
    right_raw_image = None

    try:
        start_node()
        rospy.Subscriber("/left_camera/image_raw", Image, image_callback_l)
        rospy.Subscriber("/right_camera/image_raw", Image, image_callback_r)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass