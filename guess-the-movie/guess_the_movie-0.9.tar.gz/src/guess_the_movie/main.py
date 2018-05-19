import sys
from PyQt5.QtWidgets import QApplication, QButtonGroup
from .view import elements, windows
from . import controller, model


def main():
    # create app
    app = QApplication(sys.argv)

    # create windows
    main_menu = windows.MainMenuWindow()
    game_window = windows.GameWindow()
    difficult_window = windows.DifficultMenuWindow()
    records_window = windows.RecordsWindow()

    # create elements
    buttons = elements.AnswerButtons()
    difficult_buttons = QButtonGroup()

    # create controllers
    game_controller = controller.GameController()
    ui_controller = controller.UIController()
    window_manager = controller.WindowsManager()

    # setup objects
    window_manager.add_window(main_menu)
    window_manager.add_window(game_window)
    window_manager.add_window(difficult_window)
    window_manager.add_window(records_window)

    buttons.addButton(game_window.ui.pushButton, 0)
    buttons.addButton(game_window.ui.pushButton_2, 1)
    buttons.addButton(game_window.ui.pushButton_3, 2)
    buttons.addButton(game_window.ui.pushButton_4, 3)

    difficult_buttons.addButton(difficult_window.ui.pushButton,   model.Difficult.EASY)
    difficult_buttons.addButton(difficult_window.ui.pushButton_2, model.Difficult.NORMAL)
    difficult_buttons.addButton(difficult_window.ui.pushButton_3, model.Difficult.HARD)

    # connect signals to slots
    game_controller.screenshot_changed.connect(game_window.ui.pic_label.set_screenshot)
    game_controller.score_changed.connect(game_window.ui.score.setNum)
    game_controller.answer_options_changed.connect(buttons.change_labels)
    game_controller.timer_changed.connect(game_window.ui.timer_label.setNum)

    buttons.buttonClicked[int].connect(game_controller.choose_answer)

    difficult_buttons.buttonClicked[int].connect(ui_controller.start_game)

    ui_controller.show_main_menu.connect(main_menu.show)
    ui_controller.hide_main_menu.connect(main_menu.hide)
    ui_controller.show_game_window.connect(game_window.show)
    ui_controller.hide_game_window.connect(game_window.hide)
    ui_controller.show_difficult_window.connect(difficult_window.show)
    ui_controller.hide_difficult_window.connect(difficult_window.hide)
    ui_controller.show_records_window.connect(records_window.show)
    ui_controller.hide_records_window.connect(records_window.hide)
    ui_controller.start_new_game.connect(game_controller.start_new_game)

    main_menu.ui.newGameButton.clicked.connect(ui_controller.new_game)
    main_menu.ui.recordsButton.clicked.connect(ui_controller.records)
    main_menu.ui.exitButton.clicked.connect(app.exit)

    records_window.ui.toMainMenu.clicked.connect(ui_controller.to_main_menu)

    difficult_window.ui.ToMainMenu.clicked.connect(ui_controller.to_main_menu)

    game_window.exit_to_main_menu.connect(ui_controller.to_main_menu)
    game_window.exit_to_main_menu.connect(game_controller.stop_game)


    # start app
    main_menu.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()