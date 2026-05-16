"""
ekf.py
Extended Kalman Filter (EKF) — diferansiyel sürüşlü robot lokalizasyonu.

Durum vektörü
─────────────
    x = [x (m),  y (m),  theta (rad)]^T

Süreç modeli (diferansiyel sürüş kinematikleri)
────────────────────────────────────────────────
    x_{k+1}     = x_k + v_enc * cos(theta_k) * dt
    y_{k+1}     = y_k + v_enc * sin(theta_k) * dt
    theta_{k+1} = theta_k + omega_enc * dt

    Giriş u = [v_enc, omega_enc]   (enkoder ölçümleri)

Süreç Jacobianı  F = df/dx
────────────────────────────
    F = [[1,  0,  -v*sin(theta)*dt],
         [0,  1,   v*cos(theta)*dt],
         [0,  0,   1              ]]

Ölçüm modeli (IMU açısal hız → theta tahmini)
───────────────────────────────────────────────
    z        = theta_prev + omega_imu * dt       (IMU'dan theta tahmini)
    h(x)     = x[2]                              (durum vektöründen theta)
    H        = [0, 0, 1]                         (ölçüm Jacobianı)
    inovasyon = angle_wrap(z - x_pred[2])
"""

import numpy as np


def _wrap(a: float) -> float:
    return float(np.arctan2(np.sin(a), np.cos(a)))


class ExtendedKalmanFilter:
    """
    Enkoder + IMU füzyonu ile EKF lokalizasyonu.

    Parametreler
    ------------
    initial_state : [x0, y0, theta0] başlangıç durumu
    """

    def __init__(self, initial_state):
        self.x = np.array(initial_state, dtype=float)   # [x, y, theta]
        self.P = np.diag([0.10, 0.10, 0.05])            # başlangıç kovaryansı

        # Süreç gürültüsü kovaryansı Q (enkoder belirsizliği)
        self.Q = np.diag([0.02**2, 0.02**2, 0.015**2])

        # IMU ölçüm gürültüsü varyansı (theta üzerinde)
        self.R_imu = (0.012) ** 2

        self._x_prev = self.x.copy()   # güncelleme adımında kullanılır

    # ------------------------------------------------------------------ #
    def predict(self, v_enc: float, omega_enc: float, dt: float) -> None:
        """
        Enkoder ölçümleriyle durum tahminini ilerlet (Predict adımı).

        Parametreler
        ------------
        v_enc     : Enkoder doğrusal hız ölçümü (m/s)
        omega_enc : Enkoder açısal hız ölçümü (rad/s)
        dt        : Zaman adımı (s)
        """
        x, y, theta = self.x
        self._x_prev = self.x.copy()

        # Durum tahmini: f(x, u)
        x_p     = x + v_enc * np.cos(theta) * dt
        y_p     = y + v_enc * np.sin(theta) * dt
        theta_p = _wrap(theta + omega_enc * dt)
        self.x  = np.array([x_p, y_p, theta_p])

        # Linearizasyon: Jacobian F = df/dx
        F = np.array([
            [1.0, 0.0, -v_enc * np.sin(theta) * dt],
            [0.0, 1.0,  v_enc * np.cos(theta) * dt],
            [0.0, 0.0,  1.0],
        ])

        # Kovaryans tahmini
        self.P = F @ self.P @ F.T + self.Q

    # ------------------------------------------------------------------ #
    def update_imu(self, omega_imu: float, dt: float) -> None:
        """
        IMU açısal hız ölçümüyle theta'yı düzelt (Update adımı).

        Ölçüm denklemi:
            z    = theta_prev + omega_imu * dt   (IMU'dan elde edilen theta)
            h(x) = x[2]                          (tahmin edilen theta)
            H    = [0, 0, 1]

        Parametreler
        ------------
        omega_imu : IMU açısal hız ölçümü (rad/s)
        dt        : Zaman adımı (s)
        """
        # IMU'dan elde edilen theta gözlemi
        z_theta = _wrap(self._x_prev[2] + omega_imu * dt)

        # Ölçüm Jacobianı
        H = np.array([[0.0, 0.0, 1.0]])

        # İnovasyon (açı sarmalamasıyla)
        innovation = _wrap(z_theta - self.x[2])

        # Kalman kazancı
        S = float((H @ self.P @ H.T)[0, 0]) + self.R_imu
        K = (self.P @ H.T / S).flatten()          # shape (3,)

        # Durum ve kovaryans güncelleme
        self.x    = self.x + K * innovation
        self.x[2] = _wrap(self.x[2])
        self.P    = (np.eye(3) - np.outer(K, H)) @ self.P

        # Kovaryansı simetrik tut (sayısal kararlılık)
        self.P = (self.P + self.P.T) * 0.5

    # ------------------------------------------------------------------ #
    def get_state(self) -> np.ndarray:
        return self.x.copy()
