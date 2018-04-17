# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 21:49:29 2018

@author: asieb
"""
import pygame
import logging
import os
import sys

class GameGrid(object):
    grid = []
    actors = []
    done = False
    cell_size=16
    grid_rows=0
    grid_columns=0
    play= False
    cell_margin=0
    background_color=(255,255,255)
    cell_color=(0,0,0)
    surface=None
    img_action="resize"
    cell_transparency=0
    logging = None
    
    
    def __init__(self, title, cell_size=32,
                 columns=8, rows=8, margin=0,
                 background_color=(255,255,255), cell_color=(0,0,0), 
                 img_path=None,img_action="scale",log=True):
        """ 
        Initialises the grid
        """
        # Init model
        self.cell_margin = margin
        self.grid_columns = columns
        self.grid_rows = rows
        self.cell_size = cell_size
        self.background_color = background_color
        self.cell_color = cell_color
        self.logging = logging.getLogger('gglogger')
        for row in range(rows):
            self.grid.append([])
            for column in range(columns):
                self.grid[row].append(0)
        # Init gui
        x_res = self.grid_width()
        y_res = self.grid_height()+30
        if img_path != None:
             self.cell_transparency=0
        if img_path != None and img_action == "scale":
            self.surface = pygame.image.load(img_path)
            self.surface = pygame.transform.scale(self.surface, (self.grid_width(), self.grid_height()))
        if img_path != None and img_action == "crop":
            self.surface = pygame.image.load(img_path)
            cropped_surface = pygame.Surface((self.grid_width(), self.grid_height()))
            cropped_surface.blit(self.surface, (0, 0), (0, 0, self.grid_width(), self.grid_height()))
            self.surface=  cropped_surface

        if log==True:
            self.log()
        self.logging.info("Created windows of dimension: ("+ str(x_res)+","+str(y_res)+")")
        WINDOW_SIZE = [x_res, y_res]
        pygame.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(title)
        pygame.init() 

    def grid_width(self):
        logging.debug("Cols: "+ str(self.grid_columns))
        width=self.grid_columns * self.cell_size + (self.grid_columns+1) * self.cell_margin    
        return width                                

    def grid_height(self):
        height=self.grid_rows * self.cell_size + (self.grid_rows+1) * self.cell_margin
        return height
        
    def cell_size(self):
        return self.cell_size
        
    def grid_dimensions(self):
        return (self.grid_width(), self.grid_height())
        
    def draw_actionbar(self):
        """ 
        Draws the action bar
        """
        package_directory = os.path.dirname(os.path.abspath(__file__))
        myfont = pygame.font.SysFont("monospace", 15)
        # Act Button:
        path=os.path.join(package_directory,"data", 'play.png')
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (20, 20))
        pygame.screen.blit(image,(5,(self.grid_height()+5)))
        label = myfont.render("Act", 1, (0,0,0))
        pygame.screen.blit(label, (30, (self.grid_height()+5)))
        # Run Button:
        path=os.path.join(package_directory,"data", 'run.png')
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (20, 20))
        pygame.screen.blit(image,(60,self.grid_height()+5))
        label = myfont.render("Run", 1, (0,0,0))
        pygame.screen.blit(label, (85, (self.grid_height()+5)))
        # Reset Button:
        path=os.path.join(package_directory, "data", 'reset.png')
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (20, 20))
        pygame.screen.blit(image,(120,self.grid_height()+5))
        label = myfont.render("Reset", 1, (0,0,0))
        pygame.screen.blit(label, (145, (self.grid_height()+5)))
        
    def draw_grid(self, grid):
        """ 
        Draws grid with all actors in it.
        """
        pygame.screen.fill(self.background_color)
        # Draw the gamegrid-cells
        if self.surface!=None:
            pygame.screen.blit(self.surface,(0,0,self.grid_width(),self.grid_height()))
        for row in range(self.grid_rows):
            for column in range(self.grid_columns):
                grid_location=[column,row]
                cell_left = self.cell_margin+(self.cell_margin + self.cell_size) * column
                cell_top =  self.cell_margin+(self.cell_margin + self.cell_size) * row
                
                # draw cells
                
                s = pygame.Surface((self.cell_size,self.cell_size))  # rectangle-siue
                s.set_alpha(self.cell_transparency)                # alpha level
                s.fill(self.cell_color)           # this fills the entire surface
                pygame.screen.blit(s, (cell_left, cell_top))
                
        # draw grid around the cells
        i=0
        while (i<=self.grid_width()):
            pygame.draw.rect(pygame.screen,self.background_color,
                [i, 0, self.cell_margin,self.grid_height()])  
            i+=self.cell_size+self.cell_margin
        i=0
        while (i<=self.grid_height()):
            pygame.draw.rect(pygame.screen,self.background_color,
                [0, i, self.grid_width(),self.cell_margin])
            i+=self.cell_size+self.cell_margin

                                
        # Draw Actors at actual position
        for actor in self.actors:
            if actor.hasImage():
                column=actor.location[0]
                row=actor.location[1]
                cell_left = self.cell_margin+(self.cell_margin + self.cell_size) * column
                cell_top =  self.cell_margin+(self.cell_margin + self.cell_size) * row
                pygame.screen.blit(actor.surface,(cell_left,cell_top))
                self.logging.debug("Actor gezeichnet: "+ actor.title + " Location:"+str((cell_left,cell_top)))
        
        
                

    def add_actor(self, actor, location=None):
        """ 
        Adds an actor to the grid. 
        The method is called when a new actor is created.
        """
        self.logging.debug("Actor zum Grid hinzugefügt: "+ actor.title + " Location:"+str(location))
        self.actors.append(actor)
        if location!=None:
            actor.set_location(location)

    def get_actors_at_location(self, location):
        """ 
        Get all actors at a specific location
        """
        actors_at_location = []
        for actor in self.actors:
            if actor.get_location() == location:
                actors_at_location.append(actor)
        return actors_at_location
    
    def get_actors_at_location_by_class(self, location,class_name):
        """ 
        Geta all actors of a specific class at a specific location
        """
        actors_at_location = []
        for actor in self.actors:
            if actor.get_location == location and actor.__class__.__name__ == class_name:
                actors_at_location.append(actor)
        return actors_at_location
        
    def act(self):
        """ 
        Should be overwritten in sub-classes
        """
        pass
    def listen(self,key,cell):
        """ 
        Should be overwritten in sub-classes
        """
        pass

    def show(self):
        """
        Starts the mainloop        
        """
        clock = pygame.time.Clock()
        act=False
        while not self.done:
            for event in pygame.event.get():  # User did something
                ''' Part 1: 
                    For grid an all actors
                    listen to events
                    react with listen() method
                '''
                key_pressed=None
                cell_clicked=None
                if event.type == pygame.QUIT:  # If user clicked close
                    self.done = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if pos[0] < self.grid_width() and pos[1] < self.grid_height():
                        column = (pos[0] - self.cell_margin) // (self.cell_size + self.cell_margin)
                        row = (pos[1] - self.cell_margin )// (self.cell_size + self.cell_margin)
                        cell_clicked=[column,row]
                        self.logging.debug("Mouseclick at grid-position:"+str(cell_clicked))
                    elif pos[1] >= self.grid_height() and pos[0] >5 and pos[0]<30:
                        self.play=False
                        act=True
                        self.logging.debug("Act")
                    elif pos[1] >= self.grid_height() and pos[0] >60 and pos[0]<120:
                        self.play=True
                        self.logging.debug("Play")
                    elif pos[1] >= self.grid_height() and pos[0] >120 and pos[0]<180:
                        self.play=False
                        self.logging.debug("Reset")
                elif event.type ==pygame.KEYDOWN:
                    key_pressed=event.key
                    self.logging.debug("key pressed : "+str(event.key))
                self.listen(key_pressed,cell_clicked)
                for actor in self.actors:
                    actor.listen(key_pressed,cell_clicked)
            ''' Part 2: 
                For grid an all actors
                act()
            '''
            if self.play or act:
                self.act()
                for actor in self.actors:
                    actor.act()
                act=False
            self.draw_grid(self.grid)
            self.draw_actionbar()
            clock.tick(5)
            pygame.display.flip()
        pygame.quit()
        
    def log(self):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logger = logging.getLogger('gglogger')
        logger.setLevel(logging.DEBUG)
            
        
def main():
    
    grid=GameGrid("My Grid", cell_size=64, columns=4, rows=4,margin=10)
    grid.show()


if __name__ == "__main__":
    main()