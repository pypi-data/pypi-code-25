from time import sleep
import threading
import tellopy
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy


class Buffer(object):
    def __init__(self):
        print '%s.__init__()' % str(self.__class__)
        self.cond = threading.Condition()
        self.queue = []

    def read(self, size):
        self.cond.acquire()
        try:
            if len(self.queue) == 0:
                self.cond.wait(1.0)
            data = ''
            while 0 < len(self.queue) and len(data) + len(self.queue[0]) < size:
                data = data + self.queue[0]
                del self.queue[0]
        finally:
            self.cond.release()
        # returning data of zero length indicates end of stream
        # print('%s.read(size=%d) = %d' % (self.__class__, size, len(data)))
        return data

    def seek(self, offset, whence):
        print '%s.seek(%d, %d)' % (str(self.__class__), offset, whence)
        return -1

    def handle_video_frame(self, event, sender, data):
        self.cond.acquire()
        self.queue.append(data)
        self.cond.notifyAll()
        self.cond.release()


def handle_event_connected(event, sender, data, **args):
    drone = sender
    print('connected')
    drone.set_exposure(0)
    drone.set_video_encoder_rate(4)
    drone.start_video()

def main():
    drone = tellopy.Tello()

    try:
        buffer = Buffer()
        drone.subscribe(drone.EVENT_CONNECTED, handle_event_connected)
        drone.subscribe(drone.EVENT_VIDEO_FRAME, buffer.handle_video_frame)

        drone.connect()
        drone.wait_for_connection(60.0)

        container = av.open(buffer)
        while True:
            frame = container.decode(video=0).next()

            image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
            cv2.imshow('Original', image)
            cv2.imshow('Canny', cv2.Canny(image, 100, 100))
            cv2.waitKey(1)

    except Exception as ex:
        print(ex)
    finally:
        drone.quit()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
