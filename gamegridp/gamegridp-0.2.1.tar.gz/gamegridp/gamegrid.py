# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 21:49:29 2018

@author: asieb
"""
import pygame
import logging
import os

class GameGrid(object):
    grid = []
    actors = []
    done = False
    cell_size=16
    grid_rows=0
    grid_columns=0
    play= False
    cell_margin=0
    
    def __init__(self, title, cell_size=32,
                 columns=8, rows=8, margin=0):
        """ 
        Initialises the grid
        """
        # Init model
        self.cell_margin = margin
        self.grid_columns = columns
        self.grid_rows = rows
        self.cell_size = cell_size
        for row in range(rows):
            self.grid.append([])
            for column in range(columns):
                self.grid[row].append(0)
        # Init gui
        x_res = self.grid_width()
        y_res = self.grid_height()+30
        logging.debug("X-Res: "+ str(x_res))
        WINDOW_SIZE = [x_res, y_res]
        pygame.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(title)
        pygame.init() 

    def grid_width(self):
        logging.debug("Cols: "+ str(self.grid_columns))
        width=self.grid_columns * self.cell_size + (self.grid_columns+2) * self.cell_margin    
        logging.debug("Grid-Width: "+ str(width))
        return width                                

    def grid_height(self):
        height=self.grid_rows * self.cell_size + (self.grid_rows+2) * self.cell_margin
        #logging.debug("Grid-Height: "+ str(height))
        return height
        
    def draw_actionbar(self):
        """ 
        Draws the action bar
        """
        myfont = pygame.font.SysFont("monospace", 15)
        path=os.path.join(os.path.dirname(__file__), 'play.png')
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (20, 20))
        pygame.screen.blit(image,(5,(self.grid_height()+5)))
        label = myfont.render("Act", 1, (0,0,0))
        pygame.screen.blit(label, (30, (self.grid_height()+5)))
        path=os.path.join(os.path.dirname(__file__), 'run.png')
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (20, 20))
        pygame.screen.blit(image,(60,self.grid_height()+5))
        label = myfont.render("Run", 1, (0,0,0))
        pygame.screen.blit(label, (85, (self.grid_height()+5)))
        path=os.path.join(os.path.dirname(__file__), 'reset.png')
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (20, 20))
        pygame.screen.blit(image,(120,self.grid_height()+5))
        label = myfont.render("Reset", 1, (0,0,0))
        pygame.screen.blit(label, (145, (self.grid_height()+5)))
        
    def draw_grid(self, grid):
        """ 
        Draws grid with all actors in it.
        """
        pygame.screen.fill((255,255,255))
        # Draw the grid
        for row in range(self.grid_rows):
            for column in range(self.grid_columns):
                grid_location=[column,row]
                cell_left = (self.cell_margin + self.cell_size) * column
                cell_top = (self.cell_margin + self.cell_size) * row + self.cell_margin
                pygame.draw.rect(pygame.screen,(255,255,255),
                                [cell_left, cell_top,self.cell_size,self.cell_size])
                # Draw Actors at actual position
                actors_at_location = self.get_actors_at_location(grid_location)
                for actor in actors_at_location:
                    if actor.hasImage():
                        pygame.screen.blit(actor.surface,(cell_left,cell_top))
                

    def add_actor(self, actor):
        """ 
        Adds an actor to the grid. 
        The method is called when a new actor is created.
        """
        logging.debug("Actor hinzugefügt: "+ actor.title)
        self.actors.append(actor)
        logging.debug(self.actors)

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
                        column = pos[0] // (self.cell_size + self.cell_margin)
                        row = pos[1] // (self.cell_size + self.cell_margin)
                        cell_clicked=[column,row]
                        logging.debug("Mouseclick at grid-position:"+str(cell_clicked))
                    elif pos[1] >= self.grid_height() and pos[0] >5 and pos[0]<30:
                        self.play=False
                        act=True
                        logging.debug("Act")
                    elif pos[1] >= self.grid_height() and pos[0] >60 and pos[0]<120:
                        self.play=True
                        logging.debug("Play")
                    elif pos[1] >= self.grid_height() and pos[0] >120 and pos[0]<180:
                        self.play=False
                        logging.debug("Reset")
                elif event.type ==pygame.KEYDOWN:
                    key_pressed=event.key
                    logging.debug("key pressed : "+str(event.key))
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