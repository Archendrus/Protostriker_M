#-----------------------------------------------------------------------------
#  weapons.py
#  contains all the classes for different player weapons
#-----------------------------------------------------------------------------
import bullets

class BasicWeapon():
    """ The players basic weapon - fires a single shot at a time """

    def __init__(self, game):
        self.sound = game.sound_manager.get_sound('laser')
        self.bullet_image = game.image_manager.get_image('pshot')
        self.speed = 200 # delay for creating shots
        self.last_shot = 0 # time of last shot
        self.angles = [0]
        
    def fire(self, current_time, player_rect):
        shots = []
        if current_time - self.last_shot > self.speed:
            for angle in self.angles:
                shot = self.get_bullet(player_rect, angle)
                shots.append(shot)
            self.sound.play()
            self.last_shot = current_time
        return shots

    def get_bullet(self, player_rect, angle):
        bullet = bullets.BasicBullet(player_rect.right - 6,
                                     player_rect.centery, angle,  
                                     self.bullet_image)
        return bullet

class Spreader(BasicWeapon):
    """ Spreader weapon - Fire three shots simultaneously """

    def __init__(self, game):
        BasicWeapon.__init__(self, game)
        self.sound = game.sound_manager.get_sound('spreader')
        self.bullet_image = game.image_manager.get_image('spreadshot')
        self.speed = 400
        self.angles = [0, 10, 350]

    def get_bullet(self, player_rect, angle):
        bullet = bullets.SpreaderBullet(player_rect.right - 6,
                                      player_rect.centery, angle,
                                      self.bullet_image)
        return bullet


class ReverseFire(BasicWeapon):
    """ fires a single straight shot and two reverse shots at an angle """

    def __init__(self, game):
        BasicWeapon.__init__(self, game)
        self.sound = game.sound_manager.get_sound('laser')
        self.bullet_image = game.image_manager.get_image('pshot')
        self.speed = 200
        self.angles = [0, 140, 220]

    def get_bullet(self, player_rect, angle):
        bullet= bullets.ReverseFireBullet(player_rect.right - 24, 
                                          player_rect.centery, angle,
                                          self.bullet_image)
        return bullet