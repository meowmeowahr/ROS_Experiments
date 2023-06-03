#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

import time
import cv2


bridge = CvBridge()

def start_node():
    rospy.init_node('image_pub')
    rospy.loginfo('image_pub node started')
    print(rospy.get_published_topics())


def image_callback(msg):
    print("Got image", time.time())

    try:
        # Convert your ROS Image message to OpenCV2
        cv2_img = bridge.imgmsg_to_cv2(msg, "bgr8")
        cv2_img = cv2.putText(cv2_img, "/camera/image_raw", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("camera", cv2_img)
        cv2.waitKey(20)
    except CvBridgeError as e:
        print(e)

if __name__ == '__main__':
    try:
        start_node()
        rospy.Subscriber("/camera/image_raw", Image, image_callback)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
