"""
navigation.py
Yapay Potansiyel Alan (APF) tabanlı reaktif navigasyon.

Potansiyel fonksiyonları
─────────────────────────
    Çekici potansiyel:
        U_att = 0.5 * k_att * ||pos - goal||^2
        F_att = k_att * (goal - pos)

    İtici potansiyel (her engel için, d = engel yüzeyine mesafe):
        U_rep = 0.5 * k_rep * (1/d - 1/d0)^2    eğer d < d0
        F_rep = k_rep * (1/d - 1/d0) / d^2 * (pos - obs_center) / ||pos - obs_center||

    Toplam kuvvet:
        F_total = F_att + sum(F_rep_i)

Hız komutları
─────────────
    theta_desired = atan2(F_total_y, F_total_x)
    theta_error   = wrap(theta_desired - theta)
    v             = v_max * max(0, cos(theta_error))
    omega         = clip(k_omega * theta_error, ±omega_max)

Yerel minimum kaçış
────────────────────
Belirli adım sayısından sonra ilerleme yoksa kuvvet vektörü 90° döndürülür.
"""

import numpy as np


class APFNavigator:
    """
    Yapay Potansiyel Alan tabanlı reaktif gezgin planlayıcı.

    Parametreler
    ------------
    goal      : Hedef konum [x, y]
    obstacles : environment.Obstacle listesi
    k_att     : Çekici alan katsayısı
    k_rep     : İtici alan katsayısı
    d0        : İtici alanın etkili mesafesi (m)
    v_max     : Maksimum doğrusal hız (m/s)
    omega_max : Maksimum açısal hız (rad/s)
    k_omega   : Açısal hız kontrolcü kazancı
    """

    def __init__(self, goal, obstacles,
                 k_att: float   = 1.2,
                 k_rep: float   = 8.0,
                 d0: float      = 4.0,
                 v_max: float   = 2.0,
                 omega_max: float = 1.8,
                 k_omega: float = 3.0):
        self.goal      = np.array(goal, dtype=float)
        self.obstacles = obstacles
        self.k_att     = k_att
        self.k_rep     = k_rep
        self.d0        = d0
        self.v_max     = v_max
        self.omega_max = omega_max
        self.k_omega   = k_omega

        self._prev_pos: np.ndarray = None
        self._stuck_count: int     = 0

    # ------------------------------------------------------------------ #
    def compute_commands(self, robot_state: np.ndarray) -> tuple:
        """
        Robotun mevcut durumundan (x, y, theta) hız komutları üret.

        Döndürür
        --------
        (v, omega) : Doğrusal ve açısal hız komutları
        """
        pos   = robot_state[:2].copy()
        theta = float(robot_state[2])

        # Yerel minimum tespiti
        if self._prev_pos is not None:
            if np.linalg.norm(pos - self._prev_pos) < 0.008:
                self._stuck_count += 1
            else:
                self._stuck_count = 0
        self._prev_pos = pos.copy()

        F = self._attractive(pos) + self._repulsive(pos)

        # Kaçış manevrası: kuvvet vektörünü döndür
        if self._stuck_count > 25:
            sign  = 1 if (self._stuck_count // 25) % 2 == 0 else -1
            angle = sign * np.pi / 2
            c, s  = np.cos(angle), np.sin(angle)
            F     = np.array([c * F[0] - s * F[1],
                               s * F[0] + c * F[1]])
            if self._stuck_count > 100:
                self._stuck_count = 0

        desired_theta = np.arctan2(F[1], F[0])
        theta_error   = _wrap(desired_theta - theta)

        v     = self.v_max * max(0.0, float(np.cos(theta_error)))
        omega = float(np.clip(self.k_omega * theta_error,
                              -self.omega_max, self.omega_max))
        return v, omega

    # ------------------------------------------------------------------ #
    def _attractive(self, pos: np.ndarray) -> np.ndarray:
        return self.k_att * (self.goal - pos)

    def _repulsive(self, pos: np.ndarray) -> np.ndarray:
        F_rep = np.zeros(2)
        for obs in self.obstacles:
            vec  = pos - obs.center
            dist = np.linalg.norm(vec)
            d    = max(dist - obs.radius, 1e-3)   # engel yüzeyine mesafe
            if d < self.d0:
                mag    = self.k_rep * (1.0 / d - 1.0 / self.d0) / (d ** 2)
                F_rep += mag * (vec / dist)
        return F_rep


# ─── Yardımcı ───────────────────────────────────────────────────────────────

def _wrap(a: float) -> float:
    return float(np.arctan2(np.sin(a), np.cos(a)))
