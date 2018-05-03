class PlayerState:
    def __init__(self) -> None:
        self.paused = False
        self.tracking_objects = []
        self.target_fps = 0
        self.fps = 0
        self.original_fps = 0
        self.selection = None
