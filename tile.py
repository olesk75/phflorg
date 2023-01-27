
import pygame

class GameTile(pygame.sprite.Sprite):
	"""
	Customized Sprite class which allows update with scroll value, which will be triggerd by spritegroup.update(scroll)
	"""
	def __init__(self, size_x, size_y, x, y, surface) -> None:
		# Basic static sprite (always contains an image and a rect)
		super().__init__()
		self.image = pygame.transform.scale(surface, (size_x, size_y)).convert_alpha()

		self.rect = self.image.get_rect(topleft = (x,y))

		self.solid = True  # some, like water, allows you to fall
		self.moving = False
        
	def update(self, scroll) -> None:
		# Moves the rectangle of this sprite 
		self.rect.centerx += scroll


class GameTileAnimation(GameTile):
	"""
	Customized Sprite class which allows update with scroll value, which will be triggerd by spritegroup.update(scroll)
	"""
	def __init__(self, size_x, size_y, x, y, surface, animation) -> None:
		super().__init__(size_x, size_y, x, y, surface)
		
		self.animation = animation  # the animation generates images for us

		self.image = animation.get_image()
		self.rect = self.image.get_rect(topleft = (x,y))

		self.sprites = self.animation.sprites  # contains all sprites in the animation cycle
		self.animation.active = True
        
	def update(self, scroll) -> None:
		# Moves the rectangle of this sprite 
		self.rect.x += scroll
		self.image = self.animation.get_image().convert_alpha()

class MovingGameTile(GameTile):
	"""
	Customized Sprite class which allows update with scroll value, which will be triggerd by spritegroup.update(scroll)
	"""
	def __init__(self, size_x, size_y, x, y, speed, distance, surface) -> None:
		# Basic static sprite (always contains an image and a rect)
		super().__init__(size_x, size_y, x, y, surface)
		self.image = pygame.transform.scale(surface, (size_x, size_y)).convert_alpha()
		self.speed = speed
		self.distance = distance
		self.moving = True
		self.direction = 1  # 1 is to the right, -1 to the left

		self.rect = self.image.get_rect(topleft = (x,y))

		self.solid = True  # some, like water, allows you to fall

		self.last_move = 0
		self.dist_moved = 0

		self.dist_player_pushed = 0
		
        
	def update(self, scroll) -> None:
		# Moves the rectangle of this sprite 
		self.rect.centerx += scroll

		now = pygame.time.get_ticks()
		if now - self.last_move > 30:
			self.last_move = now
			# print(f'{self.rect.centerx=}, {self.x_start_pos=} {self.distance=}')
			self.dist_moved += self.speed
			self.rect.centerx += self.speed * self.direction
			
			
			self.dist_player_pushed += self.speed * self.direction
			
			if abs(self.dist_player_pushed) > self.speed:  # if we accumulate, it means the player is not on the platform
				self.dist_player_pushed = 0
				
			if self.dist_moved >= self.distance:
				self.dist_moved = 0
				self.direction *= -1

		
			

