
import random
import arcade
from npc import SoldierNPC, CacoDemonNPC, CyberDemonNPC
from settings import TILE_SIZE, WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT
from map import MAPS

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
