import cv2


class Selector:
    window_name: str
    dragging: bool

    def __init__(self, window_name) -> None:
        self.window_name = window_name
        self.dragging = False
        self.points = ((0, 0), (0, 0))
        self.on_selecting = lambda rect: None
        self.on_selected = lambda rect: None
        self.rect = (0, 0, 0, 0)

        try:
            cv2.setMouseCallback(window_name, self.on_mouse)
        except cv2.error:
            cv2.namedWindow(window_name)
            cv2.setMouseCallback(window_name, self.on_mouse)

    def on_mouse(self, event: int, x: int, y: int, flags: int, user_data):
        if event == 0 and self.dragging:
            x0, y0 = self.points[0]
            self.points = ((x0, y0), (x, y))
            self.rect = (min(x0, x), min(y0, y), abs(x - x0), abs(y - y0))
            self.on_selecting(self.rect)
        elif event == 1:
            self.dragging = True
            self.points = ((x, y), (x, y))
            self.rect = (x, y, 0, 0)
            self.on_selecting(self.rect)
        elif event == 4:
            self.dragging = False
            self.on_selected(self.rect)
