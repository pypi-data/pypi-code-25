#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: luijo.tasks
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Luigi targets, plus just a little more.
"""

from abc import ABCMeta
from typing import Any
import jsonpickle
import luigi.target


class LocalObjectTarget(luigi.LocalTarget):
    """
    This is a local target you can use to serialize a Python object to a file.
    """
    __metaclass__ = ABCMeta

    def deserialize(self) -> Any:
        """
        Retrieve the target object.
        :return: the target object
        """
        with self.open('r') as fin:
            frozen = fin.read()
            thawed = jsonpickle.decode(frozen)
            return thawed

    def serialize(self, obj: Any):
        """
        Serialize an object to the local target.

        :param obj: the object you want to serialize
        """
        # Encode the object.
        frozen = jsonpickle.encode(obj)
        # Open the output file for writing.
        with self.open('w') as fout:
            # Write the encoded object.
            fout.write(frozen)
