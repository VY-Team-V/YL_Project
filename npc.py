import math
import arcade
import random
from sprite_object import AnimatedSprite
from settings import TILE_SIZE, WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT
from player import Player

class NPC(AnimatedSprite):
    def __init__(self, game, texture_path, pos=(10.5, 5.5), scale=0.6, animation_time=180):
        super().__init__(game, texture_path, pos, scale, animation_time)
        self.attack_dist = random.randint(3, 6) * TILE_SIZE
        self.speed = 1.5
        self.size = 20
        self.health = 100
        self.attack_damage = 10
        self.accuracy = 0.15
        self.alive = True
        self.pain = False
        self.frame_counter = 0
        self.color = arcade.color.WHITE

    def update(self, delta_time):
        if not self.alive:
            return
        super().update(delta_time)
        self.move_towards_player()
        self.check_attack()

    def move_towards_player(self):
        dx = self.game.player.x - self.x
        dy = self.game.player.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            if dist > self.attack_dist:
                new_x = self.x + dx * self.speed
                new_y = self.y + dy * self.speed

                corners = [
                    (new_x - self.size, new_y - self.size),
                    (new_x + self.size, new_y - self.size),
                    (new_x - self.size, new_y + self.size),
                    (new_x + self.size, new_y + self.size)
                ]

                can_move = True
                for corner_x, corner_y in corners:
                    map_x = int(corner_x / TILE_SIZE)
                    map_y = int(corner_y / TILE_SIZE)
                    if (map_x, map_y) in self.game.map.world_map:
                        can_move = False
                        break

                if can_move:
                    self.x = new_x
                    self.y = new_y

    def check_attack(self):
        dx = self.game.player.x - self.x
        dy = self.game.player.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < self.attack_dist and random.random() < 0.01:
            if random.random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def check_hit(self):
        if self.game.player.shot:
            dx = self.x - self.game.player.x
            dy = self.y - self.game.player.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < TILE_SIZE * 2:
                self.health -= self.game.weapon.damage
                self.game.player.shot = False
                self.pain = True
                if self.health <= 0:
                    self.alive = False

    def draw(self):
        if not self.alive:
            return

        screen_x = self.x - self.game.player.x + HALF_WIDTH
        screen_y = self.y - self.game.player.y + HALF_HEIGHT

        if -TILE_SIZE <= screen_x <= WIDTH + TILE_SIZE and -TILE_SIZE <= screen_y <= HEIGHT + TILE_SIZE:
            arcade.draw_circle_filled(screen_x, screen_y, self.size, self.color)

            health_width = self.size * 2 * (self.health / 100)
            arcade.draw_lbwh_rectangle_filled(
                screen_x - self.size, 
                screen_y + self.size + 5,
                self.size * 2,
                4,
                arcade.color.RED
            )
            arcade.draw_lbwh_rectangle_filled(
                screen_x - self.size, 
                screen_y + self.size + 5,
                health_width,
                4,
                arcade.color.GREEN
            )


class SoldierNPC(NPC):
    def __init__(self, game, pos=(10.5, 5.5)):
        super().__init__(game, '', pos, 0.6, 180)
        self.attack_dist = 4 * TILE_SIZE
        self.health = 100
        self.attack_damage = 10
        self.color = arcade.color.BLUE


class CacoDemonNPC(NPC):
    def __init__(self, game, pos=(10.5, 6.5)):
        super().__init__(game, '', pos, 0.7, 250)
        self.attack_dist = 2 * TILE_SIZE
        self.health = 150
        self.attack_damage = 25
        self.speed = 2.0
        self.accuracy = 0.35
        self.color = arcade.color.RED


class CyberDemonNPC(NPC):
    def __init__(self, game, pos=(11.5, 6.0)):
        super().__init__(game, '', pos, 1.0, 210)
        self.attack_dist = 6 * TILE_SIZE
        self.health = 350
        self.attack_damage = 15
        self.speed = 1.8
        self.accuracy = 0.25
        self.color = arcade.color.PURPLE
