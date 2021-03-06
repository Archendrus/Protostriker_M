#-------------------------------------------------------------------------------
# Name:        System
# Purpose:     Component of Engine, contains the display class, input manager
#              state class, and state manager
# Author:      Will Taplin
#
# Created:     03/07/2011
# Copyright:   (c) Owner 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import pygame
from pygame.locals import *
import os
import graphics
import sound
import gui

""" Some notes about Framerate Independent game Updates:
This engine uses framerate independent game updates at a fixed timestep.

The basic theory is:
Instead of throttling the game loop with clock.tick(value to throttle by), We
let the game run as fast as the machine can go, but only make calls to update
the game at a fixed timestep. In my case, every 1/60 second (60 fps). All
movement and/or physics values (speed,gravity, etc) are then multiplied by 1/60
second to make them based on time, rather than framerate.  For example, sprites
will now move in pixels per second, as opposed to pixels per frame.  This is
important because framerate can vary wildly when not being throttled by
clock.tick(). Basing movement and physics updates on time ensures that the game
does not run too fast on powerful machines or too slow on older machines.
The advantage to this method is that we can draw as fast the machine can go,
thus achieving much smoother looking animation.

The basic algorithm used to acheive this is:
Measure the time passed since the last game loop (in fractions of a second)
and add it to an accumulator. If the time passed is at least 1/60 second,
update the game.  Subtract 1/60 second from the accumulator and
check again, updating until the accumulator holds less than 1/60 second.
Factor the time leftover in the accumulator into the next check for game updates
This keeps things smoother than just checking if the last loop took at
least 1/60 second.  """

SCREEN_RECT = pygame.rect.Rect(0,0,320,240)
TIMESTEP = 1 / 60.0

class Display():
    """ This class handles the initialization of pygame, the window,
        the drawing buffer.  It also handles fullscreen and window toggling
        and provides access to the the buffer in which to draw.
        Instantiate display object, and call init() to get started """
    def __init__(self):
        self.screen = None   # the actual display
        self.buffer = None  # graphics buffer
        self.res = (320,240)  # size of the game and graphics buffer
        self.window_scale = None  # scale for window size
        self.fullscreen = False
        self.fullscreen_res = (640, 480)
        self.desktop_h = None  # height of desktop, in pixels
        self.caption = None  # window caption

    def init(self):
        res = self.res

        # center for window mode
        os.environ["SDL_VIDEO_CENTERED"] = "1"

        # save the desktop res before setting mode
        desktop_h = pygame.display.Info().current_h

        # calculate scale for window mode
        window_scale_factor = desktop_h / res[1]
        self.window_res = (res[0] * window_scale_factor,
                             res[1] * window_scale_factor)

        # if scaled height is the same as desktop height, window will be cut
        # off and aspect ratio will be distorted, use one scale smaller
        #if res[1] * self.window_scale == desktop_h:
            #self.window_scale -= 1

        # display, sets resolution at 2 times the size of the game res
        #self.screen = pygame.display.set_mode((res[0] * 2, res[1] * 2),
        #                                       pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode((self.window_res[0],
                                               self.window_res[1]))

        # create a buffer that is the same size as the game resolution
        self.buffer = pygame.Surface((SCREEN_RECT.width,
                                      SCREEN_RECT.height)).convert()
        if self.fullscreen:
            self.scaled_buffer = pygame.Surface((self.fullscreen_res[0],
                                                 self.fullscreen_res[1])).convert()
        else:
            self.scaled_buffer = pygame.Surface((self.window_res[0], 
                                                 self.window_res[1])).convert()
        pygame.mouse.set_visible(False)  # turn off the mouse pointer display

        self.update()

    def update(self):
        #updates the display
        # scales the game size buffer, draws it to the screen
        if self.fullscreen:  # scale settings for fullscreen
            pygame.transform.scale(self.buffer, 
                                   (self.fullscreen_res[0],
                                    self.fullscreen_res[1]),
                                    self.scaled_buffer)
        else:  # scale settings for windowed mode
            pygame.transform.scale(self.buffer, 
                                   (self.window_res[0],
                                    self.window_res[1]),
                                    self.scaled_buffer)

        self.screen.blit(self.scaled_buffer, (0,0))
        pygame.display.flip()

    def change_mode(self):
        # toggles between fullscreen and windowed modes
        if self.fullscreen:
            pygame.display.set_caption(self.caption)
            self.screen = pygame.display.set_mode((self.window_res[0],
                                                   self.window_res[1]))
            self.scaled_buffer = pygame.Surface((self.window_res[0],
                                                 self.window_res[1])).convert()
            self.fullscreen = False
        else:
            self.screen = pygame.display.set_mode((self.fullscreen_res[0],
                                                   self.fullscreen_res[1]), 
                                                   pygame.FULLSCREEN)
            self.scaled_buffer = pygame.Surface((self.fullscreen_res[0],
                                                 self.fullscreen_res[1])).convert()
            self.fullscreen = True

    def get_screen(self):
        # get game size offscreen buffer, always draw to this surface
        return self.buffer

    def get_screen_bounds(self):
        # return the rect of the offscreen buffer
        return self.buffer.get_rect()

    def set_caption(self, caption):
        pygame.display.set_caption(caption)
        self.caption = caption


class InputManager():
    """ This class processes the pygame event queue and checks
        the bound 'buttons' for pressed and held states.
        call handle_input() every game loop to process input.
        is_pressed(button) and is_held(button) returns true if
        button is pressed or held, respectively """

    def __init__(self):
        pygame.joystick.init()
        self.redefined = False  # Start with default controls
        # dictionary of held buttons
        self.held = {'keys' : [], 'buttons' : [], 'dpad' : [], 'stick' : []}
         # dictionary of pressed buttons
        self.pressed = {'keys' : [], 'buttons' : [], 'dpad' : [], 'stick' : []}
        self.config_mode = False
        self.input_enabled = True
        self.set = [(-1, 1), (1, 1), (1, -1), (-1, -1)]
        self.gamepad_name = None
        if pygame.joystick.get_count() > 0: # if gamepad plugged in
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            self.gamepad_name = self.gamepad.get_name()

        # bound controls
        # keys are of the SNES designation to take advantage of modern
        # gamepads, values are the pygame constants for the keyboard
        # pass keys to is_pressed, is_held check for button states
        self.default_bound = {'RIGHT': [K_RIGHT, 'right'],
                              'LEFT' : [K_LEFT, 'left'],
                              'UP' : [K_UP, 'up'],
                              'DOWN' : [K_DOWN, 'down'],
                              'SELECT' : [K_QUOTE, 6],
                              'START' : [K_RETURN, 7],
                              'B' : [K_z, 0],
                              'A' : [K_x, 1],
                              'Y' : [K_a, 2],
                              'X' : [K_s, 3]}

        self.user_bound = {'RIGHT' : [],  # separate dictionary for user
                           'LEFT' : [],   # bound controls
                           'UP' : [],
                           'DOWN' : [],
                           'SELECT' : [],
                           'START' : [],
                           'B' : [],
                           'A' : [],
                           'Y' : [],
                           'X' : []}

    def process_input(self):
        if not self.config_mode:
            #reset pressed buttons every call
            self.pressed = {'keys' : [], 'buttons' : [], 'dpad' : [], 
                            'stick' : []}
            for event in pygame.event.get():
                if event.type == QUIT:
                        pygame.quit()
                        quit()
                # keypress event
                elif event.type == KEYDOWN:  
                    if event.key == K_ESCAPE:
                        #pygame.quit()
                        #quit()
                        pass
                    self.pressed['keys'].append(event.key)
                    self.held['keys'].append(event.key)
                # key release event
                elif event.type == KEYUP:   
                    if event.key in self.held['keys']:
                        self.held['keys'].remove(event.key)
                # gamepad button press event
                elif event.type == JOYBUTTONDOWN:
                    self.pressed['buttons'].append(event.button)
                    self.held['buttons'].append(event.button)
                # gamepad button release event
                elif event.type == JOYBUTTONUP:
                    if event.button in self.held['buttons']:
                        self.held['buttons'].remove(event.button)
                # d-pad
                elif event.type == JOYHATMOTION:  
                    dpad_state = []
                    if event.value[0] < 0:
                        dpad_state.append('left')
                    if event.value[0] > 0:
                        dpad_state.append('right')
                    if event.value[1] < 0:
                        dpad_state.append('down')
                    if event.value[1] > 0:
                        dpad_state.append('up')
                    self.update_dpad(dpad_state)
                # analog stick
                elif event.type == JOYAXISMOTION:
                    axis_state = []
                    if self.gamepad.get_axis(0) < -.5:
                        axis_state.append('left')
                    elif self.gamepad.get_axis(0) > .5:
                        axis_state.append('right')
                    if self.gamepad.get_axis(1) < -.5:
                        axis_state.append('up')
                    elif self.gamepad.get_axis(1) > .5:
                        axis_state.append('down')
                    self.update_stick(axis_state)

    def config_process_input(self):
        # input handling for control reconfiguration
        # checks for key/button down events and returns their value
        new_button = None
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()
                new_button = event.key
            elif event.type == JOYBUTTONDOWN:
                new_button = event.button
            elif event.type == JOYHATMOTION:
                if event.value[0] < 0:
                    new_button = 'left'
                if event.value[0] > 0:
                    new_button = 'right'
                if event.value[1] < 0:
                    new_button = 'down'
                if event.value[1] > 0:
                    new_button = 'up'
        return new_button

    def is_pressed(self, button):
        # returns true if button is pressed
        if self.redefined:  # if user has defined new controls
            if button in self.user_bound.iterkeys():
                values = self.user_bound[button]
        else:
            # if button is a bound button
            if button in self.default_bound.iterkeys():
                # get the list of bindings
                values = self.default_bound[button]

        # for each type (keyboard and gamepad)
        for key in self.pressed.iterkeys():
            # for each value in pressed
            for pressed in self.pressed[key]:
                # if pressed is found in the bindings
                if pressed in values:
                    return True
        # return false if the button passed in is not a bound button
        # or is not found in the list of pressed buttons
        return False

    def is_held(self, button):
        # returns true if a button is being held
        if self.redefined:
            if button in self.user_bound.iterkeys():
                values = self.user_bound[button]
        else:
            if button in self.default_bound.iterkeys():
                values = self.default_bound[button]

        for key in self.held.iterkeys():
            for held in self.held[key]:
                if held in values:
                    return True
        return False

    def update_dpad(self, state):
        # append string representations of gamepad hat (d-pad)
        # movements. can pass two strings in for diagonals
        self.held['dpad'] = []
        for button in state:
            self.pressed['dpad'].append(button)
            self.held['dpad'].append(button)

    def update_stick(self, state):
        self.held['stick'] = []
        for button in state:
            self.held['stick'].append(button)


    def redefine_button(self, button, new_value):
        # adds new values to user made button configuration
        button_changed = False
        if new_value not in self.set:
            self.user_bound[button].append(new_value)
            self.set.append(new_value)
            button_changed = True
        return button_changed

    def toggle_default(self):
        # switch to default controls
        self.redefined = False

    def toggle_user(self):
        # switch to user defined controls
        self.redefined = True

    def toggle_config_mode(self):
        if self.config_mode == False:
            self.config_mode = True # switch to config event loop

            # reset bound buttons and block diagonal d-pad movements
            self.set = [(-1, 1), (1, 1), (1, -1), (-1, -1)]

            # empty out all user bound controls
            self.user_bound =  {'RIGHT' : [],
                                'LEFT' : [],
                                'UP' : [],
                                'DOWN' : [],
                                'SELECT' : [],
                                'START' : [],
                                'B' : [],
                                'A' : [],
                                'Y' : [],
                                'X' : []}
        else: # returning from config mode
            self.config_mode = False

    def clear(self):
        # clear everything in input manager states
        # useful for state transitions
        self.held = {'keys' : [], 'buttons' : [], 'dpad' : []}
        self.pressed = {'keys' : [], 'buttons' : [], 'dpad' : []}

    def has_gamepad(self):
        # returns true if a gamepad is connected
        if self.gamepad_name is not None:
            return True

class State():
    """ Abstract state class, intended for inheritance
        handle_input, update, and draw all called every frame
        by the state manager """
    def __init__(self, game):
        self.game = game
        self.is_exiting = False
        self.done_exiting = False
        self.show_message = False
        self.transitioning = False

    def load_content(self):
        # load images and sounds for the state here
        pass

    def unload_content(self):
        # unload images and sounds that will not be used
        # again
        pass

    def activate(self, transition):
        # called once when the state is first pushed
        # useful for starting music, sound effects, etc.
        # transition is either a transition object passed from game, or None
        
        # if state is a transitioning state, set transitioning flag,
        # create transition
        if transition is not None:
            self.transitioning = True
            self.transition = transition
        else:  # no transition
            self.transitioning = False

    def reactivate(self, transition):
        # called once when a previous active state is
        # made active again.
        # transition is either a transition object passed from game, or None
        
        # if state has an animation on reactivation, set transitioning flag,
        # create transition
        if transition is not None:
            self.transitioning = True
            self.transition = transition
        else: # no transition
            self.transitioning = False

    def transition_off(self, transition):
        # start the transition off process
        self.transition = transition
        self.transitioning = True
        self.is_exiting = True

    def handle_input(self):
        # All objects that process input should have their handle_input()
        # functions called here
        pass

    def update(self):
        # All objects that update should have their update() functions
        # called here

        # handle transition animations 
        if self.transitioning:
            self.transitioning = self.transition.update(pygame.time.get_ticks())

        # transition is done or non-existant and state is set to exit,
        # indicate the state has finished exiting and new state can begin
        if not self.transitioning and self.is_exiting:
            self.done_exiting = True

    def draw(self):
        # All objects that draw should have their draw() functions called
        # here
        pass

class Game():
    """ game class - Contains all managers, initializes pygame
        and runs a game loop """
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        self.paused = False
        self.display = Display()
        self.image_manager = graphics.ImageManager()
        self.sound_manager = sound.SoundManager()
        self.menu_manager = gui.MenuManager()
        self.input_manager = InputManager()
        self.states = []
        self.initial_state = None
        self.clock = pygame.time.Clock()
        self.accumulator = 0.0
        self.alpha = 0.0

    def set_caption(self, caption):
        # set the window title bar to caption
        self.display.set_caption(caption)

    def load_content(self):
        # load content for the entire game
        pass

    def get_current_state(self):
        # get state at the top of the stack
        return self.states[-1]

    def push_state(self, state, transition = None):
        # push a new state onto the stack
        self.states.append(state)
        state.activate(transition)

    def pop_state(self, transition = None):
        # remove and return state on the top of the stack
        self.states.pop()
        self.get_current_state().reactivate(transition)

    def change_state(self, state, transition = None):
        # replace the current top state with state
        while self.states:
            self.get_current_state().unload_content()
            self.states.pop()
        state.load_content()
        self.states.append(state)
        state.activate(transition)

    def interpolate_draw(self, current, last, boss_level):
        # returns an interpolated draw position

        if not self.paused:
            draw_pos = current * self.alpha + last * (1.0 - self.alpha)
            # if in boss level, background is not scrolling, always return 0
            if boss_level:
                draw_pos = 0
        else: # if paused return the last coordinate passed in
           draw_pos = current
        return draw_pos

    def run(self):
        current_state = self.get_current_state()
        while(current_state):
            # check for state change
            current_state = self.get_current_state()
       
            # get time passed since last frame (in seconds)
            tick = self.clock.tick() / 1000.0
            # cap the max frame time
            if tick > 0.25:
                tick = 0.25
            # add frame time to accumulator
            self.accumulator += tick

            # process input events
            self.input_manager.process_input()

            # pass input to state if not transitioning
            if not current_state.transitioning:
                current_state.handle_input()

            # update the game in TIMESTEP increments
            # if frame time was long, update as many times as needed 
            # to catch up
            while self.accumulator >= TIMESTEP:
                current_state.update()
                self.accumulator -= TIMESTEP
            
            # store alpha for interpolated draws
            self.alpha = self.accumulator / TIMESTEP
            
            # draw all states
            for state in self.states:
                state.draw(self.display.get_screen())

            # scale and flip the buffer
            self.display.update()

    def quit(self):
        # close the game
        pygame.quit()
        quit()



