# -*- coding: utf-8 -*-
"""
Module for the list of contacts (Widget).
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class UiContactsList(QListWidget):
    """
    UI-class which contains a list of buttons, each of which is a user contact.
    """
    def __init__(self, main_window, parent=None):
        """
        Constructor. Initializes all GUI and links logic to them.
        @param main_window: reference to the parent window (window itself).
        @param parent: ссылка на родительский класс (window panel).
        """
        super().__init__(parent)
        self._main_window = main_window

        self.setResizeMode(QListView.Adjust)
        self.setObjectName('contacts_lb')

        self._last_keyboard_event = None
        self._last_mouse_event = None

        # Log tab should be automatically created
        self.add_contact('Log')

    def keyPressEvent(self, *args, **kwargs):
        """
        Registers keyboard buttons pressing events and writes them in the variable.
        @param args: additional parameters (list).
        @param kwargs: additional parameters (dictionary).
        @return: -
        """
        # print('Keyboard click event:', self._last_keyboard_event.key())
        self._last_keyboard_event = args[0]

    def mousePressEvent(self, *args, **kwargs):
        """
        Registers mouse buttons pressing events and writes them in the variable.
        @param args: additional parameters (list).
        @param kwargs: additional parameters (dictionary).
        @return: -
        """
        # print('Mouse click event:', self._last_mouse_event.button())
        self._last_mouse_event = args[0]

    def add_contact(self, chat_name):
        """
        When initializing main window components, this function adds list of user contacts.
        All data is being received from the server.
        @param chat_name: contact name.
        @return: -
        """
        # Ignores if contact already exists
        index = self.find_contact_widget(chat_name)
        if index:
            return

        item = QListWidgetItem()
        item.setSizeHint(QSize(item.sizeHint().width(), 24))

        button = QPushButton(chat_name)

        # Opens context menu when mouse right button is being pressed
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(lambda _, local_contact_name=chat_name:
                                                  self.show_context_menu(local_contact_name))

        # Opens chat tab when mouse left button is being pressed
        button.clicked.connect(lambda _, local_contact_name=chat_name:
                               self._main_window.open_tab(local_contact_name))

        self.addItem(item)
        self.setItemWidget(item, button)

    def delete_contact(self, chat_name):
        """
        Deletes contact from the list.
        @param chat_name: contact name.
        @return: -
        """
        # Closes chat tab with needed name
        self._main_window.close_tab(chat_name)

        # Deletes contact button from the list of contacts
        index = self.find_contact_widget(chat_name)
        if index is not None:
            self.takeItem(index)

    def find_contact_widget(self, chat_name):
        """
        Searches for contact widget in the list of contacts.
        @param chat_name: contact name.
        @return: index of contact widget.
        """
        contacts_amount = self.count()
        if contacts_amount == 1:
            if self.itemWidget(self.item(0)).text() == chat_name:
                return 0
            return None

        for i in range(0, contacts_amount):
            widget = self.itemWidget(self.item(i))
            if widget.text() == chat_name:
                return i
        return None

    def show_context_menu(self, chat_name):
        """
        Shows context menu on the mouse left button clicking.
        @param chat_name: contact name.
        @return: -
        """
        menu = QMenu(self)
        remove_action = menu.addAction('Remove')
        remove_action.triggered.connect(lambda _, local_chat_name=chat_name:
                                        self._main_window.remove_contact_by_login(local_chat_name))
        menu.exec_(self.mapToGlobal(QPoint(self._last_mouse_event.x(),
                                           self._last_mouse_event.y())))
