import spidev
import RPi.GPIO as GPIO
import time
from osensapy import osensapy
import Adafruit_ADS1x15
import Adafruit_MCP4725
from math import log, exp 

class MainBoard():
	#initializes everything as soon as you create a board object
	def __init__(self):
		#SPI setup
		self.spiAdc = spidev.SpiDev()
		self.spiBoards = spidev.SpiDev()
		self.spiAdc.open(0,0)
		self.spiBoards.open(0,1)
		self.spiAdc.max_speed_hz = 1000000 #1MHz clock
		self.spiBoards.max_speed_hz = 1000000

		#GPIO setup
		self.ldac= 26  #19 #DAC pin	
		self.cnv = 19 #ADC pin, onboard ADC
		self.clr = 13 #DAC pin for extra board
		self.cnv_board = 26 #ADC pin for extra ADC
		GPIO.setmode(GPIO.BCM) #this is the GPIO BCM mode for the Pi
		GPIO.setup(self.ldac,GPIO.OUT) 
		GPIO.setup(self.clr,GPIO.OUT)
		GPIO.setup(self.cnv,GPIO.OUT)

		#set the DAC's mode right away to output +/-10V on all channels. See DAC datasheet pg 10 for timing diagram
		GPIO.output(self.clr, GPIO.LOW)
		GPIO.output(self.clr,GPIO.HIGH)
		GPIO.output(self.ldac,GPIO.HIGH)
		self.spiBoards.xfer([0b10001111,0b00000000,0b00000011]) #see DAC datasheet pg 12 for these numbers
		GPIO.output(self.ldac,GPIO.LOW)
		GPIO.output(self.ldac,GPIO.HIGH)

		#1Ch modules setup
		self.transmitter1 = osensapy.Transmitter("/dev/ttyS0", 247, 115200, 1)
		self.transmitter2 = osensapy.Transmitter("/dev/ttyS0", 246, 115200, 1)
		self.transmitter3 = osensapy.Transmitter("/dev/ttyS0", 245, 115200, 1)
		self.t1 = 23
		self.t2 = 4
		self.t3 = 27
		GPIO.setup(self.t1, GPIO.OUT) #CS for t1
		GPIO.setup(self.t2, GPIO.OUT) #for t2
		GPIO.setup(self.t3, GPIO.OUT) #for t3
		GPIO.output(self.t1,GPIO.LOW)
 		GPIO.output(self.t2,GPIO.LOW)
		GPIO.output(self.t3,GPIO.LOW)

		#TEC+LED unit setup
		self.led_on = 17
		GPIO.setup(self.led_on,GPIO.OUT) 
		GPIO.output(self.led_on, GPIO.HIGH)
		#for I2C ADC for TEC
		self.tec_adc = Adafruit_ADS1x15.ADS1015()
		#for I2C DAC for TEC
		self.tec_dac = Adafruit_MCP4725.MCP4725(address=0x63)
		self.tec_dac.set_voltage(1800) #initially set that DAC to reach 24-25C
		self.current_TECSetpoint = 1800 #storing this for future use
		#for I2C DAC for TEC LED
		self.led_dac = Adafruit_MCP4725.MCP4725()
		self.led_dac.set_voltage(0) #initially have that DAC be 0V
		self.current_LEDCurrent = 0 #just storing this for future use 

		#status LEDs
		self.led1 = 24
		self.led2 = 22
		self.led3 = 25
		self.led4 = 5
		GPIO.setup(self.led1, GPIO.OUT)
		GPIO.setup(self.led2, GPIO.OUT)
		GPIO.setup(self.led3, GPIO.OUT)
		GPIO.setup(self.led4, GPIO.OUT)
		GPIO.output(self.led1, 0)
		GPIO.output(self.led2, 0)
		GPIO.output(self.led3, 0)
		GPIO.output(self.led4, 0)

		#set the DAC board channels to all be 0
		self.set_dac(1,0)
		self.set_dac(2,0)
		self.set_dac(3,0)


	#read photodiodes in pairs, with "phase" = channel pair. Will return a list of two values.
	def read_photodiode(self,phase):
		GPIO.output(self.cnv,GPIO.HIGH)
		#the first 3 bytes to xfer are the "Softspan" words, the other bytes (0s) are to receive the previous conversion's results
       #see pg15 of ADC datasheet for timing diagram, pg18 for softspan words (CMOS mode)
		r = self.spiAdc.xfer([0b00000000,0b10010010,0b01001001,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
		GPIO.output(self.cnv,GPIO.LOW)
		if phase == 1:
			intVal1 = (r[0]<<8) + r[1]
			intVal2 = (r[3]<<8) + r[4] 
		elif phase == 2:
			intVal1 = (r[6]<<8) + r[7] 
			intVal2 = (r[9]<<8) + r[10] 
		else:
			intVal1 = (r[12]<<8) + r[13] 
			intVal2 = (r[15]<<8) + r[16] 		
		voltage1 = intVal1 * float(5.12) / 65536
		voltage2 = intVal2 * float(5.12) / 65536

		errorChannel = 0b000000 #every 3rd word is a way you can check if the reading is right
		#error checking 
		if(r[2]!=0b00000001):
			errorChannel=errorChannel + 0b000001
		if(r[5]!=0b00001001):
			errorChannel=errorChannel+0b000010
		if(r[8]!=0b00010001):
			errorChannel=errorChannel+0b000100
		if(r[11]!=0b00011001):
			errorChannel=errorChannel+0b001000
		if(r[14]!=0b00100001):
			errorChannel=errorChannel+0b010000
		if(r[17]!=0b00101001):
			errorChannel=errorChannel+0b100000
		#raise ValueError("There were errors in reading channels: {:06b}".format(errorChannel)) 

		return voltage1,voltage2,'{0:06b}'.format(errorChannel) 


	#to use this, you can not use the DAC at the same time (on the Pi)
	def read_adc(self,phase):
		GPIO.output(self.cnv_board, GPIO.HIGH)
		#the 3 first bytes are "softspan words", 3 bits per channel. The last 0s are to enable a transaction (fill the buffer with 0s, have values returned)
		r = self.spiBoards.xfer([0b00000000,0b00000001,0b10110110,0,0,0,0,0,0])
		GPIO.output(self.cnv_board,GPIO.LOW)
		if phase == 1:
			intVal = self.getIntVal(r[0], r[1])
		elif phase == 2:
			intVal = self.getIntVal(r[3], r[4])
		elif phase == 3:
			intVal = self.getIntVal(r[6], r[7])
		voltage = intVal * float(10) / 32768

		#error checking
		errorChannel = 0b000
		if (r[2] != 0b00000110):
			errorChannel = errorChannel+0b001
		if(r[5] != 0b00001110):
			errorChannel = errorChannel+0b010
		if(r[8] != 0b00010110):
			errorChannel = errorChannel+0b100
		return voltage,'{0:03b}'.format(errorChannel)


	#intermediate step in reading ADC
	def getIntVal(self,r0, r1):
		r = (r0 << 8) + r1
		if (r & (1 << 15)) != 0:
			r = r - (1 << 16)
		return r



	#write a specific value (within +/-10V) to one DAC channel
	def set_dac(self,phase, voltage):
#		GPIO.output(self.clr,GPIO.LOW)
#		GPIO.output(self.clr,GPIO.HIGH)
#		GPIO.output(self.ldac,GPIO.HIGH)
#		self.spiBoards.xfer([0b10001111,0b00000000,0b00000011])
#		GPIO.output(self.ldac,GPIO.LOW)
		GPIO.output(self.ldac,GPIO.HIGH)
		byte1, byte2 = self.valueToBytes(voltage)
       #t is the readback value from the DAC; good for debugging.
		if phase == 1:
			t = self.spiBoards.xfer([0b00110000,byte1,byte2])
		elif phase == 2:
			t = self.spiBoards.xfer([0b00110010,byte1,byte2])
		elif phase == 3:
			t = self.spiBoards.xfer([0b00110100,byte1,byte2])
		GPIO.output(self.ldac,GPIO.LOW)
		GPIO.output(self.ldac,GPIO.HIGH)	
	

	#intermediate step in writing to DAC
	def valueToBytes(self,value):
		value = float(10 + value) / 20
		value = int(value * 65535)
		firstByte = (value >> 8) & 0xFF
		secondByte = value & 0xFF
		#print(firstByte, secondByte)
		return firstByte, secondByte


	#set the setpoint for LED current for the eLED in mA. Max 50mA (3.3V DAC output).
	#Uses the I2C DAC with the Pi 
	def set_LEDCurrent(self,current):
		self.current = current
		if(current > 50):
			raise ValueError("Current too high, stay under 50mA")
		valueToWrite = int(float(current) / 50 * 4096)
		self.led_dac.set_voltage(valueToWrite)
		print("Set eLED current to {}".format(current))	

	#read TEC temperature
	def read_TECTemperature(self):
		voltage = self.tec_adc.read_adc(0, gain=1)
		#transfer function to convert ADC reading to temp
		voltage = float(voltage)/2048 * 4.096
		Rth = (float(3.3)/voltage * 10000) - 10000
		temp = log(float(Rth)/10000)* 1/float(3450) + 1/float(298)
		temp = float(1)/temp - 273
		return temp

    #set TEC temperature setpoint. Default is 20C.
	def set_TECTemperature(self,setpoint):
		#reversing the transfer function to get V: OLD WAY
		setpointInK = setpoint + 273 
		RthForSetpoint = 10000*exp(3450*(float(1)/setpointInK - float(1)/298))
		VForSetpointReading = float(3.3*10000)/(RthForSetpoint + 10000)
		print("V for setpoint: {}".format(VForSetpointReading))
		VForSetpointReading = int(float(VForSetpointReading)/3.3 * 4096)
#		if setpoint < 20:
#			VForSetpointReading -= 50
#			if VForSetpointReading < 50:
#				VForSetpointReading = 50
		print(VForSetpointReading)
		self.tec_dac.set_voltage(VForSetpointReading)
	

	#read 1ch temperature
	def read_temperatureSensor(self,phase):
		if phase == 1:
			GPIO.output(self.t1,GPIO.LOW)
			temp = self.transmitter1.read_channel_temp()
			GPIO.output(self.t1,GPIO.HIGH)
		elif phase == 2:
			GPIO.output(self.t2,GPIO.LOW)
			temp = self.transmitter2.read_channel_temp()
			GPIO.output(self.t2,GPIO.HIGH)
		else:
			GPIO.output(self.t3,GPIO.LOW)
			temp = self.transmitter3.read_channel_temp()
			GPIO.output(self.t3,GPIO.HIGH)
		return temp

	#turn indicator LEDs on or off
	def set_indicator_LED(self,led, state):
		if led == 1:
			GPIO.output(self.led1, state)
		elif led == 2:
			GPIO.output(self.led2, state)
		elif led == 3:
			GPIO.output(self.led3, state)
		else:
			GPIO.output(self.led4, state)

	def quit(self):
		self.set_LEDCurrent(0)
		GPIO.cleanup()
		self.spiAdc.close()
		self.spiBoards.close()
