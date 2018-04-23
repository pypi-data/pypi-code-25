from Common import UIView
from LoreleiClient.UIObjects.Input import InputBox, Button, Notification, LabelRightAligned, PasswordInput
from LoreleiLib.Packets.Login import LoginAttempt, LoginResult, AccountCreateAttempt, AccountCreateResult
from CharacterCreation import CharacterCreationView


class LoginView(UIView):

    def __init__(self):
        # Type: () -> None
        self.username_label = LabelRightAligned(120, 150, 80, 20, "Username : ")
        self.username_box = InputBox(200, 150, 200, 20)
        self.password_label = LabelRightAligned(120, 180, 80, 20, "Password : ")
        self.password_box = PasswordInput(200, 180, 200, 20)
        self.create_button = Button(200, 210, 60, 30, "Create", self.create)
        self.login_button = Button(280, 210, 60, 30, "Login", self.login)
        self.notification = None
        super(LoginView, self).__init__(self.make_view)

    def make_view(self):
        self.add_ui_object(self.username_label)
        self.add_ui_object(self.username_box)
        self.add_ui_object(self.password_label)
        self.add_ui_object(self.password_box)
        self.add_ui_object(self.login_button)
        self.add_ui_object(self.create_button)

    def login(self):
        self.connection.sendLine(LoginAttempt(self.username_box.text, self.password_box.text))

    def create(self):
        self.connection.sendLine(AccountCreateAttempt(self.username_box.text, self.password_box.text))

    def notification_callback(self):
        self.remove_ui_object(self.notification)
        self.notification = None

    def handle_data(self, data):
        if isinstance(data, LoginResult) or isinstance(data, AccountCreateResult):
            if not data.success:
                self.notification = Notification(data.message, self.notification_callback)
                self.add_ui_object(self.notification)
            else:
                self.notification = Notification(data.message, self.notification_callback)
                self.add_ui_object(self.notification)
                return CharacterCreationView()
        return None