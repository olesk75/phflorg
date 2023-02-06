"""
monsters[]          : list of known monsters in game
MonsterAI(class)    : contains monster data
"""

import pygame
from settings import *


monsters = ['minotaur', 'ogre-archer', 'skeleton-boss', 'elven-caster', 'beholder']  # used to recognize tiles from level files - order must match tile numbering 

arrow_damage = 100

class MonsterData():
    """ Movement, detection and attack properties of monsters """
    def __init__(self, monster, movement_pattern=0) -> None:
        known_monsters = monsters
        if monster not in known_monsters:
            raise ValueError("Monster must be one of %r." % known_monsters)

        self.monster = monster

        if monster == 'minotaur':
            self.boss = False  # bosses have unique behaviour, not just wondering around
            self.caster = False
            self.direction = 1  # right
            self.hitpoints = 2  # the number of hits the mob can take before dying
            self.speed_walking = 3
            self.speed_attacking = 3
            self.detection_range = 200
            self.detection_range_high = False
            self.attack_range = 50
            self.attack_jumper = False
            self.attack_instant_damage = True  # if the mob attacks, and the player is in range, player dies
            self.attack_delay = 0  # delay between attacks (ms)
            self.attack_damage = 100
            self.points_reward = 100
            self.random_turns = 0.0
            self.hitbox_width = 65 
            self.hitbox_height = 110
            self.sound_attack = False
            self.sound_death = pygame.mixer.Sound('assets/sound/monster/minotaur/death.ogg')
            self.sound_death_volume = 0.5
            self.blood_color = pygame.Color('#ac3232')

        if monster == 'ogre-archer':
            self.boss = False
            self.caster = False
            self.direction = 1  # right
            self.hitpoints = 2
            self.speed_walking = 1
            self.speed_attacking = 0
            self.detection_range = 400
            self.attack_jumper = False
            self.detection_range_high = False
            self.attack_range = 400
            self.attack_instant_damage = False  # the mob spawns an arrow wchi the player can evade
            self.attack_delay = 2000  # delay between attacks (ms)
            self.attack_damage = 600
            self.points_reward = 150
            self.random_turns = 0.15
            self.hitbox_width = 65 
            self.hitbox_height = 110
            self.sound_attack = pygame.mixer.Sound('assets/sound/monster/ogre-archer/attack.ogg')
            self.sound_attack_volume = 0.5
            self.sound_death = pygame.mixer.Sound('assets/sound/monster/ogre-archer/death.wav') 
            self.sound_death_volume = 0.3
            self.blood_color = pygame.Color('#ac3232')
 
        if monster == 'skeleton-boss':
            self.boss = True
            self.caster = True
            self.direction = 1  # right
            self.hitpoints = 5
            self.speed_walking = 4
            self.speed_attacking = 5
            self.detection_range = 400
            self.attack_jumper = True
            self.detection_range_high = True
            self.attack_range = 150
            self.attack_instant_damage = True
            self.attack_delay = 0  # delay between attacks (ms)
            self.attack_damage = 100
            self.points_reward = 500
            self.random_turns = 0.3
            self.hitbox_width = 65
            self.hitbox_height = 110
            self.sound_attack = pygame.mixer.Sound('assets/sound/monster/skeleton-boss/roar.mp3')
            self.sound_attack_volume = 0.1
            self.sound_death = pygame.mixer.Sound('assets/sound/monster/skeleton-boss/death.wav')
            self.sound_death_volume = 1
            self.blood_color = BLACK
 
            # Boss specific
            self.boss_attacks = [('firewalker', 0.01)] 
            self.cast_delay = 2000
            self.item_drop = ['key', 'health']
            self.sound_cast = pygame.mixer.Sound('assets/sound/spell/fire-spell.aif')
            self.sound_cast_volume = 0.5

        if monster == 'elven-caster':
            self.boss = False
            self.caster = True
            self.direction = 1  # right
            self.hitpoints = 2
            self.speed_walking = 1
            self.speed_attacking = 1
            self.detection_range = 400
            self.attack_jumper = False
            self.detection_range_high = False
            self.attack_range = 400
            self.attack_instant_damage = False  # the mob spawns an arrow wchi the player can evade
            self.attack_delay = 2000  # delay between attacks (ms)
            self.attack_damage = 600
            self.points_reward = 150
            self.random_turns = 0.15
            self.hitbox_width = 65 
            self.hitbox_height = 110
            self.sound_attack = pygame.mixer.Sound('assets/sound/monster/elven-caster/attack.mp3')
            self.sound_attack_volume = 0.5
            self.sound_death = pygame.mixer.Sound('assets/sound/monster/elven-caster/death.mp3')
            self.sound_death_volume = 0.5
            self.sound_cast = pygame.mixer.Sound('assets/sound/monster/elven-caster/cast.mp3')
            self.sound_cast_volume = 0.5
            self.blood_color = pygame.Color('#ac3232')

        if monster == 'beholder':  # TODO: make unique
            self.boss = False  # bosses have unique behaviour, not just wondering around
            self.caster = False
            self.direction = 1  # right
            self.hitpoints = 3
            self.speed_walking = 3
            self.speed_attacking = 5
            self.detection_range = 200
            self.detection_range_high = False
            self.attack_range = 50
            self.attack_jumper = False
            self.attack_instant_damage = True 
            self.attack_delay = 20  # delay between attacks (ms)
            self.attack_damage = 300
            self.points_reward = 100
            self.random_turns = 0.001
            self.hitbox_width = 65 
            self.hitbox_height = 110
            self.sound_attack = False
            self.sound_attack = pygame.mixer.Sound('assets/sound/monster/beholder/attack.flac')
            self.sound_attack_volume = 0.5
            self.sound_death = pygame.mixer.Sound('assets/sound/monster/beholder/death.flac')
            self.sound_death_volume = 0.5
            self.blood_color = pygame.Color('#99e550') 