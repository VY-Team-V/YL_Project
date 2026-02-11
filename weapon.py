from sprite_object import AnimatedSprite

class Weapon(AnimatedSprite):
    def __init__(self, game):
        super().__init__(game, '', scale=0.4, animation_time=90)
        self.reloading = False
        self.frame_counter = 0
        self.damage = 50

    def animate_shot(self, delta_time):
        if self.reloading:
            self.update(delta_time)
            self.frame_counter += 1
            if self.frame_counter >= 4:
                self.reloading = False
                self.frame_counter = 0
