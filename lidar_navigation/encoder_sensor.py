"""
encoder_sensor.py
Tekerlek enkoderi sensör simülasyonu.

Ölçüm modeli:
    v_meas     = v_true     + N(0, sigma_v^2)
    omega_meas = omega_true + N(0, sigma_omega^2)

Parametreler
------------
noise_std_v     : Doğrusal hız gürültüsü standart sapması (m/s)
noise_std_omega : Açısal hız gürültüsü standart sapması (rad/s)
"""

import numpy as np


class WheelEncoder:
    """Simüle edilmiş tekerlek enkoderi."""

    def __init__(self, noise_std_v: float = 0.02,
                 noise_std_omega: float = 0.01):
        self.noise_std_v     = noise_std_v
        self.noise_std_omega = noise_std_omega
        self._rng            = np.random.default_rng(seed=20)

    def measure(self, true_v: float,
                true_omega: float) -> tuple:
        """
        Gerçek hızları gürültülü olarak ölç.

        Döndürür
        --------
        (v_meas, omega_meas) : Gürültülü doğrusal ve açısal hız (m/s, rad/s)
        """
        v_meas     = true_v     + self._rng.normal(0.0, self.noise_std_v)
        omega_meas = true_omega + self._rng.normal(0.0, self.noise_std_omega)
        return float(v_meas), float(omega_meas)
