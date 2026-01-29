from sprite_object import *
from npc import *
from random import choices, randrange


class ObjectHandler:
    def __init__(self, game, map_id=0):
        self.game = game
        self.map_id = map_id
        self.sprite_list = []
        self.npc_list = []
        self.npc_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'
        add_sprite = self.add_sprite
        add_npc = self.add_npc
        self.npc_positions = {}

        # ФИКСИРОВАННЫЕ позиции врагов для каждой карты
        self.fixed_npc_positions = self.get_fixed_npc_positions()
        
        self.spawn_fixed_npc()
        
        # Размещение спрайтов в зависимости от карты
        self.setup_sprites()

    def get_fixed_npc_positions(self):
        """Возвращает фиксированные позиции врагов для текущей карты"""
        if self.map_id == 0:  # Замок
            return [
                {'type': SoldierNPC, 'pos': (3.5, 3.5)},
                {'type': SoldierNPC, 'pos': (12.5, 5.5)},
                {'type': CacoDemonNPC, 'pos': (8.5, 8.5)},
                {'type': SoldierNPC, 'pos': (5.5, 12.5)},
                {'type': CyberDemonNPC, 'pos': (14.5, 14.5)}
            ]
        elif self.map_id == 1:  # Лабиринт
            return [
                {'type': SoldierNPC, 'pos': (3.5, 2.5)},
                {'type': SoldierNPC, 'pos': (12.5, 2.5)},
                {'type': CacoDemonNPC, 'pos': (7.5, 7.5)},
                {'type': SoldierNPC, 'pos': (2.5, 12.5)},
                {'type': CyberDemonNPC, 'pos': (12.5, 12.5)}
            ]
        elif self.map_id == 2:  # Военная база
            return [
                {'type': SoldierNPC, 'pos': (4.5, 4.5)},
                {'type': SoldierNPC, 'pos': (11.5, 4.5)},
                {'type': CacoDemonNPC, 'pos': (4.5, 11.5)},
                {'type': SoldierNPC, 'pos': (11.5, 11.5)},
                {'type': CyberDemonNPC, 'pos': (8.5, 8.5)}
            ]
        return []

    def spawn_fixed_npc(self):
        """Спавнит врагов на фиксированных позициях"""
        for npc_data in self.fixed_npc_positions:
            npc_type = npc_data['type']
            pos = npc_data['pos']
            self.add_npc(npc_type(self.game, pos=pos))

    def setup_sprites(self):
        add_sprite = self.add_sprite
        
        if self.map_id == 0:  # Замок
            add_sprite(AnimatedSprite(self.game, pos=(1.5, 1.5)))
            add_sprite(AnimatedSprite(self.game, pos=(1.5, 7.5)))
            add_sprite(AnimatedSprite(self.game, pos=(5.5, 3.25)))
            add_sprite(AnimatedSprite(self.game, pos=(5.5, 4.75)))
            add_sprite(AnimatedSprite(self.game, pos=(7.5, 2.5)))
            
        elif self.map_id == 1:  # Лабиринт
            add_sprite(AnimatedSprite(self.game, pos=(2.5, 2.5)))
            add_sprite(AnimatedSprite(self.game, pos=(2.5, 13.5)))
            add_sprite(AnimatedSprite(self.game, pos=(7.5, 7.5)))
            add_sprite(AnimatedSprite(self.game, pos=(12.5, 2.5)))
            
        elif self.map_id == 2:  # Военная база
            add_sprite(AnimatedSprite(self.game, pos=(3.5, 3.5)))
            add_sprite(AnimatedSprite(self.game, pos=(3.5, 12.5)))
            add_sprite(AnimatedSprite(self.game, pos=(8.5, 8.5)))
            add_sprite(AnimatedSprite(self.game, pos=(12.5, 3.5)))

    def check_win(self):
        alive_enemies = [npc for npc in self.npc_list if npc.alive]
        if not alive_enemies and self.game.state == "PLAYING":
            self.game.state = "WIN"
            pg.mouse.set_visible(True)
            pg.event.set_grab(False)

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        self.check_win()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)