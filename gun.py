# gun.py
from visual_base import AnimatedVisual


class Gun(AnimatedVisual):
    """Оружие игрока."""
    def __init__(self, main_game):
        super().__init__(main_game, '', scale=0.4, animation_time=90)
        self.reloading = False
        self.frame_counter = 0
        self.damage = 50

    def animate_fire(self, delta_time):
        """Анимация выстрела (перезарядка)."""
        if self.reloading:
            self.update_frame(delta_time)
            self.frame_counter += 1
            if self.frame_counter >= 4:
                self.reloading = False
                self.frame_counter = 0

    def draw(self):
        pass