from LoreleiClient.Views.Modules.Common import Component
from LoreleiClient.UIObjects.Input import Box, InputBox, Dropdown, DropdownDirection, WrappedLabel, ConditionalUI
from LoreleiLib.Packets.Game.Chat import MessageSent, MessageRecieved, MessageType, WhisperSearchPlayer, \
    WhisperSearchPlayerResult
import pygame as pg


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

    def __init__(self, message, maxWidth, color=None):
        # type: (MessageRecieved, int) -> None
        self.message = message
        if color is None:
            color = ChatMessageColors().Colors[message.type.name]
        super(ChatLine, self).__init__(str(self.message), maxWidth, color)


class ChatBox(Box):

    WBuffer = 4
    HBuffer = 8

    def __init__(self, x, y, w, h):
        self.messages = [] # type: list
        self.chatLines = []
        self.chatSurfaceSize = (w-(ChatBox.WBuffer*2), 800)
        self.chatSurface = pg.Surface(self.chatSurfaceSize)
        self.scrollValue = 0
        super(ChatBox, self).__init__(x, y, w, h, 3, "Chat Log")

    def addMessage(self, message, color=None):
        # type: (MessageRecieved) -> None
        self.messages.insert(0, message)
        self.chatLines.insert(0, ChatLine(message, self.rect.w-(ChatBox.WBuffer * 2), color))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 4:
                    self.scrollValue += 24
                if event.button == 5:
                    self.scrollValue -= 24
                    if self.scrollValue < 0:
                        self.scrollValue = 0


    def draw(self, screen):
        y = 800 - ChatBox.HBuffer
        self.chatSurface.fill((50,50,50))
        for line in self.chatLines: # type: ChatLine
            y -= line.size[1]
            line.draw(ChatBox.WBuffer, y, self.chatSurface)

        cursor = self.chatSurfaceSize[1]-self.rect.h - self.scrollValue
        screen.blit(self.chatSurface, (self.rect.x + ChatBox.WBuffer, self.rect.y + ChatBox.HBuffer,
                                       self.rect.w-(ChatBox.WBuffer * 2), self.rect.h-(ChatBox.HBuffer * 2)),
                    (0, cursor, self.chatSurfaceSize[0], self.rect.h-(ChatBox.HBuffer)))
        super(ChatBox, self).draw(screen)


class MessageTypeOption:

    def __init__(self, type, color=None):
        self.name = type.name
        self.type = type
        self.color = ChatMessageColors().Colors[type.name]


class ChatModule(Component):

    Height = 200
    ChatHeight = 28
    MessageTypeList = [MessageTypeOption(MessageType.Global), MessageTypeOption(MessageType.Region), MessageTypeOption(MessageType.Local), MessageTypeOption(MessageType.Whisper)]

    def __init__(self, x, y, connection):
        self.connection = connection
        self.width = 500
        x += 2
        self.messageType = None
        self.chatBox = ChatBox(x, y, self.width, ChatModule.Height)
        self.messageTypeOption = Dropdown(x, y + ChatModule.Height + 2, '', ChatModule.MessageTypeList, 'name', self.selectMessageType,
                                          minWidth=60, fontSize=24, openDirection=DropdownDirection.Up, colorValue='color')
        self.inputBox = InputBox(x + self.messageTypeOption.rect.w + 2, y + ChatModule.Height + 2, self.width-2-self.messageTypeOption.rect.w, self.messageTypeOption.rect.h, fontSize=24, enterCallback=self.sendMessage)
        self.whisperTargetBox = ConditionalUI(InputBox(x + self.messageTypeOption.rect.w + 2, y + ChatModule.Height + 2, 100, self.messageTypeOption.rect.h, fontSize=24, inactiveCallback=self.searchWhisperTarget), self.showWhisperBox, self.showWhisperBox)
        super(ChatModule, self).__init__(x, y, self.setup)
        self.messageTypeOption.setOption(MessageTypeOption(MessageType.Region))

    def setup(self):
        self.add_ui_object(self.chatBox)
        self.add_ui_object(self.inputBox)
        self.add_ui_object(self.whisperTargetBox)
        self.add_ui_object(self.messageTypeOption)

    def showWhisperBox(self):
        # type: () -> bool
        return self.messageType == MessageType.Whisper

    def searchWhisperTarget(self):
        packet = WhisperSearchPlayer(self.whisperTargetBox.uiObject.text)
        self.connection.sendLine(WhisperSearchPlayer(self.whisperTargetBox.uiObject.text))

    def selectMessageType(self, option):
        self.messageType = option.type
        self.inputBox.setColor(option.color)

        if self.showWhisperBox():
            offset =  self.messageTypeOption.rect.w + 2 + self.whisperTargetBox.uiObject.rect.w + 2
            self.inputBox.rect.x = self.x + offset
            self.inputBox.rect.w = self.width - offset
        else:
            offset = self.messageTypeOption.rect.w + 2
            self.inputBox.rect.x = self.x + offset
            self.inputBox.rect.w = self.width - offset

    def isTyping(self):
        # type: () -> bool
        return self.inputBox.active or self.whisperTargetBox.uiObject.active

    # Got Message
    def addMessage(self, message, color=None):
        # type: (MessageRecieved) -> None
        self.chatBox.addMessage(message, color)

    # Sending Message
    def sendMessage(self, message):
        if self.inputBox.text.strip() != "":
            if self.messageType == MessageType.Whisper:
                self.addMessage(MessageRecieved(MessageType.Raw, "[{}] << {}".format(self.whisperTargetBox.uiObject.text, message)), ChatMessageColors().Colors[MessageType.Whisper.name])
                self.connection.sendLine(MessageSent(self.messageType, message, self.whisperTargetBox.uiObject.text))
            else:
                self.connection.sendLine(MessageSent(self.messageType, message))
        self.inputBox.setText("")

    def handleData(self, data):
        if isinstance(data, MessageRecieved):
            self.addMessage(data)
        if isinstance(data, WhisperSearchPlayerResult):
            self.whisperTargetBox.uiObject.setText(data.username)