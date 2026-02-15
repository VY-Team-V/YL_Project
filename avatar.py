# avatar.py
import arcade
import math
import constants as const


class Avatar:
    """Игровой персонаж."""
    def __init__(self, main_game):
        self.main_game = main_game
        self.x, self.y = 0, 0
        self.angle = 0
        self.shot = False
        self.hp = const.AVATAR_MAX_HEALTH
        self.health_recovery_delay = 700  # мс
        self.time_prev = 0
        self.shots_fired = 0
        self.damage_taken = 0

    def set_coordinates(self, x, y):
        """Устанавливает позицию в клетках."""
        self.x = x * const.CELL_SIZE
        self.y = y * const.CELL_SIZE

    def heal_over_time(self, delta_time):
        """Восстановление здоровья со временем."""
        self.time_prev += delta_time * 1000
        if self.time_prev > self.health_recovery_delay and self.hp < const.AVATAR_MAX_HEALTH:
            self.time_prev = 0
            self.hp += 1

    def check_defeat(self):
        """Проверка условия поражения."""
        if self.hp < 1:
            self.main_game.state = "GAME_OVER"

    def apply_damage(self, amount):
        """Получение урона."""
        self.hp -= amount
        self.damage_taken += amount
        arcade.play_sound(self.main_game.avatar_pain_sound)
        self.check_defeat()

    def can_step_to(self, new_x, new_y):
        """Проверка возможности перемещения в точку."""
        r = const.AVATAR_SIZE
        min_i = int((new_x - r) // const.CELL_SIZE)
        max_i = int((new_x + r) // const.CELL_SIZE)
        min_j = int((new_y - r) // const.CELL_SIZE)
        max_j = int((new_y + r) // const.CELL_SIZE)
        # стены
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
        # враги
        for enemy in self.main_game.entity_controller.enemy_list:
            if not enemy.is_alive:
                continue
            dx = new_x - enemy.x
            dy = new_y - enemy.y
            dist2 = dx*dx + dy*dy
            if dist2 < (r + enemy.size) ** 2:
                return False
        return True

    def handle_movement(self):
        """Обработка перемещения по клавишам."""
        speed = const.AVATAR_SPEED
        dx, dy = 0, 0
        if arcade.key.W in self.main_game.keys_pressed:
            dy += speed
        if arcade.key.S in self.main_game.keys_pressed:
            dy -= speed
        if arcade.key.A in self.main_game.keys_pressed:
            dx -= speed
        if arcade.key.D in self.main_game.keys_pressed:
            dx += speed
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        new_x = self.x + dx
        new_y = self.y + dy
        if self.can_step_to(new_x, self.y):
            self.x = new_x
        if self.can_step_to(self.x, new_y):
            self.y = new_y

    def aim_with_mouse(self):
        """Управление направлением взгляда с помощью мыши."""
        mx, my = self.main_game.mouse_pos
        self.angle = math.atan2(my - const.SCR_HH, mx - const.SCR_HW)

    def update_state(self, delta_time):
        """Обновление состояния игрока."""
        self.handle_movement()
        self.aim_with_mouse()
        self.heal_over_time(delta_time)

    def draw(self):
        """Отрисовка игрока (круг с указателем направления)."""
        arcade.draw_circle_filled(const.SCR_HW, const.SCR_HH, const.AVATAR_SIZE, arcade.color.GREEN)
        arrow_size = 8
        inner_offset = 5
        tip_x = const.SCR_HW + math.cos(self.angle) * (const.AVATAR_SIZE - inner_offset)
        tip_y = const.SCR_HH + math.sin(self.angle) * (const.AVATAR_SIZE - inner_offset)
        left_x = const.SCR_HW + math.cos(self.angle - math.pi/2) * arrow_size
        left_y = const.SCR_HH + math.sin(self.angle - math.pi/2) * arrow_size
        right_x = const.SCR_HW + math.cos(self.angle + math.pi/2) * arrow_size
        right_y = const.SCR_HH + math.sin(self.angle + math.pi/2) * arrow_size
        arcade.draw_triangle_filled(
            tip_x, tip_y,
            left_x, left_y,
            right_x, right_y,
            arcade.color.YELLOW
        )