from Common import UIView
from LoreleiClient.UIObjects.Input import InputBox, Button, Notification, LabelRightAligned, PasswordInput, \
    ConditionalUI
from LoreleiLib.Packets.Login import LoginAttemptRequest, LoginAttemptResponse, AccountCreateRequest, \
    AccountCreateResponse
from CharacterCreation import CharacterCreationView
from LoreleiClient.Settings.Screen import ScreenSettings
from LoreleiLib.Packets.View import ViewType


class LoginView(UIView):

    def __init__(self, connection=None):
        # Type: () -> None
        width = ScreenSettings.SCREEN_WIDTH
        height = ScreenSettings.SCREEN_HEIGHT
        self.username_label = LabelRightAligned(width/2 - 140, height/2-70, 80, 20, "Username : ", fontSize=24)
        self.username_box = InputBox(width/2-60, height/2-70, 200, 26, fontSize=24)
        self.password_label = LabelRightAligned(width/2 - 140, height/2-35, 80, 20, "Password : ", fontSize=24)
        self.password_box = PasswordInput(width/2-60, height/2-35, 200, 26, fontSize=24)
        self.create_button = Button(width/2-60, height/2, 60, 30, "Create", self.create, fontSize=24)
        self.login_button = Button(width/2+20, height/2, 60, 30, "Login", self.login, fontSize=24)
        self.connecting = ConditionalUI(Notification("Connecting...", hideButton=True), self.checkConnection)
        super(LoginView, self).__init__(self.make_view, ViewType.Login, connection)

    def make_view(self):
        self.add_ui_object(self.username_label)
        self.add_ui_object(self.username_box)
        self.add_ui_object(self.password_label)
        self.add_ui_object(self.password_box)
        self.add_ui_object(self.login_button)
        self.add_ui_object(self.create_button)
        self.add_ui_object(self.create_button)
        self.add_ui_object(self.connecting)

    def checkConnection(self):
        #print "Check Connection"
        if self.connection is None:
            return True
        return False

    def notificationCallback(self):
        self.remove_ui_object(self.notification)

    def login(self):
        self.connection.sendLine(LoginAttemptRequest(self.username_box.text, self.password_box.text))

    def create(self):
        self.connection.sendLine(AccountCreateRequest(self.username_box.text, self.password_box.text))

    def handle_data(self, data):
        if isinstance(data, LoginAttemptResponse):
            if not data.success:
                self.add_ui_object(Notification(data.message, self.notificationCallback))
        elif isinstance(data, AccountCreateResponse):
            self.add_ui_object(Notification(data.message, self.notificationCallback))
        return None