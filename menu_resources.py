import arcade as ar
import pygame as pg
import json
import os


class MenuResources:
    def __init__(self):
        self.fonts = {}
        self.images = {}
        self.sounds = {}
        self.scores_file = "scores.json"
        self.high_scores = self.load_high_scores()
        
    def load_fonts(self):
        # Загрузка шрифтов
        try:
            self.fonts['large'] = pg.font.Font('resources/fonts/doom.ttf', 74)
            self.fonts['medium'] = pg.font.Font('resources/fonts/doom.ttf', 48)
            self.fonts['small'] = pg.font.Font('resources/fonts/doom.ttf', 32)
        except:
            # Резервные шрифты если кастомные не найдены
            self.fonts['large'] = pg.font.Font(None, 74)
            self.fonts['medium'] = pg.font.Font(None, 48)
            self.fonts['small'] = pg.font.Font(None, 32)
            
    def load_images(self):
        # Загрузка изображений для меню
        image_paths = {
            'menu_bg': 'resources/textures/menu_bg.png',
            'logo': 'resources/textures/logo.png',
            'button_normal': 'resources/textures/button_normal.png',
            'button_hover': 'resources/textures/button_hover.png',
            'button_pressed': 'resources/textures/button_pressed.png',
        }
        
        for name, path in image_paths.items():
            try:
                self.images[name] = pg.image.load(path).convert_alpha()
            except:
                print(f"Не удалось загрузить изображение: {path}")
                # Создаем заглушки
                if name == 'menu_bg':
                    self.images[name] = pg.Surface((1600, 900))
                    self.images[name].fill((20, 20, 40))
                elif 'button' in name:
                    self.images[name] = pg.Surface((300, 80))
                    self.images[name].fill((100, 100, 100) if 'normal' in name else 
                                          (150, 150, 150) if 'hover' in name else 
                                          (50, 50, 50))
                    
    def load_sounds(self):
        # Загрузка звуков для меню
        sound_paths = {
            'menu_select': 'resources/sound/menu_select.wav',
            'menu_confirm': 'resources/sound/menu_confirm.wav',
            'menu_back': 'resources/sound/menu_back.wav',
        }
        
        for name, path in sound_paths.items():
            try:
                self.sounds[name] = pg.mixer.Sound(path)
            except:
                print(f"Не удалось загрузить звук: {path}")
                
    def load_high_scores(self):
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except:
                return {"scores": []}
        return {"scores": []}
        
    def save_high_score(self, score_data):
        self.high_scores["scores"].append(score_data)
        # Сортируем по убыванию очков и оставляем топ-10
        self.high_scores["scores"].sort(key=lambda x: x["score"], reverse=True)
        self.high_scores["scores"] = self.high_scores["scores"][:10]
        
        with open(self.scores_file, 'w') as f:
            json.dump(self.high_scores, f)
            
    def get_top_scores(self, count=5):

        return self.high_scores["scores"][:count]
