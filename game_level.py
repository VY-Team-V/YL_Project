# game_level.py
import constants as const


class GameLevel:
    """Уровень игры, содержит карту и список стен."""
    def __init__(self, main_game, level_id=0):
        self.main_game = main_game
        self.level_id = level_id
        self.mini_map = const.LEVELS[level_id]
        self.world_map = {}  # словарь (x, y) -> id текстуры
        self.rows = len(self.mini_map)
        self.cols = len(self.mini_map[0])
        self.build_world()

    def build_world(self):
        """Заполняет world_map на основе mini_map."""
        for j, row in enumerate(self.mini_map):
            for i, value in enumerate(row):
                if value:
                    self.world_map[(i, j)] = value