
import pygame as pg

class GameTile(pg.sprite.Sprite):
	"""
	Customized Sprite class which allows update with h_scroll value, which will be triggerd by spritegroup.update(h_scroll)
	"""
	def __init__(self, size_x, size_y, x, y, surface, slope=None, slope_pos=None) -> None:
		# Inherits from basic sprite (always contains an image and a rect)
		# slope indicates if tile is not flat, and slope_pos is used for other slope angles than 45 degree, where we need
		# to know where in the multi-tile slope the current tile is
		super().__init__()
		self.image = pg.transform.scale(surface, (size_x, size_y)).convert_alpha()

		self.rect = self.image.get_rect(topleft = (x,y))

		self.solid = True  # some, like water, allows you to fall
		self.moving = False
		self.slope = slope  # if we have a slope, we put 1 for 45 degrees up slope, 2 for 22.5 degrees, and same but negative for sloping down
		self.slope_pos = slope_pos # -1 for left, 1 for right, can be extended later

	def update(self, h_scroll, v_scroll) -> None:
		# Moves the rectangle of this sprite 
		self.rect.centerx += h_scroll
		self.rect.centery += v_scroll


class GameTileAnimation(GameTile):
	"""
	Customized Sprite class which allows update with h_scroll value, which will be triggerd by spritegroup.update(h_scroll)
	Note that we do not need the surface that the parent needs to generate an image, as the animation does that for us!
	Also note taht we can have float values for x_vel and y_vel, they only get converted to int when added to x and y pos on update
	"""
	def __init__(self, size_x :int, size_y :int, x :int, y :int, animation: classmethod) -> None:
		super().__init__(size_x, size_y, x, y, pg.Surface((0,0)))
		
		self.animation = animation  # the animation generates images for us
		self.hidden = False  # we can make things invisible 

		self.image = animation.get_image()
		self.rect = self.image.get_rect(topleft = (x,y))
		self.image_tranparent = pg.Surface((size_x, size_y), pg.SRCALPHA)  # Creates an empty per-pixel alpha Surface.


		self.sprites = self.animation.sprites  # contains all sprites in the animation cycle
		self.animation.active = True

		self.x_vel = 0  # this allows us to keep track of movement speed (not pos)
		self.y_vel = 0

		self.name = ''  # This allows us to store the type (like "health potion") in this object
        
	def update(self, h_scroll, v_scroll) -> None:
		# Moves the rectangle of this sprite 
		self.rect.x += h_scroll
		self.rect.y += v_scroll
		self.rect.x += int(self.x_vel)
		self.rect.y += int(self.y_vel)
		
		if not self.hidden:
			self.image = self.animation.get_image().convert_alpha()
		else:
			self.image = self.image_tranparent

class MovingGameTile(GameTile):
	"""
	Customized Sprite class which allows self-moving tiles (like platforms) which update with h_scroll value, which will be triggerd by spritegroup.update(h_scroll)
	"""
	def __init__(self, size_x, size_y, x, y, speed, distance, surface) -> None:
		# Basic static sprite (always contains an image and a rect)
		super().__init__(size_x, size_y, x, y, surface)
		self.image = pg.transform.scale(surface, (size_x, size_y)).convert_alpha()
		self.speed = speed
		self.distance = distance
		self.moving = True
		self.direction = 1  # 1 is to the right, -1 to the left

		self.rect = self.image.get_rect(topleft = (x,y))

		self.solid = True  # some, like water, allows you to fall

		self.last_move = 0
		self.dist_moved = 0

		self.dist_player_pushed = 0
		
        
	def update(self, h_scroll, v_scroll) -> None:
		# Moves the rectangle of this sprite 
		self.rect.centerx += h_scroll
		self.rect.centery += v_scroll

		now = pg.time.get_ticks()
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

		
			


