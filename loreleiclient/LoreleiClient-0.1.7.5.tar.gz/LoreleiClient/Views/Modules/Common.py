from LoreleiClient.UIObjects.Input import InputBox
from LoreleiLib.Packets.Common import PlayerQuitPacket
import pygame


class Component(object):

    def __init__(self, x, y, makeView):
        self.x = x
        self.y = y
        self.ui_objects = []
        self.ui_handle_event = []
        self.ui_update = []
        self.input_fields = []
        makeView()

    def add_ui_object(self, ui_obj):
        self.ui_objects.append(ui_obj)
        if hasattr(ui_obj, 'handle_event'):
            self.ui_handle_event.append(ui_obj)
        if hasattr(ui_obj, 'update'):
            self.ui_update.append(ui_obj)
        if isinstance(ui_obj, InputBox):
            self.input_fields.append(ui_obj)

    def remove_ui_object(self, ui_obj):
        if ui_obj in self.ui_objects:
            self.ui_objects.remove(ui_obj)
            if hasattr(ui_obj, 'handle_event'):
                self.ui_handle_event.remove(ui_obj)
            if hasattr(ui_obj, 'update'):
                self.ui_update.remove(ui_obj)
            if isinstance(ui_obj, InputBox):
                self.input_fields.remove(ui_obj)

    def removeAll(self):
        for item in self.ui_objects:
            del item
        for item in self.ui_handle_event:
            del item
        for item in self.ui_update:
            del item
        for item in self.input_fields:
            del item

        self.ui_objects = []
        self.ui_handle_event = []
        self.ui_update = []
        self.input_fields = []

    def handle_event(self, event):
        # Process input events
        for obj in self.ui_handle_event:
            obj.handle_event(event)

        for obj in self.ui_update:
            obj.update()

    def draw(self, screen):
        for obj in self.ui_objects:
            obj.draw(screen)