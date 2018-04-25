from PyQt5 import QtWidgets
from point_spectra_gui.ui.AboutQt import Ui_AboutQT


class AboutQT(QtWidgets.QWidget, Ui_AboutQT):
    """
    Display the version for the User. Good for debugging purposes
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    form = AboutQT()
    form.show()
    sys.exit(app.exec_())
