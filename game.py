#----------------------------------------------------------------------------
# Name:        Game.py
# Purpose:     instance of Game class
#
# Author:      Will Taplin
#
# Created:     30/11/2011
# Copyright:   (c) Owner 2011
# Licence:     <your licence>
#----------------------------------------------------------------------------
#!/usr/bin/env python
import engine
import states

class PsmGame(engine.system.Game):

    def __init__(self):
        engine.system.Game.__init__(self)
        self.set_caption("Protostriker M")
        self.display.init()
        self.image_manager.load_font('prstartk.ttf', 8)
        self.font = self.image_manager.get_font()
        self.text_color = (252,248,252)
        self.load_content()
        self.current_level = 1
        self.push_state(states.TitleScreenState(self), 
                        engine.graphics.FadeAnimation("in"))

    def load_content(self):
        self.image_manager.load_sheet('textborder.bmp', 'textborder',
                                           8, 8, False)
        self.image_manager.load_single('menuarrow.bmp', 'cursor', -1)
        self.image_manager.load_single('dialogarrow.bmp', 'arrow', -1)
        self.image_manager.load_sheet('ship1.bmp','ship', 32, 16, 
                                           False, -1)
        self.image_manager.load_sheet('enemy1.bmp', 'enemy1', 16, 16, 
                                           False, -1)
        self.image_manager.load_sheet('enemy2.bmp', 'enemy2', 16, 16,
                                           False, -1)
        self.image_manager.load_sheet('enemy3.bmp', 'enemy3', 24,16, 
                                           False, -1)
        self.image_manager.load_sheet('enemy4.bmp', 'enemy4', 16,16, 
                                           False, -1)
        self.image_manager.load_sheet('enemy5.bmp', 'enemy5', 32,32, 
                                           False, -1)
        self.image_manager.load_sheet('enemy6.bmp', 'enemy6', 16,16,
                                           False, -1)
        self.image_manager.load_sheet('enemy7.bmp', 'enemy7', 24,16, 
                                           False, -1)
        self.image_manager.load_single('laser.bmp', 'pshot',
                                            (255,0,255))
        self.image_manager.load_single('enemyshot.bmp', 'eshot', -1)
        self.image_manager.load_single('spreadershot.bmp', 'spreadshot', -1)
        self.image_manager.load_sheet('explosion.bmp', 'explosion', 16,16, 
                                           False, -1)
        self.image_manager.load_sheet('shrapnel.bmp', 'shrapnel', 8,8,
                                           False, (255,0,255))
        self.image_manager.load_sheet('powerups.bmp', 'powerups', 16,16, False, -1)

        # load sounds
        self.sound_manager.load_sound('cursor.wav', 'cursor',
                                           volume = 0.2)
        self.sound_manager.load_sound('select.wav', 'select',
                                           volume = 0.2)
        self.sound_manager.load_sound('blip.wav', 'blip', volume = 0.1)
        self.sound_manager.load_sound('pause.wav', 'pause')
        self.sound_manager.load_sound('enemy_exp.wav','en_exp',
                                           volume = 0.4)
        self.sound_manager.load_sound('player_exp.wav', 'pl_exp',
                                           volume = 0.4)
        self.sound_manager.load_sound('laser.wav', 'laser',
                                           volume = 0.2)
        self.sound_manager.load_sound('hit.wav', 'hit',
                                           volume = 0.4)
        self.sound_manager.load_sound('spreader.wav', 'spreader',
                                      volume = 0.4)
        self.sound_manager.load_sound('laserbeam.wav', 'laserbeam',
                                      volume = 0.3)
        self.sound_manager.load_sound('powerup.wav', 'powerup', volume = 0.5)
        self.sound_manager.load_sound('changeweapon.wav', 'changeweapon',
                                      volume = 0.5)

        
        





