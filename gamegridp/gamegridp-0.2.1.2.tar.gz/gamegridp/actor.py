# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 21:50:48 2018

@author: asieb
"""

import pygame
import logging
import math

class Actor(object):
    title = ""
    location = [0, 0]
    direction = 0
    grid = None
    surface=None
    img_path=None
    is_rotatable=False

    def __init__(self, title, x_pos=0, y_pos=0, heading='E', grid=None):
        self.location=[x_pos,y_pos]
        self.title = title
        self.grid = grid
        # Set Actor image
        if self.img_path!= None:
            self.surface = pygame.image.load(self.img_path)
            self.surface = pygame.transform.scale(self.surface, (grid.cell_size, grid.cell_size))
        logging.debug("Target-Location:" + str(self.location))
        if grid!=None:
            grid.add_actor(self)
        else:
            logging.info("Achtung: Kein Grid für Actor angegeben")
        if heading == 'S':
            self.direction=270
            
        
        
    def listen(self, key, cell ):
        pass
    
    def act(self):
        pass

    def setX(self, x):
        self.location[0] = x

    def setY(self, y):
        self.location[1] = y

    def turn_left(self):
        if (self.direction < 270):
            self.set_direction(self.direction+90)
        else:
            self.set_direction(0)
        logging.debug("Richtung:"+str(self.direction))

    def turn_right(self):
        if (self.direction > 0):
            self.set_direction(self.direction-90)
        else:
            self.set_direction(270)
        logging.debug("Richtung:"+str(self.direction))

    def move_forward(self):
        target=self.look_forward()
        if  (self.is_location_in_grid(target)):
            self.location = target
        logging.debug("self"+str(self.location)+", target"+str(target))
        
    def set_direction(self, direction):
        self.surface = pygame.transform.rotate(self.surface, -self.direction)
        self.surface = pygame.transform.rotate(self.surface, direction)
        self.direction = direction

    def move_up(self):
        self.set_direction(90)
        self.move_forward()

    def move_right(self):
        self.set_direction(0)
        self.move_forward()

    def move_left(self):
        self.set_direction(180)
        self.move_forward()

    def move_down(self):
        self.set_direction(270)
        self.move_forward()
        
    def look_forward(self):
        loc_x=round(self.location[0]+math.cos(math.radians(self.direction)))
        loc_y=round(self.location[1]-math.sin(math.radians(self.direction)))
        return  [loc_x,loc_y]
        
    def is_location_in_grid(self,location):
        if location[0] > self.grid.grid_columns - 1:
            return False
        elif location[1] > self.grid.grid_rows - 1:
            return False
        elif location[0] < 0 or location[1]<0:
            return False
        else :
            return True
        
    def get_location(self):
        return self.location

    def get_neighbours(self):
        locations = []
        y_pos = self.location[0]
        x_pos = self.location[1]
        locations.append([x_pos+1, y_pos])
        locations.append([x_pos+1, y_pos+1])
        locations.append([x_pos, y_pos+1])
        locations.append([x_pos-1, y_pos+1])
        locations.append([x_pos-1, y_pos])
        locations.append([x_pos-1, y_pos-1])
        locations.append([x_pos, y_pos-1])
        locations.append([x_pos+1, y_pos-1])
        return locations

    def hasImage(self):
        if self.surface==None:
            return False
        else:
            return True
        
    def mouse_pressed(self,location):
        pass