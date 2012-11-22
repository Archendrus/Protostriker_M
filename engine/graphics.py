#-------------------------------------------------------------------------------
# Name:        Graphics
# Purpose:     Component of Engine, contains the images manager and
#              Viewport class
#
# Author:      Will Taplin
#
# Created:     02/07/2011
# Copyright:   (c) Owner 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import pygame
from pygame.locals import *
import os
import system

class ImageManager():
    """ loads all game images and font into a single dictionary
        call load_single for a single image, load_sliced_images for
        a sprite sheet
        filename - name of image file to load
        key - the ID for the image, or set of images
        w, h - width and height of individual frame (sprite sheet)
        rows - boolean for whether the sprite sheet has multiple rows or not
        colorkey - RGB value for transparency, - 1 will take color from top
                   left corner of image for transparency """

    def __init__(self):
        self.images = dict()  # dictionary of all images loaded

    def load_image(self, filename, colorkey = None):
        # call pygame image load function

        # create platform independent path
        fullname = os.path.join('res', 'images', filename)
        try:
            image = pygame.image.load(fullname)
        except pygame.error, message:
            print 'Cannot load image:', filename
            raise SystemExit, message
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:  # colorkey of -1 will get pixel at top left
                colorkey =  image.get_at((0,0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image

    def load_sliced_images(self, filename, w, h, rows, colorkey):
        # slice up a sprite sheet
        # returns a list of pygame surfaces
        images = []
        master_image = self.load_image(filename, colorkey = colorkey)
        master_width, master_height = master_image.get_size()
        if rows:  # for images that have more than one row
            for j in range(int(master_height/h)):
                images.append([])  # add a new row to the list
                for i in range(int(master_width/w)):  # number of frames wide
                     # add each frame, from left to right
                    images[j].append(master_image.subsurface((i*w,j*h,w,h))) 
        else: # for single row image sheets
            for i in range(int(master_width/w)):
                images.append(master_image.subsurface((i*w,0,w,h)))
        return images

    def load_single(self, filename, key, colorkey = None):
        # loads a single image into the image manager
        image = self.load_image(filename, colorkey)
        self.images[key] = image

    def load_sheet(self, filename, key, w, h, rows = True, colorkey = None):
        # loads an image sheet into the image manager
        # load_sliced_images returns the individual frames or tiles
        images = self.load_sliced_images(filename, w, h, rows, colorkey)
        self.images[key] = images

    def load_font(self, filename, size):
        fullname = os.path.join('res', 'fonts', filename)
        try:
            font = pygame.font.Font(fullname, size)
        except pygame.error, message:
            print 'Cannot load font:', name
            raise SystemExit, message
        self.font = font

    def get_image(self, key):
        # accessor method for images
        # use to assign a sprites image attribute
        return self.images[key]

    def get_font(self):
        return self.font

    def unload_image(self, key):
        # unload an image from the image manager
        del self.images[key]

class Viewport():
    """ This class creates a viewport that is the size
    of the screen, from a larger background image to
     enable scrolling"""
    def __init__(self, game, background, auto_scroll = True):
        self.game = game
        self.background = background
        self.auto_scroll = auto_scroll
        self.width = 320 # width of screen
        self.height = 240 # height of screen
        self.coordinate = 0  # left edge of viewport
        self.last_coordinate = 0
        self.level_pos = 0
        self.minScroll = 0 # max value for left scrolling
        self.maxScroll = self.background.get_width() - 320 # max for right
        self.advance_velocity = 100  # speed of scroll
        self.vp = self.background.subsurface((self.coordinate, 0,
                                              self.width, self.height))

    def update(self):

        self.last_coordinate = self.coordinate
        self.last_level_pos = self.level_pos

        self.coordinate += self.advance_velocity * system.TIMESTEP
        self.level_pos += self.advance_velocity * system.TIMESTEP

        # loop image
        if self.coordinate > self.maxScroll:
                self.last_coordinate = 0
                self.coordinate = 0

    def draw(self, screen):
        # create new subsurface from updated coordinate
        # draw it to the screen
        draw_pos = self.game.interpolate_draw(self.coordinate, 
                                              self.last_coordinate)
        self.vp = self.background.subsurface((draw_pos, 0, self.width,
                                              self.height))
        screen.blit(self.vp, (0,0))

class FadeAnimation():
    """ fade in/fade out screen animation """

    def __init__(self, fade_type):
        self.fade_type = fade_type
        if fade_type == "in":
            self.alpha = 255
        else:
            self.alpha = 0
        self.fade = pygame.Surface((system.SCREEN_RECT.width, system.SCREEN_RECT.height))
        self.fade.convert()
        self.fade.set_alpha(self.alpha)
        self.delay = 450
        self.speed = 300
        self.started = pygame.time.get_ticks()

    def update(self, current_time):
        active = True
        if current_time - self.started > self.delay:
            if self.fade_type == "out":
                self.alpha += self.speed * system.TIMESTEP
            else:
                self.alpha -= self.speed * system.TIMESTEP

            self.fade.set_alpha(self.alpha)

            if self.alpha < -50 or self.alpha > 300:
                active = False

        return active

    def draw(self, screen):
        screen.blit(self.fade, (0,0))

class Transition(system.State):
    """ A graphical transition state """

    def __init__(self, game, text):
        system.State.__init__(self)
        self.game = game
        self.text = text
        self.render = game.font.render(text, False, game.text_color).convert()
        self.render_x = (system.SCREEN_RECT.width - self.render.get_width()) / 2
        self.render_y = (system.SCREEN_RECT.height - self.render.get_height()) / 2
        self.text_alpha = 0
        self.render.set_alpha(self.text_alpha)
        self.duration = 4000
        self.started = pygame.time.get_ticks()
        self.done = False

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.text_alpha < 255:
            self.text_alpha += 200 * system.TIMESTEP

        if current_time - self.started > self.duration:
            pass
            
        if self.alpha > 300:
            self.done = True

        self.render.set_alpha(self.text_alpha)
        self.fade.set_alpha(self.alpha)
            
    def draw(self, screen):
        screen.blit(self.render, (self.render_x, self.render_y))
        
