import pygame
from LoreleiClient.UIObjects.Input import InputBox


class UIView(object):

    def __init__(self, make_view, background=(50, 50, 50)):
        self.connection = None
        self.running = True
        self.ui_objects = []
        self.ui_handle_event = []
        self.ui_update = []
        self.background_color = background

        self.input_fields = []
        self.input_index = 0

        make_view()

    def add_ui_object(self, ui_obj):
        self.ui_objects.append(ui_obj)
        if hasattr(ui_obj, 'handle_event'):
            self.ui_handle_event.append(ui_obj)
        if hasattr(ui_obj, 'update'):
            self.ui_update.append(ui_obj)
        if isinstance(ui_obj, InputBox):
            self.input_fields.append(ui_obj)

    def remove_ui_object(self, ui_obj):
        self.ui_objects.remove(ui_obj)
        if hasattr(ui_obj, 'handle_event'):
            self.ui_handle_event.remove(ui_obj)
        if hasattr(ui_obj, 'update'):
            self.ui_update.remove(ui_obj)
        if isinstance(ui_obj, InputBox):
            self.input_fields.remove(ui_obj)

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
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.tab_event()
                    continue

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