import math
import arcade
from settings import WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT, PLAYER_SIZE, PLAYER_MAX_HEALTH, PLAYER_SPEED, TILE_SIZE
from map import Map

class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = 0, 0
        self.angle = 0
        self.shot = False
        self.health = PLAYER_MAX_HEALTH
        self.health_recovery_delay = 700
        self.time_prev = 0
        self.shots_fired = 0
        self.damage_taken = 0

    def set_position(self, x, y):
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE

    def recover_health(self, delta_time):
        self.time_prev += delta_time * 1000
        if self.time_prev > self.health_recovery_delay and self.health < PLAYER_MAX_HEALTH:
            self.time_prev = 0
            self.health += 1

    def check_game_over(self):
        if self.health < 1:
            self.game.state = "GAME_OVER"

    def get_damage(self, damage):
        self.health -= damage
        self.damage_taken += damage
        self.check_game_over()

    def movement(self):
        speed = PLAYER_SPEED
        dx, dy = 0, 0
        if arcade.key.W in self.game.keys_pressed:
            dy += speed
        if arcade.key.S in self.game.keys_pressed:
            dy -= speed
        if arcade.key.A in self.game.keys_pressed:
            dx -= speed
        if arcade.key.D in self.game.keys_pressed:
            dx += speed

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        new_x = self.x + dx
        new_y = self.y + dy

        corners = [
            (new_x - PLAYER_SIZE, new_y - PLAYER_SIZE),
            (new_x + PLAYER_SIZE, new_y - PLAYER_SIZE),
            (new_x - PLAYER_SIZE, new_y + PLAYER_SIZE),
            (new_x + PLAYER_SIZE, new_y + PLAYER_SIZE)
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

    def mouse_control(self):
        mx, my = self.game.mouse_pos
        self.angle = math.atan2(my - HALF_HEIGHT, mx - HALF_WIDTH)

    def update(self, delta_time):
        self.movement()
        self.mouse_control()
        self.recover_health(delta_time)

    def draw(self):
        arcade.draw_circle_filled(HALF_WIDTH, HALF_HEIGHT, PLAYER_SIZE, arcade.color.GREEN)

        arrow_size = 8
        inner_offset = 5
        tip_x = HALF_WIDTH + math.cos(self.angle) * (PLAYER_SIZE - inner_offset)
        tip_y = HALF_HEIGHT + math.sin(self.angle) * (PLAYER_SIZE - inner_offset)
        left_x = HALF_WIDTH + math.cos(self.angle - math.pi/2) * arrow_size
        left_y = HALF_HEIGHT + math.sin(self.angle - math.pi/2) * arrow_size
        right_x = HALF_WIDTH + math.cos(self.angle + math.pi/2) * arrow_size
        right_y = HALF_HEIGHT + math.sin(self.angle + math.pi/2) * arrow_size

        arcade.draw_triangle_filled(
            tip_x, tip_y,
            left_x, left_y,
            right_x, right_y,
            arcade.color.YELLOW
        )
