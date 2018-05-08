import pygame as pg
from LoreleiClient.Settings.Screen import ScreenSettings
from LoreleiClient.Images.Manager import ImageManager
from LoreleiLib.StringHelpers import wrap_multi_line, wrapline
from enum import Enum
from threading import Timer
pg.font.init()

COLOR_INACTIVE = pg.Color('seashell1')
COLOR_ACTIVE = pg.Color('yellow2')


class Label(object):

    w_padding = 4
    h_padding = 4

    def __init__(self, x, y, text, fontSize=18, underlined=False):
        text = str(text)
        self.text = text
        self.color = COLOR_ACTIVE
        self.font = pg.font.Font(None, fontSize)
        self.font.set_underline(underlined)
        self.rect = pg.Rect(x, y, self.font.size(self.text)[0], self.font.size(self.text)[1])
        self.txt_surface = self.font.render(text, True, self.color)

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + Label.w_padding, self.rect.y + Label.h_padding))

    def get_width(self):
        return self.font.size(self.text)[0]


class LabelRightAligned(Label):

    def __init__(self, x, y, w, h, text, fontSize=18, underlined=False):
        self.font = pg.font.Font(None, fontSize)
        size = self.font.size(text)

        x = (x + w) - (size[0] + Label.w_padding)
        super(LabelRightAligned, self).__init__(x, y, text, fontSize, underlined)


class WrappedLabel(object):

    def __init__(self, text, maxWidth, color=COLOR_ACTIVE, fontSize=18):
        self.maxWidth = maxWidth
        self.color = color
        self.fontSize = fontSize
        self.font = pg.font.Font(None, fontSize)
        self.lines = wrapline(text, self.font, maxWidth)
        self.size = self.getTotalSize()

    def getTotalSize(self):
        return [self.maxWidth, len(self.lines) * self.fontSize]

    def draw(self, x, y, screen):
        for line in self.lines:
            lineSize = self.font.render(line, True, self.color)
            screen.blit(lineSize, (x, y))
            y += self.fontSize


class Box(object):

    def __init__(self, x, y, w, h, box_width, name="", fontSize=18):
        self.rect = pg.Rect(x, y, w, h)
        self.boxWidth = box_width
        self.font = pg.font.Font(None, fontSize)
        self.fontSize = fontSize
        self.name = name
        self.txt_surface = self.font.render(name, True, COLOR_ACTIVE)

    def draw(self, screen):
        pg.draw.rect(screen, COLOR_INACTIVE, self.rect, self.boxWidth)
        textRect = pg.Rect(self.rect.x + 16, self.rect.y - (self.fontSize / 3), self.font.size(self.name)[0], self.font.size(self.name)[1])
        textRectBackground = pg.Rect(textRect.x - 6, textRect.y, textRect.w + 12, textRect.h)

        if self.name != "":
            # Blit the text.
            pg.draw.rect(screen, (50, 50, 50), textRectBackground)
            screen.blit(self.txt_surface, textRect)


class ParagraphBox(Box):

    def __init__(self, x, y, w, h, box_width, name="", observable=None, fontSize=18):
        super(ParagraphBox, self).__init__(x, y, w, h, box_width, name, fontSize)
        self.text = str(observable.value)
        self.observable = observable
        if observable is not None:
            self.observable.onChangeCallback = self.observableCallback
        self.lines = wrap_multi_line(self.text, self.font, self.rect.w-8)

    def observableCallback(self, value):
        self.text = str(value)
        self.lines = wrap_multi_line(self.text, self.font, self.rect.w-8)

    def draw(self, screen):
        pg.draw.rect(screen, (50, 50, 50), self.rect)
        super(ParagraphBox, self).draw(screen)
        y = self.rect.top + 8
        x = self.rect.left + 4
        for line in self.lines:
            if y + self.fontSize < self.rect.y + self.rect.h:
                line_size = self.font.size(line)
                txt_area = self.font.render(line, True, COLOR_INACTIVE)
                screen.blit(txt_area, (x, y, line_size[0], line_size[1]))
                y += self.fontSize


class ObservableValue:

    def __init__(self, value, callback=None):
        # type: (object, classmethod) -> None
        self.value = value
        self.onChangeCallback = callback

    def setValue(self, value):
        if self.value != value:
            self.value = value
            if self.onChangeCallback is not None:
                self.onChangeCallback(self.value)


class IntValueBox:

    def __init__(self, x, y, w, h, observable, fontSize=18):
        # type: (int, int, int, int, ObservableValue) -> None
        self.observable = observable
        self.observable.onChangeCallback = self.valueUpdated
        self.text = None
        self.textOffset = (Label.w_padding, Label.h_padding)
        self.color = COLOR_ACTIVE
        self.font = pg.font.Font(None, fontSize)
        self.rect = pg.Rect(x, y, w, h)
        self.valueUpdated(int(observable.value))

    def valueUpdated(self, value):
        # type: (int) -> None
        self.text = str(value)
        size = self.font.size(self.text)
        self.textOffset = ((self.rect.w - size[0]) / 2, (self.rect.h - size[1]) / 2)

    def draw(self, screen):
        txt_surface = self.font.render(self.text, True, self.color)
        screen.blit(txt_surface, (self.rect.x + self.textOffset[0], self.rect.y + self.textOffset[1]))
        pg.draw.rect(screen, COLOR_INACTIVE, self.rect, 2)


class Button(object):

    w_padding = 8
    h_padding = 4
    hover_offset = 2

    def __init__(self, x, y, w, h, text, callback, fontSize=18):
        self.hover = False
        self.color = COLOR_INACTIVE
        self.font = pg.font.Font(None, fontSize)
        font_render_size = self.font.size(text)
        self.rect = pg.Rect(x, y, font_render_size[0] + Button.w_padding*2, font_render_size[1] + Button.h_padding*2)
        self.hover_rect = pg.Rect(x-Button.hover_offset, y-Button.hover_offset, self.rect.w, self.rect.h)
        self.callback = callback
        self.text = text

        font_area = self.font.size(text)

        self.txt_surface = self.font.render(text, True, self.color)

    def handle_event(self, event):
        if event.type == pg.MOUSEMOTION:
            if self.rect.collidepoint(pg.mouse.get_pos()) or self.hover_rect.collidepoint(pg.mouse.get_pos()):
                self.hover = True
            else:
                self.hover = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos) :
                # Toggle the active variable.
                self.callback()

                self.color = COLOR_ACTIVE
                Timer(0.1, self.reset).start()

    def reset(self):
        self.color = COLOR_INACTIVE

    def draw(self, screen):
        if self.hover:
            # Blit the text.
            screen.blit(self.txt_surface, (self.hover_rect.x + Button.w_padding, self.hover_rect.y + Button.h_padding))
            # Blit the rect.
            pg.draw.rect(screen, self.color, self.hover_rect, 2)

        else:
            # Blit the text.
            screen.blit(self.txt_surface, (self.rect.x+Button.w_padding, self.rect.y+Button.h_padding))
            # Blit the rect.
            pg.draw.rect(screen, self.color, self.rect, 2)


class ConditionalUI(object):

    def __init__(self, uiObject, drawConditional=None, interactConditional=None):
        self.uiObject = uiObject
        self.drawCondition = drawConditional
        self.interactCondition = interactConditional

    def draw(self, screen):
        if self.drawCondition is None:
            self.uiObject.draw(screen)
        else:
            if self.drawCondition():
                self.uiObject.draw(screen)

    def handle_event(self, event):
        if self.interactCondition is None:
            self.uiObject.handle_event(event)
        else:
            if self.interactCondition():
                self.uiObject.handle_event(event)

    def update(self):
        if hasattr(self.uiObject, "update"):
            self.uiObject.update()


class DropdownDirection(Enum):
    Down = 0
    Up = 1


class Dropdown(object):

    w_padding = 4
    h_padding = 4

    # x, y : Coordinates to draw
    # default_text : Text to display when an option isn't selected
    # options : The options to select from
    # displayValue : The attribute to show in the dropdown
    def __init__(self, x, y, defaultText, options, displayValue, selectCallback, minWidth=None, minHeight=None,
                 fontSize=18, openDirection=DropdownDirection.Down, colorValue=None):
        self.open = False
        self.option = None
        self.options = options
        self.openDirection = openDirection
        self.defaultText = defaultText
        self.dropdownRects = []
        self.dropdownSquare = None
        self.selectCallback = selectCallback
        self.displayValue = displayValue
        self.colorValue = colorValue
        self.font = pg.font.Font(None, fontSize)
        self.minWidth = minWidth
        self.minHeight = minHeight
        size = self.getLargestItemSize()
        self.rect = pg.Rect(x, y, size[0]+(Dropdown.w_padding*2), size[1] + (Dropdown.h_padding*2))

    def getLargestItemSize(self):
        largest = self.font.size(self.defaultText)
        for option in self.options:
            size = self.font.size(getattr(option, self.displayValue))
            if size[0] > largest[0]:
                largest = size

        if self.minWidth > largest[0]:
            largest = (self.minWidth, largest[1])
        if self.minHeight > largest[1]:
            largest = (largest[0], self.minHeight)

        return largest

    def buildRects(self):
        self.dropdownRects = []
        if self.open and self.openDirection == DropdownDirection.Down:
            y = self.rect.y + self.rect.h

            for option in self.options:
                next_rect = pg.Rect(self.rect.x, y, self.rect.w, self.rect.h)
                self.dropdownRects.append(next_rect)
                y = next_rect.y + next_rect.h
        if self.open and self.openDirection == DropdownDirection.Up:
            y = self.rect.y - self.rect.h

            for option in self.options:
                next_rect = pg.Rect(self.rect.x, y, self.rect.w, self.rect.h)
                self.dropdownRects.append(next_rect)
                y = next_rect.y - next_rect.h

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            pos = event.pos
            if not self.open:
                if self.rect.collidepoint(pos):
                    self.open = True
                    self.buildRects()
            else:
                for i in range(0, len(self.dropdownRects)):
                    rect = self.dropdownRects[i]
                    if rect.collidepoint(pos):
                        self.setOption(self.options[i])

                self.open = False
                self.buildRects()

    def draw(self, screen):
        if len(self.options) == 0:
            return

        selected_text = self.defaultText
        color = COLOR_INACTIVE
        if self.option is not None:
            selected_text = getattr(self.option, self.displayValue)
            if self.colorValue is not None:
                color = getattr(self.option, self.colorValue)

        self.drawOption(screen, self.rect, selected_text, color, COLOR_INACTIVE)

        for i in range(0, len(self.dropdownRects)):
            rect = self.dropdownRects[i]
            option = self.options[i]
            color = COLOR_INACTIVE
            if self.colorValue is not None:
                color = getattr(option, self.colorValue)
            self.drawOption(screen, rect, getattr(option, self.displayValue), color, COLOR_ACTIVE)

    def setOption(self, option):
        self.option = option
        self.selectCallback(option)

    def drawOption(self, screen, rect, text, text_color, box_color):
        pg.draw.rect(screen, (50, 50, 50), rect)
        # Blit the text.
        screen.blit(self.font.render(text, True, text_color), (rect.x + Dropdown.w_padding, rect.y + Dropdown.h_padding))
        # Blit the rect.
        pg.draw.rect(screen, box_color, rect, 2)


class Image(object):

    def __init__(self, x, y, imageName):
        self.x = x
        self.y = y
        image = ImageManager().Images[imageName]
        if image is None:
            print "Could not load image for resource name,", imageName
        else:
            self.image = image

    def draw(self, screen):
        if self.image is not None:
            screen.blit(self.image, (self.x, self.y))


class InputBox(object):

    w_padding = 4
    h_padding = 4

    def __init__(self, x, y, w, h, text='', prefix='', fontSize=18, enterCallback=None, inactiveCallback=None):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.borderColor = COLOR_INACTIVE
        self.font = pg.font.Font(None, fontSize)
        self.prefix = prefix
        self.text = text
        self.enterCallback = enterCallback
        self.txt_surface = self.font.render(prefix + text, True, self.color)
        self.txt_size = self.txt_surface.get_size()
        self.active = False
        self.inactiveCallback = inactiveCallback

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.set_active(True)
            else:
                self.set_active(False)

        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    if self.enterCallback is not None:
                        self.enterCallback(self.text)
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pg.K_TAB:
                    pass
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.prefix + self.text, True, self.color)
                self.txt_size = self.txt_surface.get_size()

    def setColor(self, color):
        self.color = color
        self.txt_surface = self.font.render(self.prefix + self.text, True, self.color)
        self.txt_size = self.txt_surface.get_size()

    def set_active(self, active):
        if self.inactiveCallback is not None and active is False and self.active is True:
            self.inactiveCallback()

        self.active = active
        # Change the current color of the input box.
        self.borderColor = COLOR_ACTIVE if self.active else COLOR_INACTIVE

    def setText(self, text):
        self.text = text
        self.txt_surface = self.font.render(self.prefix + self.text, True, self.color)
        self.txt_size = self.txt_surface.get_size()

    def draw(self, screen):
        pg.draw.rect(screen, (50, 50, 50), self.rect)
        # Blit the text.
        width = self.getDrawWidth()
        screen.blit(self.txt_surface, (self.rect.x+InputBox.w_padding, self.rect.y+InputBox.h_padding), (self.getDrawX(width),0, width, self.txt_size[1]))
        # Blit the rect.
        pg.draw.rect(screen, self.borderColor, self.rect, 2)

    def getDrawWidth(self):
        maxWidth = self.rect.w - (InputBox.w_padding*2)
        width = self.txt_size[0]
        if width > maxWidth:
            width = maxWidth
        return width

    def getDrawX(self, drawWidth):
        x = self.txt_size[0] - drawWidth
        if x < 0:
            return 0
        else:
            return x


class PasswordInput(InputBox):

    def __init__(self, x, y, w, h, text='', prefix='', fontSize=18, enterCallback=None):
        super(PasswordInput, self).__init__(x, y, w, h, text, prefix, fontSize, enterCallback)
        self.value = ''
        self.txt_surface = self.font.render(self.value, True, self.color)

    def draw(self, screen):
        self.value = ''
        for i in range(0, len(self.text)):
            self.value += '*'

        self.txt_surface = self.font.render(self.value, True, self.color)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(screen, self.borderColor, self.rect, 2)


class Notification(object):

    def __init__(self, text, callback=None, button_text="Ok", text_color=COLOR_INACTIVE, fontSize=18, hideButton=False):
        self.padding = 10
        self.color = COLOR_INACTIVE
        self.font = pg.font.Font(None, fontSize)
        self.callback = callback
        self.text = text
        self.text_color = text_color
        self.open = True
        self.hideButton = hideButton
        self.txt_surface = self.font.render(text, True, self.text_color)
        font_area = self.font.size(text)
        self.rect = pg.Rect(ScreenSettings.SCREEN_WIDTH/2 - font_area[0]/2 - self.padding, ScreenSettings.SCREEN_HEIGHT/2 - font_area[1]/2 - self.padding, font_area[0] + self.padding*2, font_area[1] + self.padding*2)

        button_text_size = self.font.size(button_text)
        self.button = Button(self.rect.x + self.rect.w - (button_text_size[0] + 20), self.rect.y + self.rect.h + 10, button_text_size[0] + (Button.w_padding*2), button_text_size[1] + (Button.h_padding*2), button_text, self.call_callback)

        # Find text size
        # Make Rect around it
        # Make Button

    def call_callback(self):
        print "Notification close?"
        self.open = False
        if self.callback is not None:
            self.callback()

    def draw(self, screen):
        if self.open:
            pg.draw.rect(screen, (50,50,50), self.rect)
            # Blit the text.
            screen.blit(self.txt_surface, (self.rect.x+self.padding, self.rect.y+self.padding))
            # Blit the rect.
            pg.draw.rect(screen, self.color, self.rect, 2)

            if not self.hideButton:
                self.button.draw(screen)

    def handle_event(self, event):
        if not self.hideButton:
            self.button.handle_event(event)
