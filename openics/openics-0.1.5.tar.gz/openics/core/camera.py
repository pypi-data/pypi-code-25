import cv2


def open_cam(video_capture=0, open_file=False, file=None):
    """
        open camera function powered by opencv-python
        video_capture -> Select cam device by number
        open_file -> if True it will switch to read from file
        file -> file path, required is open_file = True
    """
    # FROM FILE
    if open_file:
        if file is None:
            print('File path: None')
        cap = cv2.VideoCapture(file)
        print('Processing file:', file)
    else:
        # FROM CAMERA
        cap = cv2.VideoCapture(0)

    #  Check is opening
    if cap.isOpened() is False:
        print('Error opening video straming or file')
    else:
        return cap
