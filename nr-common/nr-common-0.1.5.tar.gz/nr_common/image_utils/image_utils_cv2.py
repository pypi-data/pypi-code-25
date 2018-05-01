"""Opencv Image Utilities."""
import uuid

import cv2


def load_image(image_filename):
    """Load image with OpenCV and colored i.e. BGR.

    Args:
        image_filename (str): Path of image.

    Returns:
        numpy.ndarray: Image array with the following characteristics
        - pixel_values: [0, 255]
        - channel_order: BGR
        - shape_order: HWC
        - dtype: np.uint8
    """
    return cv2.imread(image_filename)


def show_image(image, window_name=None, wait=True, wait_time=0, destroy=True, destroy_all_windows=True):
    """Display an image on a window and wait.

    Args:
        image (numpy.ndarray): Image array to display.
        window_name (str): Name of window which is used for identification while destroying.
            If None, a random window_name is created on each call which also generates a new window.
        wait (bool): Whether to wait after displaying the image.
        wait_time (int): If `wait` is True, then the `wait_time` indicates the
            time in milliseconds to wait after displaying the image.
        destroy (bool): Whether to destroy the window after displaying the image.
        destroy_all_windows (bool): Whether to destroy all windows of just the
            window that was created by this function call.
            If True, destroys all windows by calling `cv2.destroyAllWindows()`.
            If False, destroys just this function call window by calling `cv2.destroyWindow(window_name)`.

    """
    window_name = window_name if window_name else "window_{}".format(str(uuid.uuid4())[:8])
    already_destroyed = False

    cv2.imshow(window_name, image)

    if wait:
        # It should be possible to destroy the window while waiting.
        # Press q to destroy.
        if cv2.waitKey(wait_time) & 0xFF == ord('q'):
            if destroy_all_windows:
                cv2.destroyAllWindows()
            else:
                cv2.destroyWindow(window_name)
            already_destroyed = True

    # If window is already destroyed, don't destroy again!
    if destroy and not already_destroyed:
        if destroy_all_windows:
            cv2.destroyAllWindows()
        else:
            cv2.destroyWindow(window_name)
