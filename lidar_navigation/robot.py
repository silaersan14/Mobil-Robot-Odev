"""
robot.py
Non-holonomic diferansiyel sürüşlü mobil robot modeli.

Durum vektörü: x = [x (m), y (m), theta (rad)]

Kinematik denklemler:
    x_{t+1}     = x_t + v * cos(theta_t) * dt
    y_{t+1}     = y_t + v * sin(theta_t) * dt
    theta_{t+1} = theta_t + omega * dt
"""

import numpy as np


class DifferentialDriveRobot:
    """
    Diferansiyel sürüşlü non-holonomic robot.

    Parametreler
    ------------
    x, y    : Başlangıç konumu (m)
    theta   : Başlangıç yönelimi (rad)
    wheel_base : Tekerlekler arası mesafe (m)
    """

    def __init__(self, x: float = 2.0, y: float = 2.0,
                 theta: float = 0.0, wheel_base: float = 0.5):
        self.state      = np.array([x, y, theta], dtype=float)
        self.wheel_base = wheel_base
        self.history: list = [self.state.copy()]

    # ------------------------------------------------------------------ #
    def step(self, v: float, omega: float, dt: float) -> np.ndarray:
        """
        Bir adım ilerle.

        Parametreler
        ------------
        v     : Doğrusal hız (m/s)
        omega : Açısal hız (rad/s)
        dt    : Zaman adımı (s)

        Döndürür
        --------
        Güncel durum vektörü [x, y, theta]
        """
        x, y, theta = self.state

        x_new     = x + v * np.cos(theta) * dt
        y_new     = y + v * np.sin(theta) * dt
        theta_new = _wrap_angle(theta + omega * dt)

        self.state = np.array([x_new, y_new, theta_new])
        self.history.append(self.state.copy())
        return self.state.copy()

    # ------------------------------------------------------------------ #
    @property
    def position(self) -> np.ndarray:
        return self.state[:2].copy()

    @property
    def theta(self) -> float:
        return float(self.state[2])


# ------------------------------------------------------------------ #
def _wrap_angle(a: float) -> float:
    return float(np.arctan2(np.sin(a), np.cos(a)))
