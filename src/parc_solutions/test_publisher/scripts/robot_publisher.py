#!/usr/bin/env python

import random
import rospy
from sensor_msgs.msg import LaserScan

import matplotlib.pyplot as plt
import numpy  as np
import math


def main():
    rospy.init_node('scan_values')
    sub = rospy.Subscriber('/scan', LaserScan, callback)
    
    while True:
        # Generating the X and Y axis data points
        print(ranges)
        r = ranges
        theta = []
        for index in range(len(r)):
            theta.append(angle_inc * index)

        # plotting the polar coordinates on the system
        plt.cla()
        plt.polar(theta,r,marker='o', mfc='r', mec='r', ms=2, color='#00000000')

        # Setting the axis limit
        ax.set_ylim(0, 20)

        # Displaying the plot
        plt.draw()
        plt.pause(0.1)

def callback(msg):
    global ranges, angle_inc

    print(f"Points: {len(msg.ranges)}")
    print(f"Angle Increment: {msg.angle_increment}")
    print(f"Time Increment: {msg.time_increment}")
    print(f"Angle Min: {msg.angle_min}")
    print(f"Angle Max: {msg.angle_max}")

    ranges = msg.ranges
    angle_inc = msg.angle_increment


if __name__ == '__main__':
    plt.ion()
    # Creating a new figure and setting up the resolution
    fig = plt.figure(dpi=200, linewidth=1)

    # Change the coordinate system from scaler to polar
    ax = fig.add_subplot(projection='polar')

    ranges = []
    angle_inc = 0
    
    try:
        main()
    except rospy.ROSInterruptException:
        pass
