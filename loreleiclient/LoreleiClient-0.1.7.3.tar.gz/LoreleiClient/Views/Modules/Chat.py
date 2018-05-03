from LoreleiClient.Views.Modules.Common import Component
from LoreleiClient.UIObjects.Input import Box, Label, InputBox, Dropdown, DropdownDirection, WrappedLabel
from LoreleiLib.Packets.Game.Chat import MessageSent, MessageRecieved, MessageType
from LoreleiLib.StringHelpers import wrapline
import pygame


class ChatMessageColors:

    Colors = {}

    def __init__(self):
        if len(ChatMessageColors.Colors) == 0:
            self.load()

    def load(self):
        ChatMessageColors.Colors[MessageType.Global.name] = (173, 255, 184) # Green
        ChatMessageColors.Colors[MessageType.Region.name] = (255, 234, 158) # Yellow
        ChatMessageColors.Colors[MessageType.Local.name] = (145, 233, 255) # Blue
        ChatMessageColors.Colors[MessageType.Whisper.name] = (255, 168, 243) # Pink
        ChatMessageColors.Colors[MessageType.Combat.name] = (255, 146, 145) # Red
        ChatMessageColors.Colors[MessageType.System.name] = (255, 181, 63) # Orange


class ChatLine(WrappedLabel):

    def __init__(self, message, maxWidth):
        # type: (MessageRecieved, int) -> None
        self.message = message
        super(ChatLine, self).__init__(str(self.message), maxWidth, ChatMessageColors().Colors[message.type.name])


class ChatBox(Box):

    def __init__(self, x, y, w, h):
        self.messages = [] # type: list
        self.chatLines = []
        self.chatSurfaceSize = (w-8, 800)
        self.chatSurface = pygame.Surface(self.chatSurfaceSize)
        super(ChatBox, self).__init__(x, y, w, h, 3, "Chat Log")

    def addMessage(self, message):
        # type: (MessageRecieved) -> None
        self.messages.insert(0, message)
        self.chatLines.insert(0, ChatLine(message, self.rect.w-8))

    def draw(self, screen):
        y = 800
        self.chatSurface.fill((50,50,50))
        for line in self.chatLines: # type: ChatLine
            y -= line.size[1]
            line.draw(4, y, self.chatSurface)

        cursor = self.chatSurfaceSize[1]-self.rect.h
        screen.blit(self.chatSurface, (self.rect.x + 4, self.rect.y + 4, self.rect.w-8, self.rect.h-8), (0, cursor, self.chatSurfaceSize[0], self.rect.h-8))
        super(ChatBox, self).draw(screen)

class ChatModule(Component):

    MessageTypeList = [MessageType.Global, MessageType.Region, MessageType.Local, MessageType.Whisper]

    def __init__(self, x, y, connection):
        self.width = 500
        self.height = 300
        x += 2
        self.connection = connection
        self.typing = False
        self.messageType = MessageType.Local
        self.chatBox = ChatBox(x, y, self.width, self.height)
        self.messageTypeOption = Dropdown(x, y + self.height + 2, '', ChatModule.MessageTypeList, 'name', self.selectMessageType,
                                          minWidth=60, fontSize=24, openDirection=DropdownDirection.Up)
        self.inputBox = InputBox(x + self.messageTypeOption.rect.w + 2, y + self.height + 2, self.width-2-self.messageTypeOption.rect.w, self.messageTypeOption.rect.h, fontSize=24, enterCallback=self.sendMessage)
        self.messageTypeOption.option = MessageType.Region
        super(ChatModule, self).__init__(x, y, self.setup)

    def setup(self):
        self.makeFakeMessages()
        self.add_ui_object(self.chatBox)
        self.add_ui_object(self.inputBox)
        self.add_ui_object(self.messageTypeOption)

    def selectMessageType(self, type):
        self.messageType = type

    def makeFakeMessages(self):
        self.addMessage(MessageRecieved(MessageType.Global, "Hello from the other side!", "Example_Player"))
        self.addMessage(MessageRecieved(MessageType.Region, "This region is cool", "Example_Player"))
        self.addMessage(MessageRecieved(MessageType.Local, "This is pretty ROOMY", "l33t_n00b"))
        self.addMessage(MessageRecieved(MessageType.Whisper, "Psssst.... Hi", "l33t_n00b"))
        self.addMessage(MessageRecieved(MessageType.Combat, "You were hit for {} damage".format(6)))
        self.addMessage(MessageRecieved(MessageType.System, "Server shutting down soon"))
        self.addMessage(MessageRecieved(MessageType.System, "This is a really long message so that I can make sure the wrapping works and doesn't fuck up, we'll see what happens"))

    # Got Message
    def addMessage(self, message):
        # type: (MessageRecieved) -> None
        self.chatBox.addMessage(message)

    # Sending Message
    def sendMessage(self, message):
        self.connection.sendLine(MessageSent(self.messageType, message))
        self.addMessage(MessageRecieved(self.messageType, message, "Me"))
        self.inputBox.text = ""

    def handle_event(self, event):
        # If we are typing handle all client events here
        if self.typing:
            # handle text in box
            pass
        else:
            super(ChatModule, self).handle_event(event)

    def handleData(self, data):
        if isinstance(data, MessageRecieved):
            self.addMessage(data)