import pygame
import os

class ImageManager:

    Images = {}

    def __init__(self):
        if len(ImageManager.Images) == 0:
            self.load()

    def load(self):
        root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Data")
        print os.path.join(root, "sword_small.png")
        ImageManager.Images["sword"] = pygame.image.load(os.path.join(root, "sword_small.png")).convert_alpha()
        ImageManager.Images["shield"] = pygame.image.load(os.path.join(root, "shield_small.png")).convert_alpha()
        ImageManager.Images["helmet"] = pygame.image.load(os.path.join(root, "helm_small.png")).convert_alpha()
        ImageManager.Images["chest"] = pygame.image.load(os.path.join(root, "chest_small.png")).convert_alpha()