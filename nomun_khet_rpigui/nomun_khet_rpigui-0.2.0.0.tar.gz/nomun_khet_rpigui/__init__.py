##https://python-packaging.readthedocs.io/en/latest/
'''
from guizero import App, Text, TextBox, PushButton

def joke():
	return "anaashnii esreg utgatai ug yu we?"

def say_my_name():
    welcome_message.value = my_name.value

app = App(title = "hello world")

welcome_message = Text(app, text="Welcome to my app", size = 20)
my_name = TextBox(app)
update_text = PushButton(app, command=say_my_name, text="Display my name")

#def run():#
#	app.display()
app.display()

'''

import Tkinter as tk 
import cayenne.client
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(26, GPIO.OUT) # LED pin set as output


MQTT_USERNAME  = "703efb90-2a56-11e8-b949-51e66782563e"
MQTT_PASSWORD  = "ebfe2bc570ce3e98d3f15168daac36bcbe5e907e"
MQTT_CLIENT_ID = "51aadea0-58ce-11e8-b666-5747f1aa7b74"


"""
{'topic': u'cmd', 'value': u'1', 'msg_id': u'xM1JKxx5soxMpJx', 'channel': 1, 'client_id': u'51aadea0-58ce-11e8-b666-5747f1aa7b74'}
PUB v1/703efb90-2a56-11e8-b949-51e66782563e/things/51aadea0-58ce-11e8-b666-5747f1aa7b74/data/1
1
"""

LARGE_FONT = ("Verdana", 30)

class SeaofBTCapp(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)
		self.frames = {}

		for F in (StartPage, PageOne):
			frame = F(container, self)
			self.frames[F] = frame
			frame.grid(row=0, column=0, sticky="nsew") #north south east west ?!? centeris
		self.show_frame(StartPage, 1, 0)

	def show_frame(self, cont, cVirtualChanell, cValue):
		frame =  self.frames[cont]
		frame.tkraise()
		client.virtualWrite(cVirtualChanell, cValue)

	def show_frame_1(self, cont):
		frame =  self.frames[cont]
		frame.tkraise()
		#client.virtualWrite(cVirtualChanell, cValue)

	def next_after(self):
		print("asdf")

def qf(stringtoprint):
	print(stringtoprint)

class StartPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="start page 0", font=LARGE_FONT)
		label.pack(pady=10, padx=10)	#methor

		#button1 = tk.Button(self, text= "Visit page 1", command=qf("youyoy"))
		#button1 = tk.Button(self, text= "Visit page 1", 
		#					command = lambda: qf("asdf")) 
		
		button = tk.Button(self, text = "OFF",
							command = lambda: controller.show_frame(PageOne, 1, 1),
							height = 10, width = 30
							)
		button.config(font=('helvetica', 20, 'underline italic'))
		button.config(bg='deep sky blue', fg='dodger blue')
		GPIO.output(26, GPIO.LOW)
							#,image = tk.PhotoImage(file = "off.png")
		#button.config(image = tk.PhotoImage(file = "off.png"))#.subsample(2,2), compound = tk.RIGHT)
		button.pack()

class PageOne(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="start page 1", font=LARGE_FONT)
		label.pack(pady=10, padx=10)	#methor
		
		button1 = tk.Button(self, text = "ON",
							command = lambda: controller.show_frame(StartPage, 1, 0),
							height = 10, width = 30
							)

		button1.config(font=('helvetica', 20, 'underline italic'))
		button1.config(bg='salmon', fg='tomato')
		GPIO.output(26, GPIO.HIGH)

							#,image = tk.PhotoImage(file = "on.png")
		
		#button1.config(image = tk.PhotoImage(file = "on.png"))#.subsample(2,2), compound = tk.RIGHT)
		button1.pack()


	
client = cayenne.client.CayenneMQTTClient()
app = SeaofBTCapp()

def on_message(message):
	print("Recieved: "+ str(message))
	splittedMsg = str(message).split(',') #end daraa n harah
	valueStr    = splittedMsg[1]
	channelStr  = splittedMsg[3]
	print(valueStr)
	print(channelStr)
	channel = int(channelStr.split(' ')[-1])
	value   = int(valueStr.split('\'')[-2])
	print(value)

	if(channel == 1):
		if value == 0:
			app.show_frame_1(StartPage)
		elif value == 1:
			app.show_frame_1(PageOne)


client.on_message = on_message
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)

#app.after(1000, app.next_after())

def do_it():
	client.loop()
	app.after(1000, do_it)
app.after(1000,  do_it)
app.mainloop()






