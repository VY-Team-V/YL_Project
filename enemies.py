# enemies.py
import arcade
import random
import math
import constants as const
from visual_base import AnimatedVisual


class EnemyBase(AnimatedVisual):
    """Базовый класс врага."""
    def __init__(self, main_game, texture_path, pos=(10.5, 5.5), scale=0.6, animation_time=180):
        super().__init__(main_game, texture_path, pos, scale, animation_time)
        self.attack_range = random.randint(3, 6) * const.CELL_SIZE
        self.move_speed = 1.5
        self.size = 20
        self.hp = 100
        self.damage = 10
        self.hit_chance = 0.15
        self.is_alive = True
        self.is_hurt = False
        self.anim_frame = 0
        self.color = arcade.color.WHITE

    def process_ai(self, delta_time):
        """Обновление логики врага: движение, атака."""
        if not self.is_alive:
            return
        super().update_frame(delta_time)
        self.move_to_avatar()
        self.attempt_attack()

    def can_step_to(self, new_x, new_y):
        """Проверка возможности перемещения в точку (new_x, new_y)."""
        r = self.size
        min_i = int((new_x - r) // const.CELL_SIZE)
        max_i = int((new_x + r) // const.CELL_SIZE)
        min_j = int((new_y - r) // const.CELL_SIZE)
        max_j = int((new_y + r) // const.CELL_SIZE)
        # проверка столкновений со стенами
        for i in range(min_i, max_i + 1):
            for j in range(min_j, max_j + 1):
                if (i, j) in self.main_game.level.world_map:
                    tile_cx = i * const.CELL_SIZE
                    tile_cy = j * const.CELL_SIZE
                    half = const.CELL_SIZE // 2
                    left = tile_cx - half
                    right = tile_cx + half
                    bottom = tile_cy - half
                    top = tile_cy + half
                    closest_x = max(left, min(new_x, right))
                    closest_y = max(bottom, min(new_y, top))
                    dx = new_x - closest_x
                    dy = new_y - closest_y
                    if dx * dx + dy * dy < r * r:
                        return False
        # проверка столкновений с другими врагами
        for enemy in self.main_game.entity_controller.enemy_list:
            if enemy is self or not enemy.is_alive:
                continue
            dx = new_x - enemy.x
            dy = new_y - enemy.y
            dist2 = dx*dx + dy*dy
            if dist2 < (r + enemy.size) ** 2:
                return False
        # проверка столкновения с игроком
        avatar = self.main_game.avatar
        dx = new_x - avatar.x
        dy = new_y - avatar.y
        if dx*dx + dy*dy < (r + const.AVATAR_SIZE) ** 2:
            return False
        return True

    def move_to_avatar(self):
        """Перемещение в сторону игрока."""
        dx = self.main_game.avatar.x - self.x
        dy = self.main_game.avatar.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            dx /= distance
            dy /= distance
            if distance > self.attack_range:
                target_x = self.x + dx * self.move_speed
                target_y = self.y + dy * self.move_speed
                if self.can_step_to(target_x, self.y):
                    self.x = target_x
                if self.can_step_to(self.x, target_y):
                    self.y = target_y

    def attempt_attack(self):
        """Проверка возможности атаки и нанесение урона."""
        if not self.main_game.check_visibility(self.main_game.avatar.x, self.main_game.avatar.y,
                                                self.x, self.y, self.main_game.level.world_map):
            return
        dx = self.main_game.avatar.x - self.x
        dy = self.main_game.avatar.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance < self.attack_range and random.random() < 0.01:
            if random.random() < self.hit_chance:
                self.main_game.avatar.apply_damage(self.damage)
                arcade.play_sound(self.main_game.enemy_attack_sound)

    def take_damage(self, amount):
        """Получение урона."""
        self.hp -= amount
        self.is_hurt = True
        arcade.play_sound(self.main_game.enemy_pain_sound)
        if self.hp <= 0:
            self.is_alive = False
            arcade.play_sound(self.main_game.enemy_death_sound)

    def draw(self):
        """Отрисовка врага (круг с полоской здоровья)."""
        if not self.is_alive:
            return
        screen_x = self.x - self.main_game.avatar.x + const.SCR_HW
        screen_y = self.y - self.main_game.avatar.y + const.SCR_HH
        if -const.CELL_SIZE <= screen_x <= const.SCR_W + const.CELL_SIZE and -const.CELL_SIZE <= screen_y <= const.SCR_H + const.CELL_SIZE:
            arcade.draw_circle_filled(screen_x, screen_y, self.size, self.color)
            health_width = self.size * 2 * (self.hp / 100)
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


class SoldierEnemy(EnemyBase):
    """Солдат (обычный враг)."""
    def __init__(self, main_game, pos=(10.5, 5.5)):
        super().__init__(main_game, '', pos, 0.6, 180)
        self.attack_range = 4 * const.CELL_SIZE
        self.hp = 100
        self.damage = 10
        self.color = arcade.color.BLUE


class CacoDemonEnemy(EnemyBase):
    """Какодемон (сильный враг)."""
    def __init__(self, main_game, pos=(10.5, 6.5)):
        super().__init__(main_game, '', pos, 0.7, 250)
        self.attack_range = 2 * const.CELL_SIZE
        self.hp = 150
        self.damage = 25
        self.move_speed = 2.0
        self.hit_chance = 0.35
        self.color = arcade.color.RED


class CyberDemonEnemy(EnemyBase):
    """Кибердемон (босс-подобный враг)."""
    def __init__(self, main_game, pos=(11.5, 6.0)):
        super().__init__(main_game, '', pos, 1.0, 210)
        self.attack_range = 6 * const.CELL_SIZE
        self.hp = 350
        self.damage = 15
        self.move_speed = 1.8
        self.hit_chance = 0.25
        self.color = arcade.color.PURPLE