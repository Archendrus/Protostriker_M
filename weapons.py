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
        self.default_speed = 380
        self.speed = self.default_speed # delay for creating shots
        self.speed_increment = 65
        self.max_speed = 185
        self.last_shot = 0 # time of last shot
        self.angles = [0]
        self.name = "NORMAL"
        
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

    def power_up(self):
        if self.speed > self.max_speed:
            self.speed -= self.speed_increment

class Spreader(BasicWeapon):
    """ Spreader weapon - Fire three shots simultaneously """

    def __init__(self, game):
        BasicWeapon.__init__(self, game)
        self.sound = game.sound_manager.get_sound('spreader')
        self.bullet_image = game.image_manager.get_image('spreadshot')
        self.default_speed = 575
        self.speed = self.default_speed
        self.max_speed = 380
        self.angles = [0, 10, 350]
        self.name = "SPREAD"

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
        self.angles = [0, 140, 220]
        self.name = "REVERSE"

    def get_bullet(self, player_rect, angle):
        bullet= bullets.ReverseFireBullet(player_rect.right - 24, 
                                          player_rect.centery, angle,
                                          self.bullet_image)
        return bullet

class Laser(BasicWeapon):
    """ Fires a straight laser beam that expands and 
        is attached to the player """

    def __init__(self, game):
        BasicWeapon.__init__(self, game)
        self.sound = game.sound_manager.get_sound('laserbeam')
        self.default_speed = 1250 
        self.speed = self.default_speed
        self.speed_increment = 150 
        self.max_speed = 800
        self.name = "BEAM"

    def get_bullet(self, player_rect, angle):
        bullet = bullets.LaserBeam(player_rect.right - 6,
                                   player_rect.centery - 2)
        return bullet