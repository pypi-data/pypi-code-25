from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QTimer
from PyQt5.QtGui import QPixmap
from . import model
from .view.windows import GameOverWindow, Window
from PyQt5.QtGui import QMoveEvent, QResizeEvent
from PyQt5.QtWidgets import QWidget


class GameTimer(QObject):
    # Signals
    time_over = pyqtSignal()
    time_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.__tick)
        self.timer.setInterval(1000)  # 1 sec

        self.time_left = 0

    def set_time(self, time: int) -> None:
        self.time_left = time

    def add_time(self, time: int) -> None:
        self.time_left += time

    def start(self):
        self.time_changed.emit(self.time_left)
        self.timer.start()

    def stop(self):
        self.timer.stop()

    @pyqtSlot()
    def __tick(self):
        self.time_left -= 1
        if self.time_left <= 0:
            self.time_left = 0
            self.timer.stop()
            self.time_over.emit()


        self.time_changed.emit(self.time_left)


class GameController(QObject):
    __TIMER_START_CAPACITY = 20
    __TIMER_ADDITION = 5

    # Signals
    screenshot_changed = pyqtSignal("QPixmap")
    answer_options_changed = pyqtSignal(list)
    score_changed = pyqtSignal(int)
    timer_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.picked_movies = None
        self.difficult = model.Difficult.EASY

        self.picker = model.MoviesPicker()
        self.score = model.Score()
        self.records = model.Records()

        self.timer = GameTimer()
        self.timer.time_over.connect(self.game_over)
        self.timer.time_changed.connect(self.timer_changed)


    @pyqtSlot()
    def stop_game(self):
        self.timer.stop()

    @pyqtSlot()
    def game_over(self):
        self.timer.stop()

        dialog = GameOverWindow(self.score)
        if not self.records.is_score_record(self.difficult, self.score):
            dialog.ui.name_textbox.setVisible(False)
            dialog.ui.new_record_label.setVisible(False)
        else:
            dialog.name_entered.connect(self.update_records)
        dialog.exec()

        self.start_new_game(self.difficult)

    @pyqtSlot(int)
    def choose_answer(self, answer_id):
        if self.picked_movies.get_answer_options()[answer_id] is self.picked_movies.get_answer():
            self.score.add_points(1)
            self.timer.add_time(self.__TIMER_ADDITION)
        else:
            self.game_over()

        self.score_changed.emit(self.score.get_score())
        self.next_screenshot()

    @pyqtSlot(int)
    def start_new_game(self, difficult):
        self.difficult = difficult
        self.score.clear_score()
        self.picker.clear_picked_movies_history()
        self.next_screenshot()
        self.timer.set_time(self.__TIMER_START_CAPACITY)
        self.timer.start()

    @pyqtSlot()
    def next_screenshot(self):
        self.picked_movies = self.picker.pick_movies(self.difficult)
        answer = self.picked_movies.get_answer()
        answer.screenshot_downloaded.connect(self.screenshot_changed)
        answer.download_screenshot()

        self.answer_options_changed.emit(
            [answer.get_title() for answer in self.picked_movies.get_answer_options()])

    @pyqtSlot(str)
    def update_records(self, name):
        self.records.update_records(self.difficult, self.score, name)


class UIController(QObject):
    show_game_window = pyqtSignal()
    hide_game_window = pyqtSignal()
    show_main_menu = pyqtSignal()
    hide_main_menu = pyqtSignal()
    show_difficult_window = pyqtSignal()
    hide_difficult_window = pyqtSignal()
    show_records_window = pyqtSignal()
    hide_records_window = pyqtSignal()

    start_new_game = pyqtSignal(int)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    @pyqtSlot()
    def new_game(self):
        self.hide_main_menu.emit()
        self.show_difficult_window.emit()

    @pyqtSlot(int)
    def start_game(self, difficult):
        self.hide_difficult_window.emit()
        self.show_game_window.emit()
        self.start_new_game.emit(difficult)

    @pyqtSlot()
    def records(self):
        self.hide_game_window.emit()
        self.hide_main_menu.emit()
        self.hide_difficult_window.emit()

        self.show_records_window.emit()

    @pyqtSlot()
    def to_main_menu(self):
        self.hide_game_window.emit()
        self.hide_difficult_window.emit()
        self.hide_records_window.emit()

        self.show_main_menu.emit()


class WindowsManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_window = None
        self._size = None
        self._pos = None

    def add_window(self, window: Window) -> None:
        window.resized.connect(self.resize)
        window.moved.connect(self.move)
        window.showed.connect(self.window_showed)
        
    @pyqtSlot(QResizeEvent, QWidget)
    def resize(self, event: QResizeEvent, window: QWidget) -> None:
        if window is self._current_window:
            self._size = event.size()

    @pyqtSlot(QMoveEvent, QWidget)
    def move(self, event: QMoveEvent, window: QWidget) -> None:
        if window is self._current_window:
            self._pos = event.pos()

    @pyqtSlot(QWidget)
    def window_showed(self, window: QWidget):
        self._current_window = window
        if self._size is not None:
            window.resize(self._size)
        if self._pos is not None:
            window.move(self._pos)
