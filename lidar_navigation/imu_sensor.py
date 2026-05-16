"""
imu_sensor.py
IMU (Inertial Measurement Unit) sensör simülasyonu.

Ölçüm modeli:
    omega_meas = omega_true + bias + N(0, sigma^2)

Parametreler
------------
noise_std : Açısal hız gürültüsü standart sapması (rad/s)
bias      : Sabit ofset hatası (rad/s)
"""

import numpy as np


class IMUSensor:
    """Simüle edilmiş IMU — açısal hız (yaw rate) ölçümü."""

    def __init__(self, noise_std: float = 0.01, bias: float = 0.002):
        self.noise_std = noise_std
        self.bias      = bias
        self._rng      = np.random.default_rng(seed=10)

    def measure(self, true_omega: float) -> float:
        """
        Gerçek açısal hızı gürültülü olarak ölç.

        Parametreler
        ------------
        true_omega : Gerçek açısal hız (rad/s)

        Döndürür
        --------
        Gürültülü açısal hız ölçümü (rad/s)
        """
        return true_omega + self.bias + self._rng.normal(0.0, self.noise_std)
