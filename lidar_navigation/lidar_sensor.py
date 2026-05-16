"""
lidar_sensor.py
Işın izleme (ray-casting) yöntemiyle 2B LiDAR sensör simülasyonu.

Özellikler
----------
- 360° tarama, 1° çözünürlük (360 ışın)
- Ray-circle kesişim hesabıyla gerçek mesafe ölçümü
- Gaussian gürültü ekleme  (sigma = noise_std)
- Mesafe eşikleme (max_range)
- Hareketli ortalama filtresi (filtrelenmiş veri)
- Mesafe tabanlı DBSCAN-lite engel kümeleme
"""

import numpy as np
from environment import Obstacle


class LiDARSensor:
    """
    2B LiDAR sensörü.

    Parametreler
    ------------
    max_range  : Maksimum algılama mesafesi (m)
    num_beams  : Işın sayısı (= açısal çözünürlük: 360/num_beams derece)
    noise_std  : Gaussian gürültü standart sapması (m)
    """

    def __init__(self, max_range: float = 10.0,
                 num_beams: int = 360,
                 noise_std: float = 0.05):
        self.max_range = max_range
        self.num_beams = num_beams
        self.noise_std = noise_std
        self.angles    = np.linspace(0.0, 2 * np.pi, num_beams, endpoint=False)
        self._rng      = np.random.default_rng(seed=42)

    # ------------------------------------------------------------------ #
    def scan(self, robot_state: np.ndarray,
             obstacles: list) -> tuple:
        """
        LiDAR taraması gerçekleştir.

        Döndürür
        --------
        raw_ranges      : Gürültülü ham mesafe dizisi  (num_beams,)
        filtered_ranges : Filtre sonrası mesafe dizisi (num_beams,)
        """
        x, y, theta = robot_state
        ideal_ranges = np.full(self.num_beams, self.max_range)

        for i, local_angle in enumerate(self.angles):
            global_angle = theta + local_angle
            dx = np.cos(global_angle)
            dy = np.sin(global_angle)

            for obs in obstacles:
                hit = _ray_circle_intersect(x, y, dx, dy, obs)
                if hit is not None and hit < ideal_ranges[i]:
                    ideal_ranges[i] = hit

        # Gaussian gürültü ekle ve [0, max_range] aralığına kırp
        noise      = self._rng.normal(0.0, self.noise_std, self.num_beams)
        raw_ranges = np.clip(ideal_ranges + noise, 0.0, self.max_range)

        filtered_ranges = _moving_average(raw_ranges, window=5)
        return raw_ranges, filtered_ranges

    # ------------------------------------------------------------------ #
    def ranges_to_points(self, robot_state: np.ndarray,
                         ranges: np.ndarray) -> np.ndarray:
        """Polar mesafe dizisini Kartezyen nokta bulutuna dönüştür."""
        x, y, theta = robot_state
        mask   = ranges < self.max_range
        angles = (theta + self.angles)[mask]
        r      = ranges[mask]
        return np.column_stack([x + r * np.cos(angles),
                                y + r * np.sin(angles)])

    # ------------------------------------------------------------------ #
    def cluster_points(self, points: np.ndarray,
                       eps: float = 1.5, min_pts: int = 4) -> list:
        """
        Basit mesafe tabanlı kümeleme (DBSCAN-lite).

        Döndürür
        --------
        Küme listesi; her küme bir numpy dizisidir.
        """
        if len(points) == 0:
            return []

        n       = len(points)
        visited = np.zeros(n, dtype=bool)
        clusters = []

        for i in range(n):
            if visited[i]:
                continue
            dists     = np.linalg.norm(points - points[i], axis=1)
            neighbors = np.where(dists < eps)[0]
            if len(neighbors) < min_pts:
                continue
            cluster = []
            stack   = list(neighbors)
            while stack:
                j = stack.pop()
                if visited[j]:
                    continue
                visited[j] = True
                cluster.append(points[j])
                inner = np.where(
                    np.linalg.norm(points - points[j], axis=1) < eps)[0]
                if len(inner) >= min_pts:
                    stack.extend(inner.tolist())
            if cluster:
                clusters.append(np.array(cluster))

        return clusters


# ─── Yardımcı fonksiyonlar ──────────────────────────────────────────────────

def _ray_circle_intersect(rx: float, ry: float,
                           dx: float, dy: float,
                           obs: Obstacle):
    """
    Işın-daire kesişimi hesabı.

    Işın: P(t) = (rx + t*dx, ry + t*dy),  t >= 0
    Daire: (x - cx)^2 + (y - cy)^2 = r^2

    Döndürür
    --------
    t (kesişim mesafesi) veya None (kesişim yok)
    """
    ox = obs.x - rx
    oy = obs.y - ry
    t  = ox * dx + oy * dy        # obs merkezinin ışın üzerine izdüşümü
    if t < 0:
        return None
    perp_sq = ox**2 + oy**2 - t**2
    r_sq    = obs.radius**2
    if perp_sq > r_sq:
        return None
    hit = t - np.sqrt(max(r_sq - perp_sq, 0.0))
    return hit if hit > 0 else None


def _moving_average(ranges: np.ndarray, window: int) -> np.ndarray:
    """Dairesel hareketli ortalama filtresi."""
    n        = len(ranges)
    filtered = np.empty(n)
    half     = window // 2
    for i in range(n):
        idx        = [(i + j - half) % n for j in range(window)]
        filtered[i] = np.mean(ranges[idx])
    return filtered
