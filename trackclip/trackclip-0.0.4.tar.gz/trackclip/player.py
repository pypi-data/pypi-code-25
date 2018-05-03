from cv2.cv2 import VideoCapture, imshow, waitKey, Tracker, TickMeter, VideoWriter, VideoWriter_fourcc, CAP_PROP_FPS

from trackclip.hud import HUD
from trackclip.player_state import PlayerState
from trackclip.selector import Selector
from trackclip.tracking_object import TrackingObject


class Player:
    writer: VideoWriter
    tracker: Tracker

    def __init__(self, input_filename: str, output_filename: str, codec: str, window_name: str) -> None:

        # OPTIONS
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.window_name = window_name

        self.state = PlayerState()
        self.hud = HUD(self.state)

        self.writer = None
        if self.output_filename:
            codec = VideoWriter_fourcc(*(codec or 'XVID'))
            self.writer = VideoWriter(output_filename, codec, 30, (1280, 720))

        self.capture = VideoCapture(input_filename)
        if not self.capture.isOpened():
            raise Exception("The capture could not be opened")

        ok, self.frame = self.capture.read()
        if not ok:
            raise Exception("The capture could not be read")

        self.state.target_fps = self.state.original_fps = self.capture.get(CAP_PROP_FPS)

        imshow(self.window_name, self.frame)

        self.selector = Selector(self.window_name)
        self.selector.on_selecting = self.on_selecting
        self.selector.on_selected = self.on_selected

        self.label_uppercase = False

        self.meter = TickMeter()

    def update(self):
        if not self.state.paused:
            ok, self.frame = self.capture.read()
            if not ok:
                return self._close()
            for tracking_object in self.state.tracking_objects:
                tracking_object.update(self.frame)
            if self.writer:
                self.writer.write(self.hud.render_output(self.frame))

        imshow(self.window_name, self.hud.render(self.frame))

        self.meter.stop()
        self.state.fps = 1 / (self.meter.getTimeSec() or 1)
        wait_ms = max(1, 1000.0 / self.state.target_fps - self.meter.getTimeMilli())
        self.meter.reset()
        self.meter.start()

        key = waitKey(int(wait_ms)) & 0xff
        if key == 255:
            pass
        elif len(self.state.tracking_objects) > 0 and self.state.tracking_objects[-1].label_typing_in_progress:
            print(key)
            if key == 27:  # ESC
                self.state.tracking_objects[-1].label = ""
                self.state.tracking_objects[-1].label_typing_in_progress = False
            elif key == 8:
                if len(self.state.tracking_objects[-1].label) > 0:
                    self.state.tracking_objects[-1].label = self.state.tracking_objects[-1].label[:-1]
            elif key == 13:  # ENTER
                self.state.tracking_objects[-1].label_typing_in_progress = False
            elif key == 229:  # CAPS LOCK
                self.label_uppercase = not self.label_uppercase
            elif key in range(32, 127):
                self.state.tracking_objects[-1].label += chr(key) if not self.label_uppercase else chr(key).upper()
        elif key == 27:  # ESC
            return self._close()
        elif key == 32:  # SPACE
            self.state.paused = not self.state.paused
        elif key == 81:  # LARROW
            self.state.target_fps = self.state.target_fps / 2
        elif key == 83:  # RARROW
            self.state.target_fps = self.state.target_fps * 2

    def on_selecting(self, rect):
        self.state.selection = rect

    def on_selected(self, rect):
        if rect[2] != 0 or rect[3] != 0:
            self.state.tracking_objects += [TrackingObject(self.frame, rect)]
        self.state.selection = None

    def _close(self):
        self.capture.release()
        if self.writer:
            self.writer.release()
        return -1