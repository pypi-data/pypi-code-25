#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyEM18
Copyright (C) 2018 Dhaval Savalia <dhaval.savalia6@gmail.com>
All rights reserved.

"""

import os
import serial

class PyEM18(object):
	"""
	A Python written library for EM-18 reader mudule

	@attribute Serial __serial
	UART serial connection via PySerial.

	@attribute Design Philosophy
	Bastian Raschke <bastian.raschke@posteo.de>
	"""
	__serial = None

	def __init__(self, port='/dev/ttyUSB0', baudRate = 9600):
		"""
        Constructor

        @param string port
        @param integer baudRate
        """

		if ( os.path.exists(port) == False ):
			raise ValueError('The EM-18 sensor port "' + port + '" was not found!')

		## Initialize PySerial connection
		self.__serial = serial.Serial(port = port, 
									  baudrate = baudRate, 
									  parity=serial.PARITY_NONE, 
									  stopbits=serial.STOPBITS_ONE, 
									  bytesize=serial.EIGHTBITS
									 )

		## Reset the reader if already initialized
		if ( self.__serial.isOpen() == True ):
			self.__serial.close()
		self.__serial.open()


	def __del__(self):
		"""
		Destructor

		"""

		## Close connection if still established
		if ( self.__serial is not None and self.__serial.isOpen() == True ):
			self.__serial.close()

	def read_data(self, bytesize=12, encoding="utf-8"):
		"""
		Receive a data from reader module.

		@param integer(n byte) bytesize
		@param string(decoding type) encoding
		@return string
		"""
		return self.__serial.read(bytesize).decode(encoding)
