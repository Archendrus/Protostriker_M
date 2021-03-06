#-------------------------------------------------------------------------------
# Name:        SpriteManager.py
# Purpose:     Contains the SpriteManager class, subclass of
#              engine.objects.SpriteManager.
#
# Author:      Will Taplin
#
# Created:     12/12/2011
# Copyright:   (c) Owner 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import os
import pygame
from pygame.locals import *
import engine
import enemies

class SpriteManager(engine.objects.SpriteManager):
    """ Container for all game sprite groups and their sprites.
    Can update and draw all groups with respective methods.
    Also handles the loading of level files and the creation of enemies """
    def __init__(self, game):
        engine.objects.SpriteManager.__init__(self)
        # Create all sprite groups and add them to
        # self.objects
        self.game = game
        player_group = pygame.sprite.Group()
        enemy_group = pygame.sprite.Group()
        player_shots = pygame.sprite.Group()
        enemy_shots = pygame.sprite.Group()
        powerups_group = pygame.sprite.Group()
        explosion_group = pygame.sprite.Group()
        self.add_group(enemy_group, 'enemy_group')
        self.add_group(player_shots, 'player_shots')
        self.add_group(enemy_shots, 'enemy_shots')
        self.add_group(explosion_group, 'explosions')
        self.add_group(powerups_group, 'powerups')
        self.add_group(player_group, 'player_group')
        self.enemy_queue = [] # list of offscreen enemies
        self.update_order = ['player_group',  'enemy_group', 'player_shots',
                             'enemy_shots', 'powerups', 'explosions']
        self.draw_order = ['player_shots','player_group', 'enemy_group', 
                           'powerups', 'explosions','enemy_shots']

    def update(self, current_time, viewport, player_rect):
        # update all sprites in the game
        # step through self.objects and call
        # each groups update method

        for key in self.update_order:
            for sprite in self.sprites[key]:
                enemy_bullet = sprite.update(current_time, player_rect, self.game)
                if enemy_bullet is not None:
                    self.add_sprite(enemy_bullet, 'enemy_shots')

        # spawn enemies
        # check each enenmy's dx against level_pos
        # Get index of enemy to spawn, pop it from the
        # queue, call enemy's spawn method, and add it
        # to the enemy group for update and draw
        for enemy in self.enemy_queue:
            if isinstance(enemy, enemies.Boss):
                self.enemy_queue.remove(enemy)
                enemy.spawn(current_time)
                self.add_sprite(enemy, 'enemy_group')

            elif viewport.level_pos + viewport.width >= enemy.dx:
                 index = self.enemy_queue.index(enemy)
                 spawn_enemy = self.enemy_queue.pop(index)
                 spawn_enemy.spawn(current_time)
                 self.add_sprite(spawn_enemy, 'enemy_group')

    def check_collisions(self, player):
        # check for each type of collsion, update appropriately

        player_die = False

        # Check for player collision and player shot collision
        # with all enemies onscreen
        for enemy in self.sprites['enemy_group']:
            # check player collision with enemy
            for box in enemy.hitbox:
                if player.hitbox.colliderect(box) and \
                not player.protected:
                    # kill the enemy and player, create explosions
                    # at their positions.
                    self.sprites['player_shots'].empty()
                    player_ex = player.explode()
                    if not self.game.boss_level: # boss does not die on collision
                        enemy.kill()
                        enemy_ex, powerup = enemy.explode()
                        self.add_sprite(enemy_ex, 'explosions')
                    self.add_sprite(player_ex, 'explosions')
                    player_die = True
            for bullet in self.sprites['player_shots']:
                # check player shot collision with 
                for box in enemy.hitbox:
                    if bullet.hitbox.colliderect(box):
                        # decrement enemy.hits if multi-hit enemy
                        if enemy.hits > 0:
                            # double damage if bullet is beam
                            if bullet.destroyable:
                                damage = 1
                            else:
                                damage = 2
                            # kill player shot to avoid one bullet registering 
                            # multiple hits
                            bullet.kill()
                            # Hack ass way to check if boss hurtbox
                            if self.game.boss_level:
                                if box.width != 7:  # boss hurtbos has width 7
                                    enemy.hit(0)  # no hit
                                else:
                                    enemy.hit(damage)
                            else:
                                enemy.hit(damage)
                        else: # enemy destroyed
                            # let the laser beam pass through enemies
                            if bullet.destroyable:
                                bullet.kill()
                            # kill the enemy, get an explosion sprite, and 
                            # a powerup on change
                            ex, powerup = enemy.explode()
                            # add the explosion sprite
                            for sprite in ex:
                                self.add_sprite(sprite,'explosions')
                            # add the powerup if you get one
                            if powerup is not None:
                                self.add_sprite(powerup, 'powerups')
                            player.score += enemy.points

        # check for shrapnel explosion collision with player
        for shrapnel in self.sprites['explosions']:
            if shrapnel.hitbox is not None:
                if shrapnel.hitbox.colliderect(player.hitbox) and \
                not player.respawning and not player.protected:
                    player_ex = player.explode()
                    self.add_sprite(player_ex, 'explosions')
                    player_die = True

        # check enemy bullet collision with player
        for bullet in self.sprites['enemy_shots']:
            if bullet.hitbox.colliderect(player.hitbox) and \
            not player.protected:
                bullet.kill()
                player_ex = player.explode()
                self.add_sprite(player_ex, 'explosions')
                player_die = True

        for powerup in self.sprites['powerups']:
            if player.hitbox.colliderect(powerup.hitbox):
                type = powerup.collect()
                player.power_up(type)

        # return True if player has died
        return player_die
    
    def boss_destoyed(self):
        # Returns true if boss is completely destroyed
        # (Boss sprite is destroyed and shrapnel pieces gone)
        destroyed = False
        if self.game.boss_level:
            if len(self.sprites['enemy_group']) == 0:
                self.game.sound_manager.music_control("stop")
                if len(self.sprites['explosions']) == 0:
                    destroyed = True
        return destroyed


    def load_level(self, game, filename):
        # Load a level consisting of enemy types and x,y
        # coords.
        enemy_data = [] # list of strings parsed in

        # create platform independent path, open
        # file if available.
        fullname = os.path.join('res', 'levels', filename)
        try:
            level = open(fullname, "r")
        except IOError:
            print 'Cannot load level:', filename
            raise SystemExit

        # Read each line in the file
        for line in level:
            for word in line.split():
                enemy_data.append(word)

            # Read each data element and store their
            # associated values in temp variables.
            # At end_enemy, pass temp variables to create enemy
            for element in enemy_data:
                next_index = enemy_data.index(element) + 1
                if element == 'type':
                    # Data to read is at next index
                    enemy_type = enemy_data[next_index]
                elif element == 'x':
                    x = int(enemy_data[next_index])
                elif element == 'y':
                    y = int(enemy_data[next_index])
                elif element == 'has_powerup':
                    if enemy_data[next_index] == 'True':
                        has_powerup = True 
                    else:
                        has_powerup = False
                elif element == 'end_enemy':
                    self.create_enemy(game, enemy_type, x, y, has_powerup)
                    enemy_data = []  # reset the list

        # close the level file
        level.close()

    def create_enemy(self, game, enemy_type, x, y, has_powerup):
        # Creates an enemy of enemy_type at x, y

        # flip images if left to right enemy       
        flipped_enemies = ['enemy_08', 'enemy_09', 'enemy_10']
        if enemy_type in flipped_enemies:
            if enemy_type == 'enemy_08':
                images = list(game.image_manager.get_image('enemy_01'))
            elif enemy_type == 'enemy_09':
                images = list(game.image_manager.get_image('enemy_03'))
            elif enemy_type == 'enemy_10':
                images = list(game.image_manager.get_image('enemy_06'))
            for i in xrange(0, len(images)):
                images[i] = pygame.transform.flip(images[i], True, False)
        else: # right to left enemy, use normal images
             images = game.image_manager.get_image(enemy_type)
            

        # create appropriate enemy depending on enemy_type
        if enemy_type == 'enemy_01':
            enemy = enemies.Enemy1(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_02':
            enemy = enemies.Enemy2(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_03':
            enemy = enemies.Enemy3(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_04':
            enemy = enemies.Enemy4(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_05':
            enemy = enemies.Enemy5(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_06':
            enemy = enemies.Enemy6(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_07':
            enemy = enemies.Enemy7(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_08':
            enemy = enemies.Enemy8(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_09':
            enemy = enemies.Enemy9(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_10':
            enemy = enemies.Enemy10(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_11':
            enemy = enemies.Enemy11(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_12':
            enemy = enemies.Enemy12(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_13':
            enemy = enemies.Enemy13(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_14':
            enemy = enemies.Enemy14(game, x, y, has_powerup, images)
        elif enemy_type == 'enemy_15':
            enemy = enemies.Enemy15(game, x, y, has_powerup, images)
        elif enemy_type == 'boss':
            enemy = enemies.Boss(game, x, y, has_powerup, images)

        # Add enemy to enemy queue
        self.enemy_queue.append(enemy)


