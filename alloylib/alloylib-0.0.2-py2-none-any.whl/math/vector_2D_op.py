
"""
Common 2D Vector Operations
"""

from basic import *
import numpy as np


def clip_radian_rotation(rad):
    """
    Clip the radian to be between (-pi, pi]

    parameters
    ----------
    rad : float
        rotation given in radian

    returns
    -------
    float
        clipped value between the range (-pi, pi]
    """
    if rad > np.pi:
        return -(np.pi*2) + rad
    elif rad <= -np.pi:
        return (np.pi*2) + rad
    else:
        return rad

def find_rotation(v1, v2):
    """
    Find the shortest rotation, theta (in radian) that will rotate v1 to v2

    parameters
    ----------
    v1 : numpy array
        2D array of the starting position
    v2 : numpy array
        2D array of the ending position

    returns
    -------
    float
        The rotation in radian that rotates v1 to v2

    """
    #calculate
    rot = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
    return clip_radian_rotation(rot)


def project_point_onto_line(p, p1, p2):
    """
    Projects the p onto the line create by p1 to p2.
    return None if it lies outside of p1 and p2

    parameters
    ----------
    p : numpy array
        The point to be projected
    p1 : numpy array
        The start point of the line
    p2 : numpy array
        The end point of the line

    return
    ------
    numpy array
        The projected point if exist, None if not 
    """

    # #if they are all on the vertical line
    # if p1[0] == p2[0] and p1[0] == p[0]:
    #     if (distance(p,p1) < distance(p,p2)):
    #         return p1
    #     else:
    #         return p2


    v1 = p2 - p1
    v1_norm = v1/np.linalg.norm(v1)
    v2 = p - p1
    pp = v2.dot(v1_norm) * v1_norm
    pp += p1

    #now we check if it's on the line or not
    if (distance(pp,p1) + distance(pp,p2)) == distance(p1,p2):
        return pp
    else:
        return p1 if distance(pp,p1) < distance(pp,p2) else p2


def distance_to_line(p, p1, p2):
    """Find the shortest distance from p to the line created by p1 and p2. If it's
    outside of p1 and p2, return the distance to the closest point of the line
    
    parameters
    ----------
    p : numpy array
        The point to be projected
    p1 : numpy array
        The start point of the line
    p2 : numpy array
        The end point of the line

    return
    ------
    float
        distance to the line
    """
    #project the point onto the line
    v1 = p2 - p1
    v1_norm = v1/np.linalg.norm(v1)
    v2 = p - p1
    pp = v2.dot(v1_norm) * v1_norm
    pp += p1    
    #the created point pp might be far away
    if (distance(pp,p1) + distance(pp,p2)) == distance(p1,p2):
        return distance(pp, p)
    else:
        return distance(p,p1) if distance(pp,p1) < distance(pp,p2) else distance(p,p2)

def main():
    # #test for find_rotation
    # print(find_rotation(np.array([1,0]), np.array([0,-1]))) #should be -1.57079632679
    # print(find_rotation(np.array([1,0]), np.array([0,1]))) #should be 1.57079632679
    # print(find_rotation(np.array([1,0]), np.array([1,0]))) #should be 0
    # print(find_rotation(np.array([1,0]), np.array([-1,0]))) #should be np.pi
    # print(find_rotation(np.array([0,-1]), np.array([-1,0]))) #should be -1.57079632679
    # # print(find_rotation(np.array([1,0]), np.array([-10,1]))) 
    # # print(find_rotation(np.array([1,0]), np.array([-10,-1]))) 
    # # p1 = np.array([6,6])
    # # p2 = np.array([0,5])
    # # p3 = np.array([0,10])
    # # print(project_point_onto_line(p1,p2,p3))

    # print(project_point_onto_line(np.array([0,0]), np.array([0,50]), np.array([0,60]))) 
    # print(project_point_onto_line(np.array([0,10]), np.array([0,50]), np.array([0,60]))) 
    # print(project_point_onto_line(np.array([10,0]), np.array([50,0]), np.array([60,0]))) 
    # print(project_point_onto_line(np.array([0,0]), np.array([50,0]), np.array([60,0]))) 
    # print(project_point_onto_line(np.array([0,0]), np.array([0,50]), np.array([10,50])))


    print(project_point_onto_line(np.array([2,5,5]), np.array([0,10,0]), np.array([0,-10,0])))
    print(project_point_onto_line(np.array([2,15,5]), np.array([0,10,0]), np.array([0,-10,0])))
    print(project_point_onto_line(np.array([-1,15,5]), np.array([0,10,0]), np.array([0,-10,0])))
    print(project_point_onto_line(np.array([-1,0,5]), np.array([0,10,0]), np.array([0,-10,0])))
    print(project_point_onto_line(np.array([-1,10,5]), np.array([0,10,0]), np.array([0,-10,0])))


if __name__ == '__main__':
    main()