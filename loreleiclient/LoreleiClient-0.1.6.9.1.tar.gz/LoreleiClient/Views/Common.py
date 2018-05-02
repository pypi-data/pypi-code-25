import pygame
from LoreleiClient.UIObjects.Input import InputBox, Notification
from LoreleiLib.Packets.Common import PlayerQuitPacket

class UIView(object):

    def __init__(self, makeView, viewType, connection=None, background=(50, 50, 50)):
        self.viewType = viewType
        self.connection = connection
        self.running = True
        self.ui_objects = []
        self.ui_handle_event = []
        self.ui_update = []
        self.background_color = background
        self.notification = None

        self.input_fields = []
        self.input_index = 0

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

    def tab_event(self):
        if len(self.input_fields) > 0:
            if self.input_index >= 0:
                self.input_fields[self.input_index].set_active(False)

            self.input_index += 1
            if self.input_index >= len(self.input_fields):
                self.input_index = 0

            self.input_fields[self.input_index].set_active(True)

    def handle_events(self, events):
        if not self.running:
            pygame.quit()
            return

        for event in events:
            # Process input events
            if event.type == pygame.QUIT:
                self.connection.sendLine(PlayerQuitPacket())
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.tab_event()
                    continue

        for event in events:
            for obj in self.ui_handle_event:
                obj.handle_event(event)

        for obj in self.ui_update:
            obj.update()

    def draw(self, screen):
        screen.fill(self.background_color)

        for obj in self.ui_objects:
            obj.draw(screen)

    def handle_data(self, data):
        pass