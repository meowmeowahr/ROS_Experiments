#!/usr/bin/env python

"""
Kevin's Lettuce Detector
"""

import time

import cv2
import numpy as np
import rospy
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

bridge = CvBridge()

MIN_LETTUCE_AREA = 6000

ROBOT_WIDTH = 350
ROBOT_HEIGHT = 505
ROBOT_OFFSET_FROM_TOP = 12


def start_node():
    rospy.init_node('image_pub')
    rospy.loginfo('image_pub node started')


def image_callback_l(msg):
    print("Got Left", time.time())
    global left_raw_image

    try:
        # Convert your ROS Image message to OpenCV2
        left_raw_image = bridge.imgmsg_to_cv2(msg, "bgr8")
    except CvBridgeError as e:
        print(e)


def image_callback_r(msg):
    print("Got Right", time.time())
    global right_raw_image, last_frame_time

    fps = 1 / (time.time() - last_frame_time)
    last_frame_time = time.time()

    try:
        right_raw_image = bridge.imgmsg_to_cv2(msg, "bgr8")

        combined_image = cv2.hconcat([
            cv2.rotate(left_raw_image,
                       cv2.ROTATE_90_COUNTERCLOCKWISE),
            cv2.rotate(right_raw_image,
                       cv2.ROTATE_90_COUNTERCLOCKWISE)
            ])

        # convert to hsv colorspace
        hsv = cv2.cvtColor(combined_image, cv2.COLOR_BGR2HSV)

        # lower bound and upper bound for Green color
        lower_bound = np.array([40, 20, 20])
        upper_bound = np.array([80, 255, 255])

        # find the colors within the boundaries
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        # define kernel size
        kernel = np.ones((7, 7), np.uint8)

        # Remove unnecessary noise from mask
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Generate axis lines
        visual = mask.copy()
        visual = cv2.cvtColor(visual, cv2.COLOR_GRAY2BGR)

        # Generate robot
        visual = cv2.rectangle(visual,
                               (int(visual.shape[1] // 2 - ROBOT_WIDTH // 2),
                                int(visual.shape[0] // 2 - ROBOT_HEIGHT // 2)
                                + ROBOT_OFFSET_FROM_TOP),
                               (int(visual.shape[1] // 2 + ROBOT_WIDTH // 2),
                                int(visual.shape[0] // 2 + ROBOT_HEIGHT // 2)
                                + ROBOT_OFFSET_FROM_TOP), (0, 255, 0), 2)

        robot_top_center = (visual.shape[1] // 2,
                            int(visual.shape[0] // 2 - ROBOT_HEIGHT // 2)
                            + ROBOT_OFFSET_FROM_TOP)

        visual = cv2.circle(visual, robot_top_center, 10, (255, 255, 0), -1)

        # Find the contours on the binary image:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

        # Store bounding rectangles and object id here:
        left_object_data = []
        right_object_data = []

        # ObjectCounter:
        lettuce_count = len(contours)

        for c in contours:
            # Get the contour's bounding rectangle:
            bound_rect = cv2.boundingRect(c)

            # Filter out objects with small area
            bound_area = bound_rect[2] * bound_rect[3]
            if abs(bound_area) > MIN_LETTUCE_AREA:
                # Get the dimensions of the bounding rect:
                rectX = bound_rect[0]
                rectY = bound_rect[1]
                rectWidth = bound_rect[2]
                rectHeight = bound_rect[3]

                # Store in list:
                if rectX in range(left_raw_image.shape[0]):
                    left_object_data.append((lettuce_count, bound_rect))
                    color = (0, 0, 255)
                else:
                    right_object_data.append((lettuce_count, bound_rect))
                    color = (255, 0, 0)

                # Draw bounding rect:
                cv2.rectangle(visual,
                              (int(rectX), int(rectY)),
                              (int(rectX + rectWidth),
                               int(rectY + rectHeight)),
                              color, 2)

                # Add text
                visual = cv2.putText(visual, str(bound_area),
                                     (int(rectX) + 8, int(rectY) + 20),
                                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
                                     cv2.LINE_AA)

        # FPS
        visual = cv2.putText(visual, f"{round(fps, 2)} FPS", (0, 20),
                                     cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                     (0, 255, 255), 2,
                                     cv2.LINE_AA)

        cv2.imshow("visual", visual)
        cv2.imshow("raw_combined", combined_image)
        cv2.waitKey(20)
    except CvBridgeError as e:
        print(e)


if __name__ == '__main__':
    left_raw_image = None
    right_raw_image = None
    last_frame_time = 0

    try:
        start_node()
        rospy.Subscriber("/left_camera/image_raw", Image, image_callback_l)
        rospy.Subscriber("/right_camera/image_raw", Image, image_callback_r)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
