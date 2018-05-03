from cv2.cv2 import TrackerKCF_create, Tracker


class TrackingObject:
    tracker: Tracker

    def __init__(self, frame, rect, label=""):
        self.rect = rect
        self.label = label

        self.tracker = TrackerKCF_create()
        self.tracker.init(frame, rect)

        self.label_typing_in_progress = True

    def update(self, frame):
        ok, rect = self.tracker.update(frame)
        if ok:
            self.rect = rect
        else:
            self.rect = None
            self.label_typing_in_progress = False
        return ok
