# path_solver.py
from collections import deque
from functools import lru_cache


class PathSolver:
    """Поиск пути для NPC (BFS на графе проходимых клеток)."""
    def __init__(self, main_game):
        self.main_game = main_game
        self.mini_map = main_game.level.mini_map
        self.ways = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (1, 1), (-1, 1)]
        self.graph = {}
        self.build_graph()

    @lru_cache(maxsize=None)
    def find_path(self, start, goal):
        """Возвращает следующую клетку на пути от start к goal."""
        visited = self.breadth_first_search(start, goal)
        path = [goal]
        step = visited.get(goal, start)
        while step and step != start:
            path.append(step)
            step = visited[step]
        return path[-1] if path else start

    def breadth_first_search(self, start, goal):
        """BFS для построения маршрута."""
        queue = deque([start])
        visited = {start: None}
        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break
            next_nodes = self.graph.get(cur_node, [])
            for next_node in next_nodes:
                if next_node not in visited:
                    queue.append(next_node)
                    visited[next_node] = cur_node
        return visited

    def get_neighbors(self, x, y):
        """Возвращает список соседних проходимых клеток."""
        return [(x + dx, y + dy) for dx, dy in self.ways if (x + dx, y + dy) not in self.main_game.level.world_map]

    def build_graph(self):
        """Строит граф проходимости по карте."""
        for y, row in enumerate(self.mini_map):
            for x, col in enumerate(row):
                if not col:
                    self.graph[(x, y)] = self.get_neighbors(x, y)