
import arcade
import csv
import os
import math
import random
from settings import *
from map import Map
from player import Player
from object_handler import ObjectHandler
from weapon import Weapon
from pathfinding import PathFinding
from menu_resources import MAIN_MENU_ITEMS, MAPS_NAMES
from npc import SoldierNPC, CacoDemonNPC, CyberDemonNPC

class Game(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "Doom-Style Shooter")
        self.state = "MAIN_MENU"
        self.selected_map = 0
        self.maps = MAPS_NAMES
        self.total_kills = 0
        self.time_played = 0
        self.start_time = 0
        self.current_score = 0
        self.main_menu_items = MAIN_MENU_ITEMS
        self.selected_menu_item = 0
        self.selected_map_item = 0
        self.high_scores_file = os.path.join("resources", "high_scores.csv")
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
