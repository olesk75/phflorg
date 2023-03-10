import random
import pygame as pg
import logging
import copy

from game_data.settings import *
from game_data.monster_data import MonsterData


class Monster(pg.sprite.Sprite):
    def __init__(self,x, y, surface, monster_type) -> None:
        """
        The Player class constructor - note that x and y is only for initialization,
        the player position will be tracked by the rect
        """
        super().__init__()
        self.data = MonsterData(monster_type)
        self.screen = surface

        # Setting up animations
        from game_data.animation_data import anim
        self.animations = {
            'walk': copy.copy(anim[monster_type]['walk']),
            'attack': copy.copy(anim[monster_type]['attack']),
            'death': copy.copy(anim[monster_type]['death']),
            'cast': copy.copy(anim[monster_type]['cast'])
        }

        self.cast_player_pos = ()

        self.animation = self.animations['walk']  # setting active animation
        self.animation.active = True

        self.image = self.animations['walk'].get_image()
        self.width = self.animations['walk'].ss.x_dim * self.animations['walk'].ss.scale
        self.height = self.animations['walk'].ss.y_dim * self.animations['walk'].ss.scale

        # Setting up sprite's rectangle
        self.X_ADJ = self.animations['walk'].ss.scale * 44
        self.Y_ADJ = self.animations['walk'].ss.scale * 18
        self.rect = self.image.get_rect()
        self.rect.center = (x ,y)

        # Hitbox rect and sprite
        self.hitbox = pg.Rect(x,y, self.width - self.X_ADJ, self.height - self.Y_ADJ)
        
        self.rect_detect = pg.Rect(0,0,0,0)
        self.rect_attack = pg.Rect(0,0,0,0) 
   
        self.vel_x = 0
        self.vel_y = 0
        self.turned = False
        self.at_bottom = False
        self.state = WALKING  # we init in walking state
        self.last_attack = 0
        self.last_arrow = 0
        self.ready_to_attack = True  
        self.score_flag = False  # We can only add more score when this is True
        self.prev_y_lvl = self.rect.y  # Tracking vertical progress

        self.invulnerable = False  # we set this right after a hit to ensure we don't get duplicate hits
        self.stun_start = 0
        self.die_after_stun = False  # if we get stomped by the player, we get stunned, but when we land/wake, we die

        self.currently_casting = None  # if the mob is busy casting, this is what it is casting
        self.cast_anim_list = []  # if the mob casts a spell, we creat animations here

    def create_rects(self) -> None:
        """
        Creating rects for monster hitbox, detection range and attack damage range
        To cater for monster sprites of various sizes (including walk/attack/cast being different), 
        we always draw from sprite centerx and centery as reference.
        """
        # Updating the HITBOX collision rectangle
        self.hitbox = pg.Rect(self.rect.centerx - self.data.hitbox_width / 2, self.rect.centery - self.data.hitbox_height / 2, \
            self.data.hitbox_width, self.data.hitbox_height)

        # Creating a DETECTION rect where to mob will attack if the player rect collides
        x = self.rect.centerx
        y = self.rect.centery - (self.data.detection_range_high * self.rect.height / 2)  # top of rect depends if we have high detection range True or not

        width = self.data.detection_range
        height = self.rect.height / 2
        if self.data.detection_range_high:
            height = self.rect.height

        if self.turned:       
            self.rect_detect = pg.Rect(x - width, y, width, height) 
        else:
            self.rect_detect = pg.Rect(x, y,width, height) 
        
        # Creating an ATTACK rect 
        if self.state == ATTACKING:
            x = self.rect.centerx
            y = self.rect.centery
            height = self.height / 2
            if self.turned:
                self.rect_attack = pg.Rect(x - self.data.attack_range, y, self.data.attack_range, height) 
            else:
                self.rect_attack = pg.Rect(x , y, self.data.attack_range, height) 

        pg.draw.rect(self.screen, (255,255,255), self.rect, 4 )  # self.rect - WHITE
        pg.draw.rect(self.screen, (128,128,128), self.hitbox, 2 )  # Hitbox rect (grey)

    def _check_platform_collision(self, dx, dy, obstacle_sprite_group) -> None:
         #
        # Checking platform collision to prevent falling and to turn when either at end of platform or hitting a solid tile
        #
        all_obstacles = obstacle_sprite_group.sprites()
        for obstacle in all_obstacles:
            if obstacle.solid is True:
                # collision in the y direction only, using a collision rect indicating _next_ position (y + dy)
                moved_hitbox = self.hitbox.move(0, dy - 2)  # move in place, the minus 2 lifts the monsters up a few pixels
            
                if obstacle.rect.colliderect(moved_hitbox):  # we are standing on a platform essentially
                    # Preventing falling through platforms
                    if moved_hitbox.bottom > obstacle.rect.top and self.vel_y > 0:
                            dy = 0
                            self.at_bottom = True                     
                            self.vel_y = 0

                    if self.state != DEAD:  # Corpses should not fall through platforms, but also won't move to the rest here is pointless for the dead
                        # Preventing falling off left/right edge of platforms if there is NO collision (-1) to the side and down (and it's not a jumping mob
                        moved_hitbox = self.hitbox.move(-self.hitbox.width, 40)  # checking left 
                        if  moved_hitbox.collidelist(all_obstacles) == -1 and not self.data.attack_jumper:
                            self.data.direction = 1
                            self.turned = False

                        moved_hitbox = self.hitbox.move(self.hitbox.width, 40)  #checking right
                        if moved_hitbox.collidelist(all_obstacles) == -1 and not self.data.attack_jumper:
                            self.data.direction = -1
                            self.turned = True
                    
                        # Turning around if hitting a solid tile  
                        if obstacle.rect.colliderect(self.hitbox.move(dx * 5 * self.data.direction, 20).inflate(0,-60)):
                            self.data.direction *= -1
                            self.rect.x += dx * 20  * self.data.direction # far enough to avoid re-triggering in an endless loop
                            self.turned = not self.turned
                            self.vel_x = 0


    def _boss_battle(self, player) -> tuple:
        """ Movement and attacks for specific bosess 
            returns: dx and dy for mob (replaces the normal walking/bumping dx/dy for regular mobs)
        """
        dx = 0  # these are absolute moves, not speed 
        dy = 0  # speed equivalent
        
        def _casting() -> None:
            sprite_size = 32
            if self.animation.on_last_frame and self.currently_casting == 'firewalker':
                    attack_width = 12
                    for a in range(attack_width):
                        player_center_x = self.cast_player_pos[0]
                        player_bottom_y = self.cast_player_pos[1]

                        self.cast_anim_list.append(['fire', player_center_x - sprite_size * a/2, player_bottom_y - sprite_size * 2])    
                        self.cast_anim_list.append(['fire', player_center_x + sprite_size * a/2, player_bottom_y - sprite_size * 2])

                    self.state_change(WALKING)
                    self.currently_casting = ''
                

        if self.data.monster ==  'skeleton-keybearer':
            if self.state == ATTACKING:
                # Random transitions from ATTACKING to CASTING
                for attack in self.data.boss_attacks:
                    # TODO: fix self.vel_y increasing print(self.vel_y)
                    if attack['prob'] > random.random() and not player.vel_y:  # Random roll, if player not in the air
                        self.state_change(CASTING, attack_type=attack['name'], player_pos=(player.rect.centerx, player.rect.bottom))
                        dx = 0  # we stop to cast
                    else:
                        dx = self.data.speed_attacking  # if not, we just keep the attack speed
            
                        # Sometimes a jumping mob can jump if player is higher than the mob and mob is attacking
                        max_dist_centery = -7
                        player_above_mob = player.rect.centery -  (self.rect.centery + max_dist_centery)
                        if self.data.attack_jumper \
                            and player_above_mob < 20 \
                            and self.vel_y == 0 \
                            and random.random()  < 0.01:  # hardcoded jump probability
                                self.vel_y = -10

            elif self.state == CASTING:
                _casting()

            elif self.state == WALKING:
                    dx = self.data.speed_walking  #  we start at walking speed

                    # We throw in random changes in direction, different by mod type
                    if self.data.random_turns / 100  > random.random():
                        dx *= -1
                        self.data.direction *= -1
                        self.turned = not self.turned

            elif self.state == DYING:
                self.hitbox = pg.Rect(0,0,0,0)
                if self.animation.on_last_frame:
                    logging.debug(f'BOSS {self.data.monster} dies')
                    self.state = DEAD

            elif self.state == DEAD:
                self.animation.active = False

            elif self.state == STUNNED:
                # Typically only as a result of a successful player attack
                #self.stun_start = pg.time.get_ticks()
                self.animation.active = False  #  monster is frozen for the duration
                self.rect_attack = pg.Rect(0,0,0,0)  # not attacking for the duration
                self.rect_detect = pg.Rect(0,0,0,0)  # not detecting for the duration
                if pg.time.get_ticks() - self.stun_start > self.data.stun_time:
                    self.invulnerable=False
                    self.state_change(ATTACKING)

            else:
                logging.error(f'ERROR, wrong state for monster in boss fight: {self.state}')
                exit(1)

        return dx, dy

    def state_change(self, new_state:int, attack_type:str=None, player_pos:tuple=None, deadly:bool=False) -> None:
        """
        Manages all state changes for mobs, betweeh ATTACKING, WALKING and CASTING
        Can take attack type and player position if we're switching into CASTING
        (we need player pos to fire a spell at where the player was once we started casting)
        """
        if new_state != self.state:  # only do something if we have a _change_ in state
            self.state = new_state
            if new_state == ATTACKING:
                if self.ready_to_attack:  # if previous attack is done
                    self.animation = self.animations['attack']
                    self.animation.active = True

                    self.last_attack = pg.time.get_ticks()  # recording time of last attack

                    self.data.sound_attack.play()

            elif new_state == WALKING:
                    self.animation = self.animations['walk']
                    self.animation.active = True
                    self.rect_attack = pg.Rect(0,0,0,0)  # disabling attack rect

            elif new_state == CASTING:
                    self.animation = self.animations['cast']
                    self.animation.active = True
                    
                    self.currently_casting = attack_type
                    self.cast_player_pos = player_pos

                    if self.data.caster:
                        self.data.sound_cast.play()

            elif new_state == STUNNED:
                # Typically only as a result of a successful player attack
                self.data.sound_hit.play()
                self.stun_start = pg.time.get_ticks()
                self.invulnerable = True
                self.die_after_stun = bool(deadly)

                if player_pos[0] < self.rect.centerx:
                    self.data.direction = -1
                    self.turned = True
                else:
                    self.data.direction = 1
                    self.turned = False

                direction = 1 if self.turned else -1

                if not self.die_after_stun:
                    self.vel_x = 5  * self.data.direction * direction
                    self.vel_y = -5
                    self.at_bottom = False

                self.animation.active = False  #  monster is frozen for the duration
                self.rect_attack = pg.Rect(0,0,0,0)  # not attacking for the duration
                self.rect_detect = pg.Rect(0,0,0,0)  # not detecting for the duration

            elif new_state == DYING:
                    self.animation = self.animations['death']
                    self.data.sound_death.play()
                    self.animation.active = True
                    self.animation.start_over()
                    self.rect_attack = pg.Rect(0,0,0,0)
                    self.rect_detect = pg.Rect(0,0,0,0)
                    self.hitbox = pg.Rect(0,0,0,0)

            elif new_state == DEAD:
                    pass  # TODO: do we need this state for monsters?
                    

            new_rect = self.animation.get_image().get_rect()  # we need to scale back to walking image size after an attack
            new_rect.center = self.rect.center
            self.rect = new_rect

    def update(self, h_scroll, v_scroll, obstacle_sprite_group, player) -> None:
 
        # We only update postiontion and velocities of monsters who are on-screen (with some margin)      
        on_screen_x = player.rects["player"].centerx - SCREEN_WIDTH < self.rect.centerx < player.rects["player"].centerx + SCREEN_WIDTH
        on_screen_y = player.rects["player"].centery - SCREEN_HEIGHT < self.rect.centery < player.rects["player"].centery + SCREEN_HEIGHT
        on_screen = on_screen_x * on_screen_y
            
        dx = self.vel_x
        dy = self.vel_y  # Newton would be proud!

        """ Boss battles have separate logic depending on each boss - if they cast anything, we get a list of animations back as well
            the boss_battle function updates self.vel_y directly and adds self.
        """
        if self.data.boss:
            dx, dy = self._boss_battle(player)
        else:
        # Regular mobs simply walk around mostly

            if self.state == ATTACKING:
                dx += self.data.speed_attacking
            
                # Sometimes a jumping mob can jump if player is higher than the mob and mob is attacking
                #print(f'player.rect.centery: {player.rect.centery}, self.rect.center: {self.rect.centery }')
                max_dist_centery = -7
                player_above_mob = player.rect.centery -  (self.rect.centery + max_dist_centery)
                #print(f'player is this much above attacking mob: {player_above_mob}')

                if self.data.attack_jumper \
                    and player_above_mob < 0 \
                        and self.vel_y == 0 \
                        and random.random()  < 0.01:  # hardcoded jump probability
                        self.vel_y = -10

            if self.state == WALKING:
                dx = self.data.speed_walking  #  we start at walking speed

                # We throw in random changes in direction, different by mod type, as long as we're on the ground
                if self.data.random_turns / 100  > random.random() and self.vel_y == 0:
                    dx *= -1
                    self.data.direction *= -1
                    self.turned = not self.turned

            if self.state == STUNNED:
                if self.at_bottom:
                    self.vel_x = 0

                dx = self.vel_x

                if not self.die_after_stun: 
                    now = pg.time.get_ticks()
                    if now - self.stun_start > self.data.stun_time:
                        self.vel_x = 0
                        self.invulnerable = False
                        self.create_rects()        
                        self.state_change(ATTACKING)
                else: 
                    self.state_change(DYING)  # instant death if no more health


        # we compensate for scrolling
        self.rect.x += h_scroll
        self.rect.y += v_scroll

        if on_screen:
            # we compensate for gravity
            self.vel_y += GRAVITY  # gravity component gets added to the vel_y, which we add to dy at the top
            
           

            # Checking detection, hitbox and attack rects as well as platform rects for collision
        
            self.create_rects()
            self._check_platform_collision(dx, dy, obstacle_sprite_group)
            dy += self.vel_y  # TODO: supposed to help jumping for bosses, but doesn't work

            # Update rectangle position
            self.rect.x += dx * self.data.direction
            self.rect.y += dy 

        if self.state in (DEAD, DYING):
            self.rect_attack = None
            self.rect_detect = None
            self.hitbox = None
        
        # Dying, waiting for anim to run to the end
        if self.state == DYING and self.animation.on_last_frame:
            self.state_change(DEAD)


        # Updating the ready_to_attack flag 
        now = pg.time.get_ticks()
        if now - self.last_attack > self.data.attack_delay:
            self.ready_to_attack = True
        else:
            self.ready_to_attack = False


        # Get the correct image for the SpriteGroup.update()
        if self.state == CASTING:
            self.image = self.animations['cast'].get_image().convert_alpha()
            self.image = self.animations['cast'].get_image(repeat_delay = self.data.cast_delay)
        elif self.state == ATTACKING:
            # If we have a diffent size attack sprites, we need to take scale into account
            self.image = self.animations['attack'].get_image(repeat_delay = self.data.attack_delay).convert_alpha()
        elif self.state in (WALKING, STUNNED, DYING, DEAD):
            self.image = self.animation.get_image()
        else:
            logging.error(f'Monster state {self.state} unknown, aborting...')
            exit(1)
                
        self.image = pg.transform.flip(self.image, self.turned, False)        

class Projectile(pg.sprite.Sprite):
    def __init__(self,x, y, image, turned, scale = 1) -> None:
        """
        The Projector class constructor - note that x and y is only for initialization,
        the projectile position will be tracked by the rect
        NOTE: no animation - one image only!
        """
        super().__init__()
        self.image = pg.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))

        self.speed = 10
        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pg.Rect(x, y, self.width, self.height)
        self.turned = turned
        
    def update(self, h_scroll, v_scroll, platforms_sprite_group) -> None:
        
        # we set start speeds for x and y
        dx = self.speed
        if self.turned:
            dx = -self.speed
            
        dy = 0  # projectiles have no gravity

        # we compensate forscrolling
        self.rect.x += h_scroll
        self.rect.y += v_scroll

        # Update rectangle position
        self.rect.x += dx 
        self.rect.y += dy 

        # Collision with platform
        if pg.sprite.spritecollideany(self, platforms_sprite_group):
            self.kill()
        
        # Ready for super.draw()
        self.image = pg.transform.flip( self.image.convert_alpha(), self.turned, False)

class Spell(pg.sprite.Sprite):
    def __init__(self, x, y, anim, turned, scale = 1) -> None:
        """
        The Spell class constructor - note that x and y is only for initialization,
        the spell position will be tracked by the rect
        NOTE: Animation, but only _one_ animation cycle
        """
        super().__init__()
        self.anim = anim
        self.anim.active = True
        self.anim.counter = 0
        image = anim.get_image()

        self.image = pg.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))

        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pg.Rect(x, y, self.width, self.height)
        self.turned = turned

        self.anim.first_done = False
        
    def update(self, h_scroll, v_scroll) -> None:
        self.rect.x += h_scroll
        self.rect.y += v_scroll

        # Done with one cycle, as spell do not repeat (yet!)
        if self.anim.first_done:
            self.currently_casting = False
            self.kill()

        self.image = pg.transform.flip( self.anim.get_image().convert_alpha(), self.turned, False)

class Drop(pg.sprite.Sprite):
    def __init__(self, x, y, anim, turned= False, scale = 1, drop_type=None) -> None:
        """
        The Drop class constructor - object animates in place until kill()
        NOTE: continious animation
        """
        super().__init__()
        self.scale = scale
        self.drop_type = drop_type  # key, health potion etc.
        self.anim = anim
        self.anim.active = True
        self.anim.counter = 0
        image = anim.get_image()

        self.image = pg.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))

        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pg.Rect(x, y, self.width, self.height)
        self.turned = turned
        
    def update(self, h_scroll, v_scroll) -> None:
        self.rect.x += h_scroll # we compensate for h_scrolling
        self.rect.y += v_scroll # we compensate for h_scrolling

        self.image = pg.transform.flip( self.anim.get_image().convert_alpha(), self.turned, False)         
