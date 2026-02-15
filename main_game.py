# main_game.py
import arcade
import csv
import os
import math
from collections import deque
import constants as const
from game_level import GameLevel
from avatar import Avatar
from entity_controller import EntityController
from gun import Gun
from path_solver import PathSolver


class MainGame(arcade.Window):
    """Главный класс игры, управляет состояниями и рендерингом."""
    def __init__(self):
        super().__init__(const.SCR_W, const.SCR_H, "Doom-Style Shooter")
        self.state = "MAIN_MENU"
        self.selected_level = 0
        self.level_names = ["Замок", "Лабиринт", "Военная база"]
        self.total_kills = 0
        self.time_played = 0
        self.start_time = 0
        self.current_score = 0
        self.menu_items = ["Выбор карты", "Рекорды", "Выход"]
        self.selected_menu_item = 0
        self.selected_map_item = 0
        self.high_scores_file = "high_scores.csv"
        self.high_scores = self.load_records()
        self.score_saved_this_game = False
        self.mouse_pos = (0, 0)
        self.keys_pressed = set()
        self.level = None
        self.avatar = None
        self.entity_controller = None
        self.gun = None
        self.path_solver = None

        # Звуки
        self.shotgun_sound = arcade.load_sound("resources/sound/shotgun.wav")
        self.enemy_pain_sound = arcade.load_sound("resources/sound/npc_pain.wav")
        self.enemy_death_sound = arcade.load_sound("resources/sound/npc_death.wav")
        self.enemy_attack_sound = arcade.load_sound("resources/sound/npc_attack.wav")
        self.avatar_pain_sound = arcade.load_sound("resources/sound/player_pain.wav")
        self.theme_sound = arcade.load_sound("resources/sound/theme.mp3")

        arcade.set_background_color(arcade.color.BLACK)

    def check_visibility(self, x1, y1, x2, y2, world_map):
        """Проверка прямой видимости между точками (x1,y1) и (x2,y2) через клетки карты."""
        x1_cell = int(x1 // const.CELL_SIZE)
        y1_cell = int(y1 // const.CELL_SIZE)
        x2_cell = int(x2 // const.CELL_SIZE)
        y2_cell = int(y2 // const.CELL_SIZE)
        cells = self.get_cell_line(x1_cell, y1_cell, x2_cell, y2_cell)
        for (cx, cy) in cells:
            if (cx, cy) == (x1_cell, y1_cell) or (cx, cy) == (x2_cell, y2_cell):
                continue
            if (cx, cy) in world_map:
                return False
        return True

    def get_cell_line(self, x0, y0, x1, y1):
        """Алгоритм Брезенхема для получения списка клеток на линии."""
        cells = []
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            cells.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
        return cells

    def load_records(self):
        """Загружает таблицу рекордов из CSV."""
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

    def save_record(self):
        """Сохраняет текущий счёт в таблицу рекордов."""
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

    def is_new_record(self):
        """Проверяет, является ли текущий счёт рекордным."""
        if not self.high_scores:
            return True
        if len(self.high_scores) < 3:
            return True
        min_score = min(score['score'] for score in self.high_scores)
        return self.current_score > min_score

    def start_level(self, level_id=0):
        """Инициализация нового уровня."""
        self.level = GameLevel(self, level_id)
        start_pos = const.AVATAR_START_POSITIONS.get(level_id, (1.5, 5))
        self.avatar = Avatar(self)
        self.avatar.set_coordinates(*start_pos)
        self.entity_controller = EntityController(self, level_id)
        self.gun = Gun(self)
        self.path_solver = PathSolver(self)
        self.total_kills = 0
        self.start_time = 0
        self.time_played = 0
        self.current_score = 0
        self.score_saved_this_game = False
        arcade.play_sound(self.theme_sound, looping=True)

    def compute_score(self):
        """Вычисляет текущий счёт на основе убийств, времени и здоровья."""
        kill_points = self.total_kills * 100
        time_bonus = max(0, 300 - self.time_played) * 10
        health_bonus = self.avatar.hp * 2
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
        """Отрисовка игрового процесса."""
        arcade.draw_lbwh_rectangle_filled(0, 0, const.SCR_W, const.SCR_H, const.GROUND_COLOR)
        # отрисовка стен
        for (x, y), texture_id in self.level.world_map.items():
            screen_x = x * const.CELL_SIZE - self.avatar.x + const.SCR_HW
            screen_y = y * const.CELL_SIZE - self.avatar.y + const.SCR_HH
            if -const.CELL_SIZE <= screen_x <= const.SCR_W + const.CELL_SIZE and -const.CELL_SIZE <= screen_y <= const.SCR_H + const.CELL_SIZE:
                color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)][(texture_id - 1) % 5]
                arcade.draw_lbwh_rectangle_filled(
                    screen_x - const.CELL_SIZE // 2,
                    screen_y - const.CELL_SIZE // 2,
                    const.CELL_SIZE,
                    const.CELL_SIZE,
                    color
                )
        self.entity_controller.draw_all()
        self.avatar.draw()
        self.draw_hud()

    def draw_hud(self):
        """Отрисовка интерфейса (здоровье, убийства, время, очки)."""
        arcade.draw_text(f"Здоровье: {self.avatar.hp}", 10, const.SCR_H - 30, arcade.color.WHITE, 20, anchor_x="left")
        arcade.draw_text(f"Убито: {self.total_kills}", 10, const.SCR_H - 60, arcade.color.WHITE, 20, anchor_x="left")
        arcade.draw_text(f"Время: {int(self.time_played)} сек.", 10, const.SCR_H - 90, arcade.color.WHITE, 20, anchor_x="left")
        arcade.draw_text(f"Очки: {int(self.current_score)}", 10, const.SCR_H - 120, arcade.color.WHITE, 20, anchor_x="left")

    def draw_main_menu(self):
        """Отрисовка главного меню."""
        arcade.draw_lbwh_rectangle_filled(0, 0, const.SCR_W, const.SCR_H, const.MENU_BACKGROUND)
        arcade.draw_text("DOOM STYLE SHOOTER", const.SCR_HW, const.SCR_H - 150, arcade.color.RED, 74, anchor_x="center")
        for i, item in enumerate(self.menu_items):
            color = arcade.color.YELLOW if i == self.selected_menu_item else arcade.color.LIGHT_GRAY
            arcade.draw_text(item, const.SCR_HW, const.SCR_H - 350 - i * 100, color, 48, anchor_x="center")
        arcade.draw_text("Управление: ↑↓ - выбор, ENTER - подтвердить, ESC - выход",
                        const.SCR_HW, 100, arcade.color.LIGHT_GOLDENROD_YELLOW, 24, anchor_x="center")

    def draw_map_select(self):
        """Отрисовка меню выбора карты."""
        arcade.draw_lbwh_rectangle_filled(0, 0, const.SCR_W, const.SCR_H, const.MENU_BACKGROUND)
        arcade.draw_text("ВЫБОР КАРТЫ", const.SCR_HW, const.SCR_H - 150, arcade.color.YELLOW, 74, anchor_x="center")
        for i, map_name in enumerate(self.level_names):
            color = arcade.color.GOLD if i == self.selected_map_item else arcade.color.LIGHT_GRAY
            arcade.draw_text(map_name, const.SCR_HW, const.SCR_H - 350 - i * 100, color, 48, anchor_x="center")
        arcade.draw_text("ENTER - начать игру, ESC - назад в меню",
                        const.SCR_HW, 100, arcade.color.LIGHT_GOLDENROD_YELLOW, 24, anchor_x="center")

    def draw_high_scores(self):
        """Отрисовка таблицы рекордов."""
        arcade.draw_lbwh_rectangle_filled(0, 0, const.SCR_W, const.SCR_H, const.MENU_BACKGROUND)
        arcade.draw_text("ТАБЛИЦА РЕКОРДОВ", const.SCR_HW, const.SCR_H - 150, arcade.color.YELLOW, 74, anchor_x="center")
        if self.high_scores:
            for i, score_data in enumerate(self.high_scores[:3]):
                arcade.draw_text(f"{i + 1}. {int(score_data['score'])} очков",
                                const.SCR_HW, const.SCR_H - 300 - i * 100, arcade.color.WHITE, 48, anchor_x="center")
        else:
            arcade.draw_text("Пока нет рекордов. Сыграйте игру!",
                            const.SCR_HW, const.SCR_H - 300, arcade.color.LIGHT_SALMON, 48, anchor_x="center")
        arcade.draw_text("ESC - назад в меню", const.SCR_HW, 100, arcade.color.LIGHT_GOLDENROD_YELLOW, 24, anchor_x="center")

    def draw_loading_screen(self):
        """Экран загрузки."""
        arcade.draw_lbwh_rectangle_filled(0, 0, const.SCR_W, const.SCR_H, arcade.color.BLACK)
        dots = "." * (int(self.time_played) % 4)
        arcade.draw_text(f"ЗАГРУЗКА{dots}", const.SCR_HW, const.SCR_HH, arcade.color.WHITE, 74, anchor_x="center")
        arcade.draw_text(f"Карта: {self.level_names[self.selected_level]}",
                        const.SCR_HW, const.SCR_HH - 100, arcade.color.GOLD, 48, anchor_x="center")

    def draw_game_over_screen(self):
        """Экран проигрыша."""
        arcade.draw_lbwh_rectangle_filled(0, 0, const.SCR_W, const.SCR_H, (30, 0, 0))
        arcade.draw_text("ВЫ ПРОИГРАЛИ", const.SCR_HW, const.SCR_H - 150, arcade.color.RED, 74, anchor_x="center")
        stats = [
            f"Карта: {self.level_names[self.selected_level]}",
            f"Уничтожено врагов: {self.total_kills}",
            f"Время выживания: {int(self.time_played)} сек.",
            f"Финальные очки: {int(self.current_score)}"
        ]
        for i, stat in enumerate(stats):
            arcade.draw_text(stat, const.SCR_HW, const.SCR_H - 300 - i * 70, arcade.color.LIGHT_SALMON, 48, anchor_x="center")
        if self.is_new_record() and not self.score_saved_this_game:
            arcade.draw_text("НОВЫЙ РЕКОРД!", const.SCR_HW, const.SCR_H - 600, arcade.color.YELLOW, 48, anchor_x="center")
            self.save_record()
            self.score_saved_this_game = True
        arcade.draw_text("Нажмите ПРОБЕЛ для возврата в меню",
                        const.SCR_HW, 150, arcade.color.GOLD, 36, anchor_x="center")

    def draw_win_screen(self):
        """Экран победы."""
        arcade.draw_lbwh_rectangle_filled(0, 0, const.SCR_W, const.SCR_H, (0, 30, 0))
        arcade.draw_text("ПОБЕДА!", const.SCR_HW, const.SCR_H - 150, arcade.color.GREEN, 74, anchor_x="center")
        stats = [
            f"Карта: {self.level_names[self.selected_level]}",
            f"Уничтожено врагов: {self.total_kills}",
            f"Время прохождения: {int(self.time_played)} сек.",
            f"Финальные очки: {int(self.current_score)}"
        ]
        for i, stat in enumerate(stats):
            arcade.draw_text(stat, const.SCR_HW, const.SCR_H - 300 - i * 60, arcade.color.LIGHT_GREEN, 48, anchor_x="center")
        if self.is_new_record() and not self.score_saved_this_game:
            arcade.draw_text("НОВЫЙ РЕКОРД!", const.SCR_HW, const.SCR_H - 600, arcade.color.YELLOW, 74, anchor_x="center")
            self.save_record()
            self.score_saved_this_game = True
        arcade.draw_text("Нажмите ПРОБЕЛ для возврата в меню",
                        const.SCR_HW, 150, arcade.color.GOLD, 36, anchor_x="center")

    def on_update(self, delta_time):
        if self.state == "PLAYING":
            self.time_played += delta_time
            self.avatar.update_state(delta_time)
            self.entity_controller.update_all(delta_time)
            self.gun.animate_fire(delta_time)
            self.total_kills = len([e for e in self.entity_controller.enemy_list if not e.is_alive])
            self.current_score = self.compute_score()
        elif self.state == "LOADING":
            self.time_played += delta_time
            if self.time_played > 1:
                self.state = "PLAYING"

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        if self.state == "MAIN_MENU":
            if key == arcade.key.DOWN:
                self.selected_menu_item = (self.selected_menu_item + 1) % len(self.menu_items)
            elif key == arcade.key.UP:
                self.selected_menu_item = (self.selected_menu_item - 1) % len(self.menu_items)
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
                self.selected_map_item = (self.selected_map_item + 1) % len(self.level_names)
            elif key == arcade.key.UP:
                self.selected_map_item = (self.selected_map_item - 1) % len(self.level_names)
            elif key == arcade.key.ENTER:
                self.selected_level = self.selected_map_item
                self.state = "LOADING"
                self.time_played = 0
                self.start_level(self.selected_level)
            elif key == arcade.key.ESCAPE:
                self.state = "MAIN_MENU"
        elif self.state == "HIGH_SCORES":
            if key == arcade.key.ESCAPE:
                self.state = "MAIN_MENU"
        elif self.state == "PLAYING":
            if key == arcade.key.ESCAPE:
                self.state = "MAIN_MENU"
                arcade.stop_sound(self.theme_sound)
            if key == arcade.key.SPACE:
                self.avatar.shot = True
                self.avatar.shots_fired += 1
                arcade.play_sound(self.shotgun_sound)
                self.entity_controller.add_muzzle_flash(const.SCR_HW, const.SCR_HH)
                for enemy in self.entity_controller.enemy_list:
                    if enemy.is_alive and self.check_visibility(self.avatar.x, self.avatar.y, enemy.x, enemy.y, self.level.world_map):
                        enemy.take_damage(self.gun.damage)
                self.avatar.shot = False
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
        if self.state == "PLAYING" and button == arcade.MOUSE_BUTTON_LEFT:
            self.avatar.shot = True
            self.avatar.shots_fired += 1
            arcade.play_sound(self.shotgun_sound)
            self.entity_controller.add_muzzle_flash(const.SCR_HW, const.SCR_HH)
            for enemy in self.entity_controller.enemy_list:
                if enemy.is_alive and self.check_visibility(self.avatar.x, self.avatar.y, enemy.x, enemy.y, self.level.world_map):
                    enemy.take_damage(self.gun.damage)
            self.avatar.shot = False


def main():
    game = MainGame()
    arcade.run()