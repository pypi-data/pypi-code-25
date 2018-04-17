# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 21:50:48 2018

@author: asieb
"""

import pygame
import logging
import math
import gamegrid

class Actor(object):
    title = ""
    location = (0, 0)
    direction = 0
    grid = None
    surface=None
    is_rotatable=False

    def __init__(self, title, grid, location, heading='E', img_path=None, img_action="scale"):
        self.title = title
        self.grid=grid
        self.location=location
        # Set Actor image
        cell_size=(grid.cell_size,grid.cell_size)
        if img_path != None and img_action == "scale":
            self.surface = pygame.image.load(img_path)
            self.surface = pygame.transform.scale(self.surface, cell_size)
        if img_path != None and img_action == "crop":
            self.surface = pygame.image.load(img_path)
            cropped_surface = pygame.Surface(cell_size)
            cropped_surface.blit(self.surface, (0, 0), (0, 0, self.grid_width(), self.grid_height()))
            self.surface = cropped_surface
        if img_path != None and img_action == "center":
            self.surface = pygame.image.load(img_path)
            cropped_surface = pygame.Surface(cell_size)
            cropped_surface.blit(self.surface, (0, 0), (0, 0, self.grid_width(), self.grid_height()))
            self.surface=  cropped_surface
        logging.debug("Target-Location:" + str(self.location))
        if heading == 'S':
            self.direction=270
        try:
            grid.add_actor(self,location)
        except ValueError:
            logging.error("Achtung.... kein Grid angegeben! ")
        
        
    def log(self):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logger = logging.getLogger('actor-'+title)
        logger.setLevel(logging.DEBUG)
        logger.info('logged from main module')

        
        
    def listen(self, key, cell ):
        pass
    
    def act(self):
        pass

    def setX(self, x):
        self.location[0] = x

    def setY(self, y):
        self.location[1] = y
        
    def set_location(self, location):
        self.location=location

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
    

def main():
    
    grid=gamegrid.GameGrid("My Grid", cell_size=64, columns=4, rows=4,margin=10)
    grid.log()
    python=Actor("Python",grid, (4,4), img_path="python.jpg")
    grid.show()


if __name__ == "__main__":
    main()