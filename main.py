import arcade
import csv
import os
import math
import random
from collections import deque
from functools import lru_cache

# Константы
RES = WIDTH, HEIGHT = 1600, 900
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 60
PLAYER_START_POSITIONS = {
    0: (1.5, 5),
    1: (1.5, 1.5),
    2: (1.5, 1.5)
}
PLAYER_SPEED = 3
PLAYER_SIZE = 20
PLAYER_MAX_HEALTH = 100
MOUSE_SENSITIVITY = 0.3
FLOOR_COLOR = (30, 30, 30)
MENU_BG_COLOR = (20, 20, 40)
MENU_TEXT_COLOR = (255, 255, 255)
MENU_HIGHLIGHT_COLOR = (255, 50, 50)
TILE_SIZE = 64
NUM_RAYS = WIDTH // 2
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = math.pi / 3 / NUM_RAYS
MAX_DEPTH = 20

castle_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 3, 3, 3, 3, 0, 0, 0, 2, 2, 2, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 2, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 2, 0, 0, 1],
    [1, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 4, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 3, 1, 3, 1, 1, 1, 3, 0, 0, 3, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 0, 3, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 0, 3, 1, 1, 1],
    [1, 1, 3, 1, 1, 1, 1, 1, 1, 3, 0, 0, 3, 1, 1, 1],
    [1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 0, 0, 0, 3, 4, 0, 4, 3, 0, 1],
    [1, 0, 0, 5, 0, 0, 0, 0, 0, 0, 3, 0, 3, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 4, 0, 0, 0, 0, 0, 0, 4, 0, 0, 4, 0, 0, 0, 1],
    [1, 1, 3, 3, 0, 0, 3, 3, 1, 3, 3, 1, 3, 1, 1, 1],
    [1, 1, 1, 3, 0, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 3, 4, 0, 0, 4, 3, 3, 3, 3, 3, 3, 3, 3, 1],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
]

maze_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 3, 0, 0, 0, 4, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 3, 0, 0, 0, 2, 0, 0, 0, 4, 0, 0, 0, 5, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 3, 0, 0, 0, 4, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1],
    [1, 0, 5, 0, 0, 0, 2, 0, 0, 0, 4, 0, 0, 0, 3, 1],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 2, 0, 0, 0, 3, 0, 0, 0, 4, 0, 0, 0, 5, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

military_base_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 2, 2, 2, 0, 0, 3, 3, 3, 3, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 2, 0, 0, 3, 0, 0, 3, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 2, 0, 0, 3, 0, 0, 3, 0, 0, 1],
    [1, 0, 0, 2, 2, 2, 2, 0, 0, 3, 3, 3, 3, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 4, 4, 4, 4, 0, 0, 5, 5, 5, 5, 0, 0, 1],
    [1, 0, 0, 4, 0, 0, 4, 0, 0, 5, 0, 0, 5, 0, 0, 1],
    [1, 0, 0, 4, 0, 0, 4, 0, 0, 5, 0, 0, 5, 0, 0, 1],
    [1, 0, 0, 4, 4, 4, 4, 0, 0, 5, 5, 5, 5, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

MAPS = {0: castle_map, 1: maze_map, 2: military_base_map}


class Map:
    def __init__(self, game, map_id=0):
        self.game = game
        self.map_id = map_id
        self.mini_map = MAPS[map_id]
        self.world_map = {}
        self.rows = len(self.mini_map)
        self.cols = len(self.mini_map[0])
        self.get_map()
    
    def get_map(self):
        for j, row in enumerate(self.mini_map):
            for i, value in enumerate(row):
                if value:
                    self.world_map[(i, j)] = value


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
                # Проверка коллизии перед движением (с учётом размера врага)
                new_x = self.x + dx * self.speed
                new_y = self.y + dy * self.speed
                
                # Проверяем 4 точки вокруг врага (учитывая его размер)
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
            
            # Индикатор здоровья
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


class ObjectHandler:
    def __init__(self, game, map_id=0):
        self.game = game
        self.map_id = map_id
        self.sprite_list = []
        self.npc_list = []
        self.shot_effects = []
        self.fixed_npc_positions = self.get_fixed_npc_positions()
        self.spawn_fixed_npc()
        self.setup_sprites()
    
    def get_fixed_npc_positions(self):
        if self.map_id == 0:
            return [
                {'type': SoldierNPC, 'pos': (3.5, 3.5)},
                {'type': SoldierNPC, 'pos': (12.5, 5.5)},
                {'type': CacoDemonNPC, 'pos': (8.5, 8.5)},
                {'type': SoldierNPC, 'pos': (5.5, 12.5)},
                {'type': CyberDemonNPC, 'pos': (14.5, 14.5)}
            ]
        elif self.map_id == 1:
            return [
                {'type': SoldierNPC, 'pos': (3.5, 2.5)},
                {'type': SoldierNPC, 'pos': (12.5, 2.5)},
                {'type': CacoDemonNPC, 'pos': (7.5, 7.5)},
                {'type': SoldierNPC, 'pos': (2.5, 12.5)},
                {'type': CyberDemonNPC, 'pos': (12.5, 12.5)}
            ]
        elif self.map_id == 2:
            return [
                {'type': SoldierNPC, 'pos': (4.5, 4.5)},
                {'type': SoldierNPC, 'pos': (11.5, 4.5)},
                {'type': CacoDemonNPC, 'pos': (4.5, 11.5)},
                {'type': SoldierNPC, 'pos': (11.5, 11.5)},
                {'type': CyberDemonNPC, 'pos': (8.5, 8.5)}
            ]
        return []

    def spawn_fixed_npc(self):
        for npc_data in self.fixed_npc_positions:
            npc_type = npc_data['type']
            pos = npc_data['pos']
            self.add_npc(npc_type(self.game, pos))

    def setup_sprites(self):
        pass

    def check_win(self):
        alive_enemies = [npc for npc in self.npc_list if npc.alive]
        if not alive_enemies and self.game.state == "PLAYING":
            self.game.state = "WIN"

    def add_shot_effect(self, x, y):
        self.shot_effects.append({'x': x, 'y': y, 'size': 20, 'alpha': 255, 'life': 0.3})

    def update(self, delta_time):
        for sprite in self.sprite_list:
            if isinstance(sprite, AnimatedSprite):
                sprite.update(delta_time)
        for npc in self.npc_list:
            npc.update(delta_time)
        
        for effect in self.shot_effects[:]:
            effect['life'] -= delta_time
            effect['size'] += 100 * delta_time
            effect['alpha'] = int(255 * (effect['life'] / 0.3))
            if effect['life'] <= 0:
                self.shot_effects.remove(effect)
        
        self.check_win()

    def draw(self):
        for effect in self.shot_effects:
            arcade.draw_circle_filled(
                effect['x'], 
                effect['y'], 
                effect['size'], 
                (255, 255, 200, effect['alpha'])
            )
        
        for npc in self.npc_list:
            if npc.alive:
                npc.draw()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)


class Weapon(AnimatedSprite):
    def __init__(self, game):
        super().__init__(game, '', scale=0.4, animation_time=90)
        self.reloading = False
        self.frame_counter = 0
        self.damage = 50
    
    def animate_shot(self, delta_time):
        if self.reloading:
            self.update(delta_time)
            self.frame_counter += 1
            if self.frame_counter >= 4:
                self.reloading = False
                self.frame_counter = 0

    def draw(self):
        pass


class PathFinding:
    def __init__(self, game):
        self.game = game
        self.map = game.map.mini_map
        self.ways = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (1, 1), (-1, 1)]
        self.graph = {}
        self.get_graph()
    
    @lru_cache(maxsize=None)
    def get_path(self, start, goal):
        visited = self.bfs(start, goal)
        path = [goal]
        step = visited.get(goal, start)
        while step and step != start:
            path.append(step)
            step = visited[step]
        return path[-1] if path else start

    def bfs(self, start, goal):
        queue = deque([start])
        visited = {start: None}
        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break
            next_nodes = self.graph.get(cur_node, [])
            for next_node in next_nodes:
                if next_node not in visited:
                    queue.append(next_node)
                    visited[next_node] = cur_node
        return visited

    def get_next_nodes(self, x, y):
        return [(x + dx, y + dy) for dx, dy in self.ways if (x + dx, y + dy) not in self.game.map.world_map]

    def get_graph(self):
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if not col:
                    self.graph[(x, y)] = self.get_next_nodes(x, y)


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

        # Проверка коллизии с учётом радиуса игрока (PLAYER_SIZE)
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Проверяем 4 угла вокруг игрока (с учётом радиуса)
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
        # Круг игрока
        arcade.draw_circle_filled(HALF_WIDTH, HALF_HEIGHT, PLAYER_SIZE, arcade.color.GREEN)
        
        # Треугольник ВНУТРИ круга (не выходит за границы)
        arrow_size = 8  # Уменьшенный размер
        inner_offset = 5  # Смещение внутрь круга
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


class Game(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "Doom-Style Shooter")
        self.state = "MAIN_MENU"
        self.selected_map = 0
        self.maps = ["Замок", "Лабиринт", "Военная база"]
        self.total_kills = 0
        self.time_played = 0
        self.start_time = 0
        self.current_score = 0
        self.main_menu_items = ["Выбор карты", "Рекорды", "Выход"]
        self.selected_menu_item = 0
        self.selected_map_item = 0
        self.high_scores_file = "high_scores.csv"
        self.high_scores = self.load_high_scores()
        self.score_saved_this_game = False
        self.mouse_pos = (0, 0)
        self.keys_pressed = set()
        self.map = None
        self.player = None
        self.object_handler = None
        self.weapon = None
        self.pathfinding = None
        arcade.set_background_color(arcade.color.BLACK)
    
    def load_high_scores(self):
        scores = []
        try:
            if os.path.exists(self.high_scores_file):
                with open(self.high_scores_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        row['score'] = int(row['score'])
                        scores.append(row)
        except Exception:
            pass
        return scores

    def save_high_score(self):
        score_data = {'score': self.current_score}
        self.high_scores.append(score_data)
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        self.high_scores = self.high_scores[:3]
        try:
            with open(self.high_scores_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['score']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.high_scores)
        except Exception:
            pass

    def is_new_high_score(self):
        if not self.high_scores:
            return True
        if len(self.high_scores) < 3:
            return True
        min_score = min(score['score'] for score in self.high_scores)
        return self.current_score > min_score

    def new_game(self, map_id=0):
        self.map = Map(self, map_id)
        start_pos = PLAYER_START_POSITIONS.get(map_id, (1.5, 5))
        self.player = Player(self)
        self.player.set_position(*start_pos)
        self.object_handler = ObjectHandler(self, map_id)
        self.weapon = Weapon(self)
        self.pathfinding = PathFinding(self)
        self.total_kills = 0
        self.start_time = 0
        self.time_played = 0
        self.current_score = 0
        self.score_saved_this_game = False

    def calculate_score(self):
        kill_points = self.total_kills * 100
        time_bonus = max(0, 300 - self.time_played) * 10
        health_bonus = self.player.health * 2
        total = kill_points + time_bonus + health_bonus
        return int(total)

    def on_draw(self):
        self.clear()
        
        if self.state == "PLAYING":
            self.draw_game()
        elif self.state == "MAIN_MENU":
            self.draw_main_menu()
        elif self.state == "MAP_SELECT":
            self.draw_map_select()
        elif self.state == "HIGH_SCORES":
            self.draw_high_scores()
        elif self.state == "LOADING":
            self.draw_loading_screen()
        elif self.state == "GAME_OVER":
            self.draw_game_over_screen()
        elif self.state == "WIN":
            self.draw_win_screen()

    def draw_game(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, WIDTH, HEIGHT, FLOOR_COLOR)
        for (x, y), texture_id in self.map.world_map.items():
            screen_x = x * TILE_SIZE - self.player.x + HALF_WIDTH
            screen_y = y * TILE_SIZE - self.player.y + HALF_HEIGHT
            if -TILE_SIZE <= screen_x <= WIDTH + TILE_SIZE and -TILE_SIZE <= screen_y <= HEIGHT + TILE_SIZE:
                color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)][(texture_id - 1) % 5]
                arcade.draw_lbwh_rectangle_filled(
                    screen_x - TILE_SIZE // 2,
                    screen_y - TILE_SIZE // 2,
                    TILE_SIZE,
                    TILE_SIZE,
                    color
                )
        self.object_handler.draw()
        self.player.draw()
        self.draw_hud()

    def draw_hud(self):
        arcade.draw_text(f"Здоровье: {self.player.health}", 10, HEIGHT - 30, arcade.color.WHITE, 20, anchor_x="left")
        arcade.draw_text(f"Убито: {self.total_kills}", 10, HEIGHT - 60, arcade.color.WHITE, 20, anchor_x="left")
        arcade.draw_text(f"Время: {int(self.time_played)} сек.", 10, HEIGHT - 90, arcade.color.WHITE, 20, anchor_x="left")
        arcade.draw_text(f"Очки: {int(self.current_score)}", 10, HEIGHT - 120, arcade.color.WHITE, 20, anchor_x="left")

    def draw_main_menu(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, WIDTH, HEIGHT, MENU_BG_COLOR)
        arcade.draw_text("DOOM STYLE SHOOTER", HALF_WIDTH, HEIGHT - 150, arcade.color.RED, 74, anchor_x="center")
        for i, item in enumerate(self.main_menu_items):
            color = arcade.color.YELLOW if i == self.selected_menu_item else arcade.color.LIGHT_GRAY
            arcade.draw_text(item, HALF_WIDTH, HEIGHT - 350 - i * 100, color, 48, anchor_x="center")
        arcade.draw_text("Управление: ↑↓ - выбор, ENTER - подтвердить, ESC - выход", 
                        HALF_WIDTH, 100, arcade.color.LIGHT_GOLDENROD_YELLOW, 24, anchor_x="center")

    def draw_map_select(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, WIDTH, HEIGHT, MENU_BG_COLOR)
        arcade.draw_text("ВЫБОР КАРТЫ", HALF_WIDTH, HEIGHT - 150, arcade.color.YELLOW, 74, anchor_x="center")
        for i, map_name in enumerate(self.maps):
            color = arcade.color.GOLD if i == self.selected_map_item else arcade.color.LIGHT_GRAY
            arcade.draw_text(map_name, HALF_WIDTH, HEIGHT - 350 - i * 100, color, 48, anchor_x="center")
        arcade.draw_text("ENTER - начать игру, ESC - назад в меню", 
                        HALF_WIDTH, 100, arcade.color.LIGHT_GOLDENROD_YELLOW, 24, anchor_x="center")

    def draw_high_scores(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, WIDTH, HEIGHT, MENU_BG_COLOR)
        arcade.draw_text("ТАБЛИЦА РЕКОРДОВ", HALF_WIDTH, HEIGHT - 150, arcade.color.YELLOW, 74, anchor_x="center")
        if self.high_scores:
            for i, score_data in enumerate(self.high_scores[:3]):
                arcade.draw_text(f"{i + 1}. {int(score_data['score'])} очков",
                                HALF_WIDTH, HEIGHT - 300 - i * 100, arcade.color.WHITE, 48, anchor_x="center")
        else:
            arcade.draw_text("Пока нет рекордов. Сыграйте игру!", 
                            HALF_WIDTH, HEIGHT - 300, arcade.color.LIGHT_SALMON, 48, anchor_x="center")
        arcade.draw_text("ESC - назад в меню", HALF_WIDTH, 100, arcade.color.LIGHT_GOLDENROD_YELLOW, 24, anchor_x="center")

    def draw_loading_screen(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, WIDTH, HEIGHT, arcade.color.BLACK)
        dots = "." * (int(self.time_played) % 4)
        arcade.draw_text(f"ЗАГРУЗКА{dots}", HALF_WIDTH, HALF_HEIGHT, arcade.color.WHITE, 74, anchor_x="center")
        arcade.draw_text(f"Карта: {self.maps[self.selected_map]}", 
                        HALF_WIDTH, HALF_HEIGHT - 100, arcade.color.GOLD, 48, anchor_x="center")

    def draw_game_over_screen(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, WIDTH, HEIGHT, (30, 0, 0))
        arcade.draw_text("ВЫ ПРОИГРАЛИ", HALF_WIDTH, HEIGHT - 150, arcade.color.RED, 74, anchor_x="center")
        stats = [
            f"Карта: {self.maps[self.selected_map]}",
            f"Уничтожено врагов: {self.total_kills}",
            f"Время выживания: {int(self.time_played)} сек.",
            f"Финальные очки: {int(self.current_score)}"
        ]
        for i, stat in enumerate(stats):
            arcade.draw_text(stat, HALF_WIDTH, HEIGHT - 300 - i * 70, arcade.color.LIGHT_SALMON, 48, anchor_x="center")
        if self.is_new_high_score() and not self.score_saved_this_game:
            arcade.draw_text("НОВЫЙ РЕКОРД!", HALF_WIDTH, HEIGHT - 600, arcade.color.YELLOW, 48, anchor_x="center")
            self.save_high_score()
            self.score_saved_this_game = True
        arcade.draw_text("Нажмите ПРОБЕЛ для возврата в меню", 
                        HALF_WIDTH, 150, arcade.color.GOLD, 36, anchor_x="center")

    def draw_win_screen(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, WIDTH, HEIGHT, (0, 30, 0))
        arcade.draw_text("ПОБЕДА!", HALF_WIDTH, HEIGHT - 150, arcade.color.GREEN, 74, anchor_x="center")
        stats = [
            f"Карта: {self.maps[self.selected_map]}",
            f"Уничтожено врагов: {self.total_kills}",
            f"Время прохождения: {int(self.time_played)} сек.",
            f"Финальные очки: {int(self.current_score)}"
        ]
        for i, stat in enumerate(stats):
            arcade.draw_text(stat, HALF_WIDTH, HEIGHT - 300 - i * 60, arcade.color.LIGHT_GREEN, 48, anchor_x="center")
        if self.is_new_high_score() and not self.score_saved_this_game:
            arcade.draw_text("НОВЫЙ РЕКОРД!", HALF_WIDTH, HEIGHT - 600, arcade.color.YELLOW, 74, anchor_x="center")
            self.save_high_score()
            self.score_saved_this_game = True
        arcade.draw_text("Нажмите ПРОБЕЛ для возврата в меню", 
                        HALF_WIDTH, 150, arcade.color.GOLD, 36, anchor_x="center")

    def on_update(self, delta_time):
        if self.state == "PLAYING":
            self.time_played += delta_time
            self.player.update(delta_time)
            self.object_handler.update(delta_time)
            self.weapon.animate_shot(delta_time)
            self.total_kills = len([npc for npc in self.object_handler.npc_list if not npc.alive])
            self.current_score = self.calculate_score()
        elif self.state == "LOADING":
            self.time_played += delta_time
            if self.time_played > 1:
                self.state = "PLAYING"

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        if self.state == "MAIN_MENU":
            if key == arcade.key.DOWN:
                self.selected_menu_item = (self.selected_menu_item + 1) % len(self.main_menu_items)
            elif key == arcade.key.UP:
                self.selected_menu_item = (self.selected_menu_item - 1) % len(self.main_menu_items)
            elif key == arcade.key.ENTER:
                if self.selected_menu_item == 0:
                    self.state = "MAP_SELECT"
                    self.selected_map_item = 0
                elif self.selected_menu_item == 1:
                    self.state = "HIGH_SCORES"
                elif self.selected_menu_item == 2:
                    arcade.close_window()
            elif key == arcade.key.ESCAPE:
                arcade.close_window()
        elif self.state == "MAP_SELECT":
            if key == arcade.key.DOWN:
                self.selected_map_item = (self.selected_map_item + 1) % len(self.maps)
            elif key == arcade.key.UP:
                self.selected_map_item = (self.selected_map_item - 1) % len(self.maps)
            elif key == arcade.key.ENTER:
                self.selected_map = self.selected_map_item
                self.state = "LOADING"
                self.time_played = 0
                self.new_game(self.selected_map)
            elif key == arcade.key.ESCAPE:
                self.state = "MAIN_MENU"
        elif self.state == "HIGH_SCORES":
            if key == arcade.key.ESCAPE:
                self.state = "MAIN_MENU"
        elif self.state == "PLAYING":
            if key == arcade.key.ESCAPE:
                self.state = "MAIN_MENU"
            if key == arcade.key.SPACE:
                self.player.shot = True
                self.player.shots_fired += 1
                self.object_handler.add_shot_effect(HALF_WIDTH, HALF_HEIGHT)
                for npc in self.object_handler.npc_list:
                    if npc.alive:
                        npc.check_hit()
        elif self.state in ["GAME_OVER", "WIN"]:
            if key == arcade.key.SPACE or key == arcade.key.ENTER:
                self.state = "MAIN_MENU"
            elif key == arcade.key.ESCAPE:
                arcade.close_window()

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.state == "PLAYING":
            if button == arcade.MOUSE_BUTTON_LEFT:
                self.player.shot = True
                self.player.shots_fired += 1
                self.object_handler.add_shot_effect(HALF_WIDTH, HALF_HEIGHT)
                for npc in self.object_handler.npc_list:
                    if npc.alive:
                        npc.check_hit()


def main():
    game = Game()
    arcade.run()


if __name__ == "__main__":
    main()
