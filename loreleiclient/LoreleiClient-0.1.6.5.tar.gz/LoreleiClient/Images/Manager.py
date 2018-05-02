import pygame
import os

class ImageManager:

    Images = {}

    def __init__(self):
        if len(ImageManager.Images) == 0:
            self.load()

    def load(self):
        root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Data")
        ImageManager.Images["icon"] = self.loadImage(root, "crest.png")
        ImageManager.Images["main_hand"] = self.loadImage(root, "sword_small.png")
        ImageManager.Images["off_hand"] = self.loadImage(root, "shield_small.png")
        ImageManager.Images["head"] = self.loadImage(root, "helm_small.png")
        ImageManager.Images["chest"] = self.loadImage(root, "chest_small.png")
        ImageManager.Images["hands"] = self.loadImage(root, "glove_small.png")
        ImageManager.Images["legs"] = self.loadImage(root, "legs_small.png")
        ImageManager.Images["feet"] = self.loadImage(root, "feet_small.png")
        ImageManager.Images["ring1"] = self.loadImage(root, "ring_small.png")
        ImageManager.Images["ring2"] = self.loadImage(root, "ring_small.png")
        ImageManager.Images["necklace"] = self.loadImage(root, "necklace.png")
        ImageManager.Images["bracelets"] = self.loadImage(root, "bracelet.png")

    def loadImage(self, root, path):
        image = None
        try:
            image = pygame.image.load(os.path.join(root, path)).convert_alpha()
        except:
            image = pygame.image.load(os.path.join(root, "sword_small.png")).convert_alpha()
        return image