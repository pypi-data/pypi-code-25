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