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

        # ФИКСИРОВАННОЕ количество врагов - 5 для всех карт
        self.enemies = 5
        
        # ФИКСИРОВАННЫЕ типы врагов для всех карт
        self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        self.weights = [70, 20, 10]  # 70% солдаты, 20% како-демоны, 10% кибердемоны
        
        # Ограниченная область для спавна (вокруг стартовой позиции игрока)
        start_x, start_y = self.game.player.map_pos
        self.restricted_area = {(start_x + dx, start_y + dy) for dx in range(-3, 4) for dy in range(-3, 4)}
        
        self.spawn_npc()
        
        # Размещение спрайтов в зависимости от карты
        self.setup_sprites()

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

    def spawn_npc(self):
        for i in range(self.enemies):
            npc = choices(self.npc_types, self.weights)[0]
            attempts = 0
            while attempts < 100:  # Ограничение попыток
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
                # Проверяем, чтобы позиция была свободной
                if (pos not in self.game.map.world_map and 
                    pos not in self.restricted_area and
                    pos not in self.npc_positions):
                    self.add_npc(npc(self.game, pos=(x + 0.5, y + 0.5)))
                    break
                attempts += 1

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