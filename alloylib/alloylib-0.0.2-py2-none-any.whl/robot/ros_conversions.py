"""
Different functions that convert Ros messages to Numpy array
"""

import numpy as np

def numpy_to_wrench(arr):
    """Convert numpy array into wrench
    """
    msg = Wrench()
    msg.force.x = arr[0]
    msg.force.y = arr[1]
    msg.force.z = arr[2]
    msg.torque.x = arr[3]
    msg.torque.y = arr[4]
    msg.torque.z = arr[5]
    return msg

def wrench_to_numpy(wrench):
    """Convert Geometry_msgs.Wrench to a numpy array
    where [0:3] are the force and [3:] are torque
    """
    arr = np.zeros((6,))
    arr[0] = wrench.force.x
    arr[1] = wrench.force.y
    arr[2] = wrench.force.z
    arr[3] = wrench.torque.x 
    arr[4] = wrench.torque.y 
    arr[5] = wrench.torque.z 
    return arr

def twist_to_numpy(twist):
    """Convert twist to numpy
    """
    arr = np.zeros((6,))
    arr[0] = twist.linear.x
    arr[1] = twist.linear.y
    arr[2] = twist.linear.z
    arr[3] = twist.angular.x
    arr[4] = twist.angular.y
    arr[5] = twist.angular.z
    return arr

def numpy_to_twist(np_arr):
    """Convert a (6,) numpy array to
    twist given linear first, follow by angular
    """
    msg = Twist()
    msg.linear.x = np_arr[0]
    msg.linear.y = np_arr[1]
    msg.linear.z = np_arr[2]
    msg.angular.x = np_arr[3]
    msg.angular.y = np_arr[4]
    msg.angular.z = np_arr[5]
    return msg

def pose_to_numpy(pose):
    """Convert Pose to Numpy array 
    """

    arr = np.zeros((7,))
    arr[0] = pose.position.x
    arr[1] = pose.position.y
    arr[2] = pose.position.z
    arr[3] = pose.orientation.w
    arr[4] = pose.orientation.x
    arr[5] = pose.orientation.y
    arr[6] = pose.orientation.z
    return arr