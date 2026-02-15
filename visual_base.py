# visual_base.py
import arcade
import constants as const


class VisualBase:
    """Базовая сущность для визуальных объектов (не анимированных)."""
    def __init__(self, main_game, texture, pos=(10.5, 3.5), scale=0.7):
        self.main_game = main_game
        self.avatar = main_game.avatar
        self.x, self.y = pos[0] * const.CELL_SIZE, pos[1] * const.CELL_SIZE
        self.width = 30
        self.height = 30

    def draw(self):
        """Отрисовка объекта (пустая)."""
        pass


class AnimatedVisual(VisualBase):
    """Анимированная визуальная сущность."""
    def __init__(self, main_game, texture_path, pos=(11.5, 3.5), scale=0.8, animation_time=120):
        super().__init__(main_game, texture_path, pos, scale)
        self.animation_time = animation_time
        self.animation_time_prev = 0
        self.current_image = 0

    def update_frame(self, delta_time):
        """Обновление кадра анимации по времени."""
        self.animation_time_prev += delta_time * 1000
        if self.animation_time_prev > self.animation_time:
            self.animation_time_prev = 0
            self.current_image = (self.current_image + 1) % 4