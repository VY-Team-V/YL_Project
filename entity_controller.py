# entity_controller.py
import arcade
from enemies import SoldierEnemy, CacoDemonEnemy, CyberDemonEnemy
from visual_base import AnimatedVisual
import constants as const


class EntityController:
    """Управление всеми сущностями на уровне (враги, спрайты, эффекты)."""
    def __init__(self, main_game, level_id=0):
        self.main_game = main_game
        self.level_id = level_id
        self.visual_list = []  # список декоративных спрайтов
        self.enemy_list = []   # список врагов
        self.shot_effects = [] # вспышки выстрелов
        self.fixed_enemy_positions = self.get_fixed_enemy_positions()
        self.spawn_fixed_enemies()
        self.setup_visuals()

    def get_fixed_enemy_positions(self):
        """Возвращает список фиксированных позиций врагов для данного уровня."""
        if self.level_id == 0:
            return [
                {'type': SoldierEnemy, 'pos': (3.5, 3.5)},
                {'type': SoldierEnemy, 'pos': (12.5, 5.5)},
                {'type': CacoDemonEnemy, 'pos': (8.5, 8.5)},
                {'type': SoldierEnemy, 'pos': (5.5, 12.5)},
                {'type': CyberDemonEnemy, 'pos': (14.5, 14.5)}
            ]
        elif self.level_id == 1:
            return [
                {'type': SoldierEnemy, 'pos': (3.5, 2.5)},
                {'type': SoldierEnemy, 'pos': (12.5, 2.5)},
                {'type': CacoDemonEnemy, 'pos': (7.5, 7.5)},
                {'type': SoldierEnemy, 'pos': (2.5, 12.5)},
                {'type': CyberDemonEnemy, 'pos': (12.5, 12.5)}
            ]
        elif self.level_id == 2:
            return [
                {'type': SoldierEnemy, 'pos': (4.5, 4.5)},
                {'type': SoldierEnemy, 'pos': (11.5, 4.5)},
                {'type': CacoDemonEnemy, 'pos': (4.5, 11.5)},
                {'type': SoldierEnemy, 'pos': (11.5, 11.5)},
                {'type': CyberDemonEnemy, 'pos': (8.5, 8.5)}
            ]
        return []

    def spawn_fixed_enemies(self):
        """Создаёт врагов в фиксированных позициях."""
        for data in self.fixed_enemy_positions:
            enemy_type = data['type']
            pos = data['pos']
            self.add_enemy(enemy_type(self.main_game, pos))

    def setup_visuals(self):
        """Настройка декоративных спрайтов (пусто)."""
        pass

    def check_victory(self):
        """Проверка условия победы (все враги мертвы)."""
        alive_enemies = [e for e in self.enemy_list if e.is_alive]
        if not alive_enemies and self.main_game.state == "PLAYING":
            self.main_game.state = "WIN"

    def add_muzzle_flash(self, x, y):
        """Добавляет эффект вспышки выстрела."""
        self.shot_effects.append({'x': x, 'y': y, 'size': 20, 'alpha': 255, 'life': 0.3})

    def update_all(self, delta_time):
        """Обновляет все сущности."""
        for visual in self.visual_list:
            if isinstance(visual, AnimatedVisual):
                visual.update_frame(delta_time)
        for enemy in self.enemy_list:
            enemy.process_ai(delta_time)
        for effect in self.shot_effects[:]:
            effect['life'] -= delta_time
            effect['size'] += 100 * delta_time
            effect['alpha'] = int(255 * (effect['life'] / 0.3))
            if effect['life'] <= 0:
                self.shot_effects.remove(effect)
        self.check_victory()

    def draw_all(self):
        """Отрисовка всех сущностей."""
        for effect in self.shot_effects:
            arcade.draw_circle_filled(
                effect['x'],
                effect['y'],
                effect['size'],
                (255, 255, 200, effect['alpha'])
            )
        for enemy in self.enemy_list:
            if enemy.is_alive:
                enemy.draw()

    def add_enemy(self, enemy):
        self.enemy_list.append(enemy)

    def add_visual(self, visual):
        self.visual_list.append(visual)