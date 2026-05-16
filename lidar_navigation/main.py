"""
main.py
Sensör Füzyonu ve Lokalizasyon Kullanarak LiDAR Tabanlı Otonom Navigasyon
=========================================================================
Mobil Robotlar Dersi — Simülasyon Giriş Noktası

Çalıştırma
----------
    python main.py

Çıktılar
--------
- 5 matplotlib grafik penceresi
- Terminal'de RMSE ve MAE değerleri
"""

import numpy as np
import matplotlib.pyplot as plt

from environment   import Environment
from robot         import DifferentialDriveRobot
from lidar_sensor  import LiDARSensor
from imu_sensor    import IMUSensor
from encoder_sensor import WheelEncoder
from ekf           import ExtendedKalmanFilter
from navigation    import APFNavigator
from visualization import (plot_environment, plot_paths, plot_lidar,
                           plot_localization, plot_errors)


# ─── Simülasyon parametreleri ────────────────────────────────────────────── #
DT              = 0.1     # zaman adımı (s)
MAX_STEPS       = 3000    # maksimum adım sayısı
GOAL_THRESHOLD  = 1.5     # hedef yakınlık eşiği (m)
LIDAR_SNAP_STEP = 100     # LiDAR anlık görüntü adımı


def _wrap(a: float) -> float:
    return float(np.arctan2(np.sin(a), np.cos(a)))


# ─────────────────────────────────────────────────────────────────────────── #
def compute_planned_path(env: Environment) -> np.ndarray:
    """
    Gürültüsüz (ideal) APF simülasyonu ile referans yolu hesapla.
    Bu yol "planlanan yol" olarak grafikte gösterilir.
    """
    from robot     import DifferentialDriveRobot
    from navigation import APFNavigator

    init_theta = float(np.arctan2(env.goal[1] - env.start[1],
                                  env.goal[0] - env.start[0]))
    robot_sim = DifferentialDriveRobot(env.start[0], env.start[1], init_theta)
    nav_sim   = APFNavigator(goal=env.goal, obstacles=env.obstacles)

    planned = [robot_sim.state[:2].copy()]
    for _ in range(MAX_STEPS):
        v, omega = nav_sim.compute_commands(robot_sim.state)
        robot_sim.step(v, omega, DT)
        planned.append(robot_sim.state[:2].copy())
        if np.linalg.norm(robot_sim.state[:2] - env.goal) < GOAL_THRESHOLD:
            break

    return np.array(planned)


# ─────────────────────────────────────────────────────────────────────────── #
def run_simulation():
    """Ana simülasyon döngüsü."""
    env = Environment()

    init_theta = float(np.arctan2(env.goal[1] - env.start[1],
                                  env.goal[0] - env.start[0]))

    robot   = DifferentialDriveRobot(env.start[0], env.start[1], init_theta)
    lidar   = LiDARSensor(max_range=10.0, num_beams=360, noise_std=0.05)
    imu     = IMUSensor(noise_std=0.01,  bias=0.002)
    encoder = WheelEncoder(noise_std_v=0.02, noise_std_omega=0.01)
    ekf     = ExtendedKalmanFilter([env.start[0], env.start[1], init_theta])
    nav     = APFNavigator(goal=env.goal, obstacles=env.obstacles)

    # Dead reckoning durumu (enkoder entegrasyonu, füzyon yok)
    dr_state = np.array([env.start[0], env.start[1], init_theta])

    # Geçmiş kayıtları
    true_states: list = [robot.state.copy()]
    ekf_states:  list = [ekf.get_state()]
    dr_states:   list = [dr_state.copy()]
    timestamps:  list = [0.0]

    # LiDAR anlık görüntüsü
    lidar_raw_snap    = None
    lidar_filt_snap   = None
    lidar_robot_state = None

    print("=" * 58)
    print(" LiDAR Tabanli Otonom Navigasyon Simulasyonu")
    print("=" * 58)
    print(f"  Baslangic : {env.start},  Hedef : {env.goal}")
    print(f"  Engel sayisi : {len(env.obstacles)}")
    print(f"  dt={DT} s,  max_steps={MAX_STEPS}")
    print("-" * 58)

    for step in range(MAX_STEPS):
        t = (step + 1) * DT

        # 1) Navigasyon komutu (EKF tahminine göre — gerçekçi senaryo)
        v_cmd, omega_cmd = nav.compute_commands(ekf.get_state())

        # 2) Gerçek robot adımı
        robot.step(v_cmd, omega_cmd, DT)

        # 3) Sensör okuma
        raw_ranges, filt_ranges = lidar.scan(robot.state, env.obstacles)
        v_enc,    omega_enc     = encoder.measure(v_cmd, omega_cmd)
        omega_imu               = imu.measure(omega_cmd)

        # 4) Dead reckoning (sadece enkoder, füzyon yok)
        dr_x     = dr_state[0] + v_enc * np.cos(dr_state[2]) * DT
        dr_y     = dr_state[1] + v_enc * np.sin(dr_state[2]) * DT
        dr_theta = _wrap(dr_state[2] + omega_enc * DT)
        dr_state = np.array([dr_x, dr_y, dr_theta])

        # 5) EKF: tahmin (enkoder) + güncelleme (IMU)
        ekf.predict(v_enc, omega_enc, DT)
        ekf.update_imu(omega_imu, DT)

        # 6) Kayıt
        true_states.append(robot.state.copy())
        ekf_states.append(ekf.get_state())
        dr_states.append(dr_state.copy())
        timestamps.append(t)

        # LiDAR anlık görüntüsü
        if step == LIDAR_SNAP_STEP:
            lidar_raw_snap    = raw_ranges
            lidar_filt_snap   = filt_ranges
            lidar_robot_state = robot.state.copy()

        # Hedefe ulaşma kontrolü
        dist = np.linalg.norm(robot.state[:2] - env.goal)
        if dist < GOAL_THRESHOLD:
            print(f"  [OK] Hedefe ulasildi!  Adim={step+1},  t={t:.1f} s")
            break

        if (step + 1) % 500 == 0:
            print(f"  Adim {step+1:4d} | pos=({robot.state[0]:5.1f},"
                  f" {robot.state[1]:5.1f}) | d_goal={dist:.1f} m")
    else:
        print("  [!] Maksimum adim sayisina ulasildi.")

    print("-" * 58)

    return (
        np.array(true_states),
        np.array(ekf_states),
        np.array(dr_states),
        np.array(timestamps),
        env, lidar,
        lidar_raw_snap, lidar_filt_snap, lidar_robot_state,
    )


# ─────────────────────────────────────────────────────────────────────────── #
def main():
    # ── Simülasyonu çalıştır ──────────────────────────────────────────── #
    (true_states, ekf_states, dr_states, timestamps,
     env, lidar,
     raw_snap, filt_snap, snap_state) = run_simulation()

    # ── Planlanan (ideal) yolu hesapla ───────────────────────────────── #
    print("  Referans yol (planlanan) hesaplaniyor...")
    planned_path = compute_planned_path(env)

    # -- Grafikler -------------------------------------------------------- #
    print("  Grafikler olusturuluyor...")

    fig1 = plot_environment(env)
    fig2 = plot_paths(env, planned_path, true_states, ekf_states, dr_states)

    if raw_snap is not None:
        fig3 = plot_lidar(raw_snap, filt_snap, snap_state,
                          lidar.angles, lidar.max_range)
    else:
        print("  [!] LiDAR anlik goruntu alinamadi (adim sayisi yetersiz).")

    fig4 = plot_localization(timestamps, true_states, ekf_states, dr_states)
    fig5, metrics = plot_errors(timestamps, true_states, ekf_states, dr_states)

    # -- Grafikleri kaydet ------------------------------------------------ #
    import os
    out_dir = os.path.join(os.path.dirname(__file__), "figures")
    os.makedirs(out_dir, exist_ok=True)
    fig1.savefig(os.path.join(out_dir, "fig1_ortam_haritasi.png"),     dpi=200, bbox_inches='tight')
    fig2.savefig(os.path.join(out_dir, "fig2_yol_karsilastirma.png"),  dpi=200, bbox_inches='tight')
    if raw_snap is not None:
        fig3.savefig(os.path.join(out_dir, "fig3_lidar.png"),          dpi=200, bbox_inches='tight')
    fig4.savefig(os.path.join(out_dir, "fig4_lokalizasyon.png"),       dpi=200, bbox_inches='tight')
    fig5.savefig(os.path.join(out_dir, "fig5_hata_analizi.png"),       dpi=200, bbox_inches='tight')
    print(f"  Grafikler kaydedildi --> {out_dir}")

    # ── Metrikler ─────────────────────────────────────────────────────── #
    print()
    print("=" * 58)
    print("  HATA METRIKLERI")
    print("=" * 58)
    print(f"  EKF  Pozisyon RMSE  : {metrics['RMSE_pos_EKF']:.4f} m")
    print(f"  EKF  Pozisyon MAE   : {metrics['MAE_pos_EKF']:.4f} m")
    print(f"  DR   Pozisyon RMSE  : {metrics['RMSE_pos_DR']:.4f} m")
    print(f"  DR   Pozisyon MAE   : {metrics['MAE_pos_DR']:.4f} m")
    print(f"  EKF  Yonelim RMSE   : {metrics['RMSE_theta_EKF']:.4f} rad")
    print(f"  EKF  Yonelim MAE    : {metrics['MAE_theta_EKF']:.4f} rad")
    print(f"  DR   Yonelim RMSE   : {metrics['RMSE_theta_DR']:.4f} rad")
    print(f"  DR   Yonelim MAE    : {metrics['MAE_theta_DR']:.4f} rad")
    print("=" * 58)

    plt.show()


if __name__ == "__main__":
    main()
