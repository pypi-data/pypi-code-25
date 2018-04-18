#!/usr/bin/env python
# coding: utf-8

from inquirer import (
    Text,
    List,
    Password,
    Confirm,
    Checkbox,
    prompt
)

from .exceptions import EmptyError


class QuestionHandler:

    TEXT = "text"
    LIST = "list"
    PASSWORD = "password"
    CHECKBOX = "checkbox"
    CONFIRM = "confirm"


class InquirerComponent(object):

    #
    # Public
    # ##########################

    def prompt(self, handler, message, choices=None):

        if choices:
            questions = self.make_question(handler, message, choices=choices)

        else:
            questions = self.make_question(handler, message)

        result = prompt(questions, raise_keyboard_interrupt=True)[handler]

        if self._isempty(result):

            error_msg = "Empty result! "

            if (handler == QuestionHandler.TEXT
                    or handler == QuestionHandler.PASSWORD):
                error_msg += "Please write something."

            elif handler == QuestionHandler.LIST:
                error_msg += "Please select choiecs."

            elif handler == QuestionHandler.CHECKBOX:
                error_msg += "Please check checkbox."

            elif handler == QuestionHandler.CONFIRM:
                error_msg += "Please write Y/N."

            raise EmptyError(error_msg)

        else:
            return result

    def prompt_text(self, message):

        handler = QuestionHandler.TEXT
        result = self.prompt(handler, message)

        return result

    def prompt_password(self, message):

        handler = QuestionHandler.PASSWORD
        result = self.prompt(handler, message)

        return result

    def prompt_confirm(self, message):

        handler = QuestionHandler.CONFIRM
        result = self.prompt(handler, message)

        return result

    def prompt_list(self, message, choices):

        handler = QuestionHandler.LIST
        result = self.prompt(handler, message, choices)

        return result

    def prompt_checkbox(self, message, choices):

        handler = QuestionHandler.CHECKBOX
        result = self.prompt(handler, message, choices)

        return result

    def make_question(self, handler, message, **kwargs):

        if handler == QuestionHandler.TEXT:

            question = Text(handler, message=message)

        elif handler == QuestionHandler.PASSWORD:

            question = Password(handler, message=message)

        elif handler == QuestionHandler.CONFIRM:

            question = Confirm(handler, message=message)

        elif handler == QuestionHandler.LIST:

            if "choices" not in kwargs:
                raise KeyError("List question need 'choices' kwargs")

            choices = kwargs["choices"]

            description = "('↑', '↓':Select)"
            message = self._add_description(message, description)

            question = List(handler, message=message, choices=choices)

        elif handler == QuestionHandler.CHECKBOX:

            if "choices" not in kwargs:
                raise KeyError("Checkbox question need 'choices' kwargs")

            choices = kwargs["choices"]

            description = "('↑', '↓':Select, '→','←':Choose)"
            message = self._add_description(message, description)

            question = Checkbox(handler, message=message, choices=choices)

        return [question]

    #
    # Private
    # ##########################

    def _isempty(self, obj):

        if isinstance(obj, str):
            return True if obj == "" else False

        elif isinstance(obj, list):
            return True if len(obj) == 0 else False

    def _add_description(self, message, description):

        if message.endswith(" "):
            message += description

        else:
            message += " {0}".format(description)

        return message
