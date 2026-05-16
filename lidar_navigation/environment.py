"""
environment.py
2B simülasyon ortamı: engeller, başlangıç ve hedef noktaları.
"""

import numpy as np


class Obstacle:
    """Dairesel 2B engel."""

    def __init__(self, x: float, y: float, radius: float):
        self.x = x
        self.y = y
        self.radius = radius
        self.center = np.array([x, y], dtype=float)


class Environment:
    """
    50 x 50 birimlik 2B simülasyon ortamı.

    - 12 dairesel engel
    - Başlangıç : (2, 2)
    - Hedef     : (45, 45)
    """

    WIDTH  = 50.0
    HEIGHT = 50.0
    START  = np.array([2.0,  2.0])
    GOAL   = np.array([45.0, 45.0])

    # (cx, cy, radius)  — en az 10 engel zorunlu; burada 12 adet tanımlandı
    _OBSTACLE_PARAMS = [
        ( 8.0,  6.0, 1.5),
        (14.0, 12.0, 2.0),
        ( 6.0, 18.0, 1.5),
        (20.0,  8.0, 1.5),
        (22.0, 20.0, 2.0),
        (28.0, 14.0, 1.5),
        (12.0, 30.0, 2.0),
        (32.0, 24.0, 1.5),
        (38.0, 32.0, 1.5),
        (24.0, 36.0, 2.0),
        (34.0, 40.0, 1.5),
        (18.0, 22.0, 1.5),
    ]

    def __init__(self):
        self.width     = self.WIDTH
        self.height    = self.HEIGHT
        self.start     = self.START.copy()
        self.goal      = self.GOAL.copy()
        self.obstacles = [Obstacle(x, y, r) for x, y, r in self._OBSTACLE_PARAMS]

    def is_collision(self, pos: np.ndarray, robot_radius: float = 0.3) -> bool:
        for obs in self.obstacles:
            if np.linalg.norm(pos - obs.center) < obs.radius + robot_radius:
                return True
        return False

    def closest_obstacle_dist(self, pos: np.ndarray) -> float:
        return min(np.linalg.norm(pos - obs.center) - obs.radius
                   for obs in self.obstacles)
