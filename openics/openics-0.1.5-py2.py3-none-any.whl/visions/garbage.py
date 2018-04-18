import numpy as np
import cv2
from openics.core import math, camera

# Window Configuration
cv2.namedWindow('Detection', cv2.WINDOW_AUTOSIZE)
cv2.moveWindow('Detection', 800, 50)


def nearest_object(frame_data, edge_threshold=600, center_position='center'):
    """
        Nearest object: to find object by distance from aimimg point
        is_open_file -> Use to select source of data
        edge_threshold -> if the value high, it'll looking only explicitly edge
    """
    frame = frame_data
    # CONVERT VIDEO CHANNEL BGR TO GRAY
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # EDEGE DETECTION
    edge_gray = cv2.Canny(
        gray,
        threshold1=edge_threshold,
        threshold2=400
    )
    ret, thresh = cv2.threshold(edge_gray, cv2.THRESH_OTSU, 255, 0)
    # cv2.imshow('Binarization', thresh)

    # FIND CONTOURS
    im, contours, hierarchy = cv2.findContours(
        thresh,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # SET Aiming
    max_y, max_x = gray.shape
    if center_position == 'center':
        frame_center = (max_x//2, max_y//2)
    elif center_position == 'bottom':
        frame_center = (max_x//2, max_y)
    elif center_position == 'top':
        frame_center = (max_x, max_y//2)

    cv2.circle(frame, frame_center, 10, (0, 0, 255), -1)

    # Draw line from frame center to object centroid
    centroid_set, radius_set = [], []
    for points in contours:
        centroid = math.centroid(points)
        radius = math.distance(frame_center, centroid, mode='euclid')
        centroid_set.append(centroid)
        radius_set.append(radius)

    if len(radius_set) > 0:
        min_distance_index = np.argmin(radius_set)
        target_centroid = centroid_set[min_distance_index]
    else:
        min_distance_index = 0
        target_centroid = (frame_center)
    cv2.line(frame, frame_center, target_centroid, (255, 0, 0), 2)
    cv2.circle(frame, target_centroid, 5, (0, 0, 255), -1)

    return frame, target_centroid,


def callback(**kwargs):
    """
        Default callback function for find_object
        it does prints centroid that have got
        from nearest_object.
    """
    for key in kwargs:
        print('{} is {}'.format(key, kwargs[key]))


def find_object(is_open_file=False, edge_threshold=600, callback=callback):
    """
        Integrate functions to find nearest object and show on displays
        is_open_file -> Choose to open from file or camera
        edge_threshold -> Sharp of edge
        callback(cantroid, frame) -> Function that user can write by
        themselves for handle centroid and frame
    """
    cap = camera.open_cam(open_file=is_open_file, file='')

    while cap.isOpened():
        # READ VIDEO FRAME
        ret, frame = cap.read()

        if ret is True:
            frame, centroid = nearest_object(
                frame_data=frame,
                center_position='bottom',
                edge_threshold=edge_threshold
            )
            cv2.imshow('Detection', frame)
        # Callback function for customized by user
        callback(cantroid=centroid, frame=frame)

        # QUIT KEYS
        if cv2.waitKey(36) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
