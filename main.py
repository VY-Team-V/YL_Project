# [file name]: main.py
import pygame as pg
import sys
import csv
import os
from datetime import datetime
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(True)
        self.screen = pg.display.set_mode(RES)
        pg.event.set_grab(False)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        
        self.title_font = pg.font.Font(None, 96)
        self.large_font = pg.font.Font(None, 74)
        self.medium_font = pg.font.Font(None, 48)
        self.small_font = pg.font.Font(None, 36)
        
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
        
        # Флаг для предотвращения многократного сохранения одного рекорда
        self.score_saved_this_game = False
        
        self.load_menu_resources()
        
        self.map = None
        self.player = None
        self.object_renderer = None
        self.raycasting = None
        self.object_handler = None
        self.weapon = None
        self.sound = None
        self.pathfinding = None

    def load_menu_resources(self):
        # Загрузка фона главного меню (должен лежать в resources/textures/menu_bg.png)
        try:
            self.menu_bg = pg.image.load('resources/textures/menu_bg.png').convert()
            self.menu_bg = pg.transform.scale(self.menu_bg, RES)
        except:
            # Создание запасного градиентного фона
            self.menu_bg = pg.Surface(RES)
            for y in range(HEIGHT):
                color_value = 20 + int(20 * (y / HEIGHT))
                pg.draw.line(self.menu_bg, (color_value, color_value, 60), (0, y), (WIDTH, y))
        
        self.logo = None

    def new_game(self, map_id=0):
        self.map = Map(self, map_id)
        
        start_pos = PLAYER_START_POSITIONS.get(map_id, (1.5, 5))
        
        self.player = Player(self)
        self.player.x, self.player.y = start_pos
        
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self, map_id)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        
        # Сброс статистики
        self.total_kills = 0
        self.start_time = pg.time.get_ticks()
        self.time_played = 0
        self.current_score = 0
        self.score_saved_this_game = False  # Сбрасываем флаг сохранения
        
        # Воспроизведение музыки
        pg.mixer.music.play(-1)

    def update(self):
        if self.state == "PLAYING":
            self.player.update()
            self.raycasting.update()
            self.object_handler.update()
            self.weapon.update()
            self.time_played = (pg.time.get_ticks() - self.start_time) // 1000
            self.total_kills = len([npc for npc in self.object_handler.npc_list if not npc.alive])
            self.current_score = self.calculate_score()
            
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'Doom-Style Shooter - {self.clock.get_fps() :.1f} FPS')

    def calculate_score(self):
        kill_points = self.total_kills * 100
        time_bonus = max(0, 300 - self.time_played) * 10
        health_bonus = self.player.health * 2
        
        return kill_points + time_bonus + health_bonus

    def draw(self):
        if self.state == "PLAYING":
            self.object_renderer.draw()
            self.weapon.draw()
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

    def draw_main_menu(self):
        # Фон
        self.screen.blit(self.menu_bg, (0, 0))
        
        # Заголовок
        title_shadow = self.title_font.render("DOOM STYLE SHOOTER", True, (100, 0, 0))
        title = self.title_font.render("DOOM STYLE SHOOTER", True, (255, 50, 50))
        self.screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 5, 85))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        # Элементы меню
        for i, item in enumerate(self.main_menu_items):
            color = (255, 255, 0) if i == self.selected_menu_item else (200, 200, 200)
            
            text_shadow = self.large_font.render(item, True, (50, 50, 50))
            text = self.large_font.render(item, True, color)
            
            x = WIDTH // 2 - text.get_width() // 2
            y = 350 + i * 100
            
            # Рамка для выбранного элемента
            if i == self.selected_menu_item:
                pg.draw.rect(self.screen, (255, 50, 50, 100), 
                            (x - 30, y - 15, text.get_width() + 60, text.get_height() + 30), 
                            border_radius=15, width=3)
            
            self.screen.blit(text_shadow, (x + 3, y + 3))
            self.screen.blit(text, (x, y))
        
        # Инструкции внизу
        controls = self.small_font.render("Управление: ↑↓ - выбор, ENTER - подтвердить, ESC - выход", True, (200, 200, 100))
        self.screen.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT - 80))

    def draw_map_select(self):
        self.screen.blit(self.menu_bg, (0, 0))
        
        # Заголовок
        title_shadow = self.large_font.render("ВЫБОР КАРТЫ", True, (50, 50, 50))
        title = self.large_font.render("ВЫБОР КАРТЫ", True, (255, 255, 0))
        self.screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, 103))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Список карт - ТОЛЬКО НАЗВАНИЕ КАРТЫ
        for i, map_name in enumerate(self.maps):
            is_selected = (i == self.selected_map_item)
            color = (255, 200, 0) if is_selected else (180, 180, 180)
            
            # Название карты
            text = self.medium_font.render(map_name, True, color)
            x = WIDTH // 2 - text.get_width() // 2
            y = 300 + i * 100  # Увеличен интервал
            
            if is_selected:
                # Подсветка выбранной карты
                pg.draw.rect(self.screen, (50, 50, 255, 80), 
                            (x - 30, y - 15, text.get_width() + 60, text.get_height() + 30), 
                            border_radius=10)
            
            # Отображение текста
            self.screen.blit(text, (x, y))
        
        # Кнопка назад
        back_text = self.medium_font.render("Назад (ESC)", True, (150, 150, 150))
        self.screen.blit(back_text, (50, HEIGHT - 100))
        
        # Управление
        controls = self.small_font.render("ENTER - начать игру, ESC - назад в меню", True, (200, 200, 100))
        self.screen.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT - 80))

    def draw_high_scores(self):
        self.screen.blit(self.menu_bg, (0, 0))
        
        # Заголовок
        title_shadow = self.large_font.render("ТАБЛИЦА РЕКОРДОВ", True, (50, 50, 50))
        title = self.large_font.render("ТАБЛИЦА РЕКОРДОВ", True, (255, 255, 0))
        self.screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, 103))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        if self.high_scores:
            for i, score_data in enumerate(self.high_scores[:3]):  # Только 3 лучших рекорда
                y_pos = 250 + i * 100  # Увеличил интервал для лучшей читаемости
                
                # Создаем фон для записи
                bg_color = (30, 30, 60, 200) if i % 2 == 0 else (40, 40, 70, 200)
                pg.draw.rect(self.screen, bg_color, 
                            (WIDTH//2 - 250, y_pos - 15, 500, 70),  # Уменьшил ширину
                            border_radius=10)
                
                # Место
                place_text = self.medium_font.render(f"{i+1}.", True, (255, 255, 255))
                self.screen.blit(place_text, (WIDTH//2 - 220, y_pos + 10))
                
                # Очки
                score_text = self.medium_font.render(f"{score_data['score']} очков", True, (255, 255, 100))
                self.screen.blit(score_text, (WIDTH//2 - 50, y_pos + 10))
        else:
            no_scores = self.medium_font.render("Пока нет рекордов. Сыграйте игру!", True, (255, 150, 150))
            self.screen.blit(no_scores, (WIDTH//2 - no_scores.get_width()//2, 300))
        
        back_text = self.medium_font.render("Назад (ESC)", True, (255, 255, 255))
        self.screen.blit(back_text, (50, HEIGHT - 100))
        
        instruction = self.small_font.render("Нажмите ESC для возврата в меню", True, (200, 200, 100))
        self.screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT - 80))

    def draw_loading_screen(self):
        self.screen.fill((0, 0, 0))
        
        dots = "." * ((pg.time.get_ticks() // 500) % 4)
        loading_text = self.large_font.render(f"ЗАГРУЗКА{dots}", True, (255, 255, 255))
        self.screen.blit(loading_text, (WIDTH//2 - loading_text.get_width()//2, HEIGHT//2 - 50))
        
        map_text = self.medium_font.render(f"Карта: {self.maps[self.selected_map]}", True, (255, 200, 100))
        self.screen.blit(map_text, (WIDTH//2 - map_text.get_width()//2, HEIGHT//2 + 30))
        
        bar_width = 500
        bar_height = 30
        bar_x = WIDTH//2 - bar_width//2
        bar_y = HEIGHT//2 + 100
        
        pg.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        
        progress = (pg.time.get_ticks() % 2000) / 2000
        pg.draw.rect(self.screen, (255, 50, 50), (bar_x, bar_y, bar_width * progress, bar_height), border_radius=5)

    def draw_game_over_screen(self):
        self.screen.fill((30, 0, 0))
        
        title = self.large_font.render("ВЫ ПРОИГРАЛИ", True, (255, 50, 50))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        stats = [
            f"Карта: {self.maps[self.selected_map]}",
            f"Уничтожено врагов: {self.total_kills}",
            f"Время выживания: {self.time_played} сек.",
            f"Финальные очки: {self.current_score}"
        ]
        
        for i, stat in enumerate(stats):
            text = self.medium_font.render(stat, True, (255, 200, 200))
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, 250 + i * 70))
        
        # Проверяем, является ли результат новым рекордом И ЕЩЕ НЕ СОХРАНЕННЫМ
        if self.is_new_high_score() and not self.score_saved_this_game:
            new_record = self.medium_font.render("НОВЫЙ РЕКОРД!", True, (255, 255, 0))
            self.screen.blit(new_record, (WIDTH//2 - new_record.get_width()//2, 550))
            # Сохраняем рекорд только один раз
            self.save_high_score()
            self.score_saved_this_game = True  # Устанавливаем флаг, что рекорд сохранен
        
        continue_text = self.medium_font.render("Нажмите ПРОБЕЛ для возврата в меню", True, (255, 255, 100))
        self.screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT - 150))

    def draw_win_screen(self):
        self.screen.fill((0, 30, 0))
        
        title = self.large_font.render("ПОБЕДА!", True, (50, 255, 50))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        stats = [
            f"Карта: {self.maps[self.selected_map]}",
            f"Уничтожено врагов: {self.total_kills}",
            f"Время прохождения: {self.time_played} сек.",
            f"Финальные очки: {self.current_score}"
        ]
        
        for i, stat in enumerate(stats):
            text = self.medium_font.render(stat, True, (200, 255, 200))
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, 250 + i * 60))
        
        # Проверяем, является ли результат новым рекордом И ЕЩЕ НЕ СОХРАНЕННЫМ
        if self.is_new_high_score() and not self.score_saved_this_game:
            new_record_text = self.large_font.render("НОВЫЙ РЕКОРД!", True, (255, 255, 0))
            self.screen.blit(new_record_text, (WIDTH//2 - new_record_text.get_width()//2, HEIGHT - 200))
            # Сохраняем рекорд только один раз
            self.save_high_score()
            self.score_saved_this_game = True  # Устанавливаем флаг, что рекорд сохранен
        
        continue_text = self.medium_font.render("Нажмите ПРОБЕЛ для возврата в меню", True, (255, 255, 100))
        self.screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT - 150))

    def calculate_accuracy(self):
        if hasattr(self.player, 'shots_fired') and self.player.shots_fired > 0:
            return (self.total_kills / self.player.shots_fired * 100) if self.player.shots_fired > 0 else 0
        return 0

    def calculate_rating(self):
        if self.time_played > 0:
            return self.total_kills / (self.time_played / 60)
        return 0

    def load_high_scores(self):
        scores = []
        try:
            if os.path.exists(self.high_scores_file):
                with open(self.high_scores_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Преобразуем score в число
                        row['score'] = int(row['score'])
                        scores.append(row)
        except Exception as e:
            print(f"Ошибка загрузки рекордов: {e}")
        return scores

    def save_high_score(self):
        # Сохраняем только очки
        score_data = {
            'score': self.current_score
        }
        
        self.high_scores.append(score_data)
        # Сортируем по убыванию очков
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        # Оставляем только топ-3
        self.high_scores = self.high_scores[:3]
        
        try:
            with open(self.high_scores_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['score']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.high_scores)
            print("Рекорд сохранен в CSV!")
        except Exception as e:
            print(f"Ошибка сохранения рекорда: {e}")

    def is_new_high_score(self):
        if not self.high_scores:
            return True
        
        # Если рекордов меньше 3, то это новый рекорд
        if len(self.high_scores) < 3:
            return True
        
        # Проверяем, выше ли текущий счет минимального в топ-3
        min_score = min(score['score'] for score in self.high_scores)
        return self.current_score > min_score

    def check_events(self):
        self.global_trigger = False
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            
            elif self.state == "MAIN_MENU":
                self.handle_main_menu_events(event)
            
            elif self.state == "MAP_SELECT":
                self.handle_map_select_events(event)
            
            elif self.state == "HIGH_SCORES":
                self.handle_high_scores_events(event)
            
            elif self.state == "PLAYING":
                if event.type == self.global_event:
                    self.global_trigger = True
                self.player.single_fire_event(event)
                
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.state = "MAIN_MENU"
                    pg.mouse.set_visible(True)
                    pg.event.set_grab(False)
                    pg.mixer.music.stop()
            
            elif self.state in ["GAME_OVER", "WIN"]:
                self.handle_game_end_events(event)

    def handle_main_menu_events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self.selected_menu_item = (self.selected_menu_item + 1) % len(self.main_menu_items)
            elif event.key == pg.K_UP:
                self.selected_menu_item = (self.selected_menu_item - 1) % len(self.main_menu_items)
            elif event.key == pg.K_RETURN:
                if self.selected_menu_item == 0:
                    self.state = "MAP_SELECT"
                    self.selected_map_item = 0
                elif self.selected_menu_item == 1:
                    self.state = "HIGH_SCORES"
                elif self.selected_menu_item == 2:
                    pg.quit()
                    sys.exit()
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

    def handle_map_select_events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self.selected_map_item = (self.selected_map_item + 1) % len(self.maps)
            elif event.key == pg.K_UP:
                self.selected_map_item = (self.selected_map_item - 1) % len(self.maps)
            elif event.key == pg.K_RETURN:
                if self.selected_map_item < len(self.maps):
                    self.selected_map = self.selected_map_item
                    self.state = "LOADING"
                    pg.display.flip()
                    pg.time.delay(1000)
                    self.start_game()
            elif event.key == pg.K_ESCAPE:
                self.state = "MAIN_MENU"

    def handle_high_scores_events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.state = "MAIN_MENU"

    def handle_game_end_events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE or event.key == pg.K_RETURN:
                self.state = "MAIN_MENU"
                pg.mouse.set_visible(True)
                pg.event.set_grab(False)
                pg.mixer.music.stop()
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

    def start_game(self):
        self.new_game(self.selected_map)
        self.state = "PLAYING"
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

    def run(self):
        self.screen.fill((0, 0, 0))
        loading_text = self.large_font.render("Загрузка игры...", True, (255, 255, 255))
        self.screen.blit(loading_text, (WIDTH//2 - loading_text.get_width()//2, HEIGHT//2))
        pg.display.flip()
        
        try:
            pg.mixer.music.load('resources/sound/theme.mp3')
            pg.mixer.music.set_volume(0.3)
            pg.mixer.music.play(-1)
        except:
            pass
        
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()