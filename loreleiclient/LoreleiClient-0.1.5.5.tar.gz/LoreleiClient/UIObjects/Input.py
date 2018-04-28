import pygame as pg
from LoreleiClient.Settings.Screen import ScreenSettings
from LoreleiClient.Images.Manager import ImageManager
from threading import Timer
from itertools import chain
pg.font.init()

COLOR_INACTIVE = pg.Color('seashell1')
COLOR_ACTIVE = pg.Color('yellow2')


class Label(object):

    w_padding = 4
    h_padding = 4

    def __init__(self, x, y, text, fontSize=18):
        text = str(text)
        self.text = text
        self.color = COLOR_ACTIVE
        self.font = pg.font.Font(None, fontSize)
        self.rect = pg.Rect(x, y, self.font.size(self.text)[0], self.font.size(self.text)[1])
        self.txt_surface = self.font.render(text, True, self.color)

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + Label.w_padding, self.rect.y + Label.h_padding))

    def get_width(self):
        return self.font.size(self.text)[0]


class LabelRightAligned(Label):

    def __init__(self, x, y, w, h, text, fontSize=18):
        self.font = pg.font.Font(None, fontSize)
        size = self.font.size(text)

        x = (x + w) - (size[0] + Label.w_padding)
        #y = (x + y) - (size[1] + Label.h_padding)
        super(LabelRightAligned, self).__init__(x, y, text, fontSize)


class Box(object):

    def __init__(self, x, y, w, h, box_width, name="", fontSize=18):
        self.rect = pg.Rect(x, y, w, h)
        self.boxWidth = box_width
        self.font = pg.font.Font(None, fontSize)
        self.name = name
        self.txt_surface = self.font.render(name, True, COLOR_ACTIVE)
        self.textRect = pg.Rect(x + 16, y-(fontSize/3), self.font.size(self.name)[0], self.font.size(self.name)[1])
        self.textRectBackground = pg.Rect(self.textRect.x-6, self.textRect.y, self.textRect.w+12, self.textRect.h)

    def draw(self, screen):
        pg.draw.rect(screen, COLOR_INACTIVE, self.rect, self.boxWidth)

        if self.name != "":
            # Blit the text.
            pg.draw.rect(screen, (50, 50, 50), self.textRectBackground)
            screen.blit(self.txt_surface, self.textRect)


class ParagraphBox(Box):

    def __init__(self, x, y, w, h, box_width, name="", observable=None, fontSize=16):
        super(ParagraphBox, self).__init__(x, y, w, h, box_width, name, fontSize=16)
        self.fontSize = fontSize
        self.font = pg.font.Font(None, fontSize)
        self.text = str(observable.value)
        self.observable = observable
        if observable is not None:
            self.observable.onChangeCallback = self.observableCallback
        self.lines = self.wrap_multi_line(self.text, self.font, self.rect.w-8)

    def observableCallback(self, value):
        self.text = str(value)
        self.lines = self.wrap_multi_line(self.text, self.font, self.rect.w-8)

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

    def truncline(self, text, font, maxwidth):
        real = len(text)
        stext = text
        l = font.size(text)[0]
        cut = 0
        a = 0
        done = 1
        old = None
        while l > maxwidth:
            a = a + 1
            n = text.rsplit(None, a)[0]
            if stext == n:
                cut += 1
                stext = n[:-cut]
            else:
                stext = n
            l = font.size(stext)[0]
            real = len(stext)
            done = 0
        return real, done, stext

    def wrapline(self, text, font, maxwidth):
        done = 0
        wrapped = []

        while not done:
            nl, done, stext = self.truncline(text, font, maxwidth)
            wrapped.append(stext.strip())
            text = text[nl:]
        return wrapped

    def wrap_multi_line(self, text, font, maxwidth):
        """ returns text taking new lines into account.
        """
        lines = chain(*(self.wrapline(line, font, maxwidth) for line in text.splitlines()))
        return list(lines)


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


class Dropdown(object):

    w_padding = 4
    h_padding = 4

    # x, y : Coordinates to draw
    # default_text : Text to display when an option isn't selected
    # options : The options to select from
    # displayValue : The attribute to show in the dropdown
    def __init__(self, x, y, defaultText, options, displayValue, selectCallback, minWidth=None, fontSize=18):
        self.open = False
        self.option = None
        self.options = options
        self.defaultText = defaultText
        self.dropdownRects = []
        self.dropdownSquare = None
        self.selectCallback = selectCallback
        self.displayValue = displayValue
        self.font = pg.font.Font(None, fontSize)
        self.minWidth = minWidth
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
        return largest

    def buildRects(self):
        self.dropdownRects = []
        if self.open:
            y = self.rect.y + self.rect.h

            for option in self.options:
                next_rect = pg.Rect(self.rect.x, y, self.rect.w, self.rect.h)
                self.dropdownRects.append(next_rect)
                y = next_rect.y + next_rect.h

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
        if self.option is not None:
            selected_text = getattr(self.option, self.displayValue)
        self.drawOption(screen, self.rect, selected_text, COLOR_ACTIVE, COLOR_INACTIVE)

        for i in range(0, len(self.dropdownRects)):
            rect = self.dropdownRects[i]
            option = self.options[i]
            self.drawOption(screen, rect, getattr(option, self.displayValue), COLOR_INACTIVE, COLOR_ACTIVE)

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

    def __init__(self, x, y, w, h, text='', prefix='', fontSize=18, enter_callback=None):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.font = pg.font.Font(None, fontSize)
        self.prefix = prefix
        self.text = text
        self.enter_callback = enter_callback
        self.txt_surface = self.font.render(prefix + text, True, self.color)
        self.active = False

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
                    if self.enter_callback is not None:
                        self.enter_callback(self.text)
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pg.K_TAB:
                    pass
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.prefix + self.text, True, self.color)

    def set_active(self, active):
        self.active = active
        # Change the current color of the input box.
        self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+(InputBox.w_padding*2))
        self.rect.w = width

    def draw(self, screen):
        pg.draw.rect(screen, (50, 50, 50), self.rect)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+InputBox.w_padding, self.rect.y+InputBox.h_padding))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)


class PasswordInput(InputBox):

    def __init__(self, x, y, w, h, text='', prefix='', fontSize=18, enter_callback=None):
        super(PasswordInput, self).__init__(x, y, w, h, text, prefix, fontSize, enter_callback)
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
        pg.draw.rect(screen, self.color, self.rect, 2)


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
