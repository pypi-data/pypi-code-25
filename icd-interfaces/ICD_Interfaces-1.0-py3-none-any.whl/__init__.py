# -*- coding: utf-8 -*-
""" AC ICD Class Modells

Class models to store AC ICD information

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""


from abc import ABC, abstractmethod
from typing import List,Any, Dict
SOURCE = 0
DESTINATION = 1
DIRECTIONS = dict({SOURCE: 'SOURCE', DESTINATION: 'DESTINATION'})
APEX_INTEGER_LENGTH = 4
APEX_FLOAT_LENGTH = 8
APEX_DISCRETE_LENGTH = 8
APEX_DEFAULT_REFRESH = 8


class Interface(ABC):
    """ Abstract class for interface-type models """
    mandatory_attributes: List[str] = []

    def _add_mandatory(self, attribute)->None:
        self.mandatory_attributes.append(attribute)

    @abstractmethod
    def _set_mandatory(self)->None:
        pass

    def validate(self, obj)->bool:
        """ Checks if all mandatory attributes are set in obj """
        for attribute in self.mandatory_attributes:
            if not getattr(obj, attribute):
                return False

        return True

    def __init__(self)->None:
        self._set_mandatory()
        self.sorted_attributes: Dict[str,str] = dict()
        self._parent = None

    def __str__(self):
        return self.name

    def set_attribute(self, idx:str, value:int, attr:str)->None:
        lst = dir(self)
        if idx in range (0,len(lst)):
            setattr(self, attr, value)

    def get_attributes(self)-> List[Any]:
        lst = dir(self)
        attr_list = []
        for i in lst:
            attr_list.append(getattr(self, i))
        return attr_list

    def sort_attributes(self, order:str)->None:
        for item in order:
            self.sorted_attributes[item] = self.__dict__[item]

    def get_message_length(self)->int:
        return 0

    def get_refresh_period(self)->int:
        return 0

    def get_associated_name(self)->bool:
        return False
        
    def has_parent(self)->bool:
        return False
        
    def can_group(self)->bool:
        return False

    def to_dict(self):
        return self.get_name()

class Signal(Interface):
    """ abstract class for signal-type models """
    def get_parent(self):
        return self._parent

    def set_parent(self, parent):
        if not self._parent:
            self._parent = []
        self._parent.append(parent)


class OutputSignal(Signal):
    """ abstract class for output signals """
    direction = DESTINATION


class OutputLine(Interface):
    """ abstract class for output interfaces """
    direction = DESTINATION


class InputLine(Interface):
    """ abstract class for input interfaces """
    direction = SOURCE


class InputSignal(Signal):
    """ abstract class for input signals """
    direction = SOURCE
