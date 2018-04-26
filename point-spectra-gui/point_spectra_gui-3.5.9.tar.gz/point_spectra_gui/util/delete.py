def del_layout(qlayout, idx):
    """
    This method will delete the n - idxed layout that exists in qlayout

    +--------------------+
    | +----------------+ | The outer box is QLayout
    | |       0        | | The inner Layouts marked as 0 and 1 can be indexed by qlayout
    | |                | | You can reference the index of these inner layouts by using
    | +----------------+ | the method takeAt()
    | +----------------+ | In this case if I want to access Layout 2
    | |       1        | | I use qlayout.takeAt(1)
    | |                | |
    | +----------------+ |
    +--------------------+


    :param qlayout:
    :param idx:
    :return:
    """
    to_delete = qlayout.takeAt(qlayout.count() - idx)  # remove the layout item at n-1 index
    if to_delete is not None:  # We run this method as long as there are objects
        while to_delete.count():  # while the count is not 0
            item = to_delete.takeAt(0)  # grab the layout item at 0th index
            widget = item.widget()  # get the widget at this location
            if widget is not None:  # if there is an object in this widget
                widget.deleteLater()  # delete this widget
            else:
                pass


def del_qwidget(QWidget):
    QWidget.close()
    QWidget.deleteLater()
