import pygame

# Monster class
class Monster(pygame.sprite.Sprite):
    def __init__(self, name, world,x, y, screen, walk_anim, attack_anim, move_pattern):
        """
        The Player class constructor - note that x and y is only for initialization,
        the player position will be tracked by the rect
        """
        super().__init__()
        self.name = name
        self.screen = screen
        self.world = world

        self.SCREEN_WIDTH = pygame.display.get_window_size()[0]
        self.SCREEN_HEIGHT = pygame.display.get_window_size()[1]

        # 1: back and forth continuously
        self.pattern = move_pattern 
        self.direction = 1  # right
        self.pattern_x = 0  # starting point on the left
        self.pattern_max = 100  # LIMIT ON X

        if self.pattern == 1:  # Slow walking, fast attacking
            self.speed_walking = 3
            self.speed_attacking = 5
        else:
            print(f'ERROR: move pattern {self.pattern} not recognized')
            exit(1)

        # Setting up walk animation
        self.animation = walk_anim
        self.image = walk_anim.image()
        self.width = walk_anim.ss.x_dim * walk_anim.ss.scale
        self.height = walk_anim.ss.y_dim * walk_anim.ss.scale

        # Setting up attack animation
        self.attack = attack_anim

        # Setting up death animation
        self.dead = False

        # Manual adjustments of hitbox
        self.X_ADJ = walk_anim.ss.scale * 44
        self.Y_ADJ = walk_anim.ss.scale * 18
        self.X_CENTER = 40
        self.Y_CENTER = 28

        self.rect = pygame.Rect(0,0, self.width - self.X_ADJ, self.height - self.Y_ADJ)
        self.rect_detect = pygame.Rect(0,0,0,0)
        self.rect_attack = pygame.Rect(0,0,0,0)

        self.rect.center = (x + self.X_CENTER, y + self.Y_CENTER)
        self.vel_y = 0
        self.flip = False
        self.at_bottom = False
        self.attacking = False
        self.score_flag = False  # We can only add more score when this is True
        self.prev_y_lvl = self.rect.y  # Tracking vertical progress


    def move(self, platforms):
        self.platform_group = platforms
        dx = 0
        dy = 0

        self.animation.active = True  # Always animating
        dx = self.speed_walking  #  we start at walking speed

        # Creating a detection rect where to mob will attack if the player rect collides
        flip_offset = 200
        x = self.rect.center[0]
        y = self.rect.top
        if self.flip:       
            self.rect_detect = pygame.Rect(x - flip_offset, y, 200, 100) 
        else:
            self.rect_detect = pygame.Rect(x, y, 200, 100) 

        # Creating an attack rect where to mob will kill player if player rect collides
        if self.attacking:
            # Progressom attack animation
            self.attack.anim_counter += 1
            dx = self.speed_attacking  # once we're attacking we speed up
                    
            # The attack rect is an offset from the mob rect
            flip_offset = 100
            x = self.rect.center[0]
            y = self.rect.top

            if self.flip:
                self.rect_attack = pygame.Rect(x - flip_offset, y, 90, 100) 
            else:
                self.rect_attack = pygame.Rect(x , y, 90, 100) 
            
            if self.attack.anim_counter == self.attack.frames:  # after each attack animation we stop the attack
                self.attacking = False
                self.rect_attack = self.rect
                self.attack.anim_counter = 0

        # Gravity
        self.vel_y += self.world.GRAVITY  # allows us to let mobs fall (including during death)
        dy += self.vel_y

        # Watch screen boundaries
        # Left and right
        if self.rect.left + dx < 0:
            dx = - self.rect.left
        if self.rect.right + dx > self.SCREEN_WIDTH:
            dx = self.SCREEN_WIDTH - self.rect.right

        # Check platform collision
        for platform in self.platform_group:
            # collision in the y direction only, so instead of using self.rect directly, we create
            # this temporaty rectangle with dy added for where the rectange _would_ be after the move
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width - self.X_ADJ, self.height - self.Y_ADJ):
                if self.rect.bottom < platform.rect.centery:  # Is player above platform?
                    if self.vel_y > 0 and self.dead == False:  # Is monster falling and not dead?
                        dy = 0
                        self.at_bottom = True                     
                        self.vel_y = 0
                
                if not self.dead:
                    # Very simple stay-on-platform strategy, where monster just goes back and forth
                    if self.rect.right >= platform.rect.right:  # If we hit the right limit we turn
                        self.direction = -1
                    if self.rect.left <= platform.rect.left:  # If we hit the left limit we turn
                        self.direction = 1

        # Update rectangle position
        self.rect.x += dx * self.direction
        self.rect.y += dy 

    def update(self, scroll):
        # update platform's vert pos
        self.rect.x += scroll


    def draw(self):
        self.flip = False
        if self.direction == -1: 
            self.flip = True
        # As collision detection is done with the rectangle, it's size and shape matters
        if self.attacking:
            self.image = self.attack.image()
            self.image = self.image.convert_alpha()
            self.screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))
        elif self.dead:
            # Spin sprite
            """rotate an image while keeping its center and size"""
            angle = 5
            orig_rect = self.image.get_rect()
            rot_image = pygame.transform.rotate(self.image, angle)
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            self.image = rot_image.subsurface(rot_rect).copy()
            self.screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))
        else:
            self.image = self.animation.image()
            self.image = self.image.convert_alpha()
            self.screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))

        #pygame.draw.rect(self.screen, (255,255,255), self.rect, 2 )  # Debug show rect on screen (white)