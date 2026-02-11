from collections import deque
from functools import lru_cache
from settings import TILE_SIZE

class SpriteObject:
    def __init__(self, game, texture, pos=(10.5, 3.5), scale=0.7):
        self.game = game
        self.player = game.player
        self.x, self.y = pos[0] * TILE_SIZE, pos[1] * TILE_SIZE
        self.width = 30
        self.height = 30

    def draw(self):
        pass


class AnimatedSprite(SpriteObject):
    def __init__(self, game, texture_path, pos=(11.5, 3.5), scale=0.8, animation_time=120):
        super().__init__(game, texture_path, pos, scale)
        self.animation_time = animation_time
        self.animation_time_prev = 0
        self.current_image = 0

    def update(self, delta_time):
        self.animation_time_prev += delta_time * 1000
        if self.animation_time_prev > self.animation_time:
            self.animation_time_prev = 0
            self.current_image = (self.current_image + 1) % 4
