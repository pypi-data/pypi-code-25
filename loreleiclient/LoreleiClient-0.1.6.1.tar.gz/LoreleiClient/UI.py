import pygame
from LoreleiClient.Views.Login import LoginView
from LoreleiClient.Settings.Screen import ScreenSettings


class UI:

    def __init__(self, connection):
        self.running = True
        self.connection = connection
        self.connector = None
        self.DESIRED_FPS = 30.0
        self.SCREEN_WIDTH = ScreenSettings.SCREEN_WIDTH
        self.SCREEN_HEIGHT = ScreenSettings.SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.view = LoginView()
        pygame.display.set_caption("Lorelei")

    def game_tick(self):
        try:
            self.view.draw(self.screen)
            pygame.display.flip()
            self.view.handle_events(pygame.event.get())
            return True
        except Exception as err:
            if err.message.lower() != "display surface quit":
                print err
            return False

    def handle_data(self, data):
        newView = self.view.handle_data(data)
        if newView is not None:
            self.setView(newView)

    def setView(self, view):
        print "Change View"
        self.view = view
        self.view.connection = self.connection
        if hasattr(self.view, 'getData'):
            self.view.getData()

    def set_connection(self, connection):
        self.connection = connection
        self.view.connection = connection

    def close(self):
        pygame.quit()
        self.running = False
        self.connection.loseConnection()