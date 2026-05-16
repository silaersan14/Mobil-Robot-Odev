"""
visualization.py
Tüm matplotlib grafik fonksiyonları.

Grafik grupları
───────────────
1. plot_environment  — 2B ortam haritası (engeller, start, goal)
2. plot_paths        — Planlanan yol vs gerçek yol vs EKF vs DR
3. plot_lidar        — LiDAR ham + filtrelenmiş veri (2 alt grafik)
4. plot_localization — x(t), y(t), theta(t) karşılaştırması (3 alt grafik)
5. plot_errors       — Pozisyon ve yönelim hata analizi + RMSE/MAE

Her grafik: başlık, eksen etiketleri, birimler, legend içerir.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D


# ─── Renk paleti ────────────────────────────────────────────────────────────
_C_TRUE    = '#2196F3'   # mavi  — gerçek yol
_C_EKF     = '#FF9800'   # turuncu — EKF tahmini
_C_DR      = '#F44336'   # kırmızı — dead reckoning
_C_PLANNED = '#4CAF50'   # yeşil — planlanan yol
_C_OBS     = '#607D8B'   # gri-mavi — engeller


# ─────────────────────────────────────────────────────────────────────────── #
def plot_environment(env) -> plt.Figure:
    """
    Grafik 1: 2B Ortam Haritası
    Engeller, başlangıç noktası ve hedef noktası.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    _draw_obstacles(ax, env)

    ax.plot(*env.start, 'g*', markersize=18, zorder=6, label='Başlangıç (2, 2)')
    ax.plot(*env.goal,  'r*', markersize=18, zorder=6, label='Hedef (45, 45)')

    # Sınır çizgisi
    rect = mpatches.FancyBboxPatch((0, 0), env.width, env.height,
                                   boxstyle='square,pad=0',
                                   linewidth=2, edgecolor='black',
                                   facecolor='none', zorder=1)
    ax.add_patch(rect)

    ax.set_xlim(-1, env.width  + 1)
    ax.set_ylim(-1, env.height + 1)
    ax.set_aspect('equal')
    ax.set_xlabel('x (m)', fontsize=12)
    ax.set_ylabel('y (m)', fontsize=12)
    ax.set_title('2B Ortam Haritası: Engeller, Başlangıç ve Hedef Noktaları',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────── #
def plot_paths(env,
               planned_path: np.ndarray,
               true_states:  np.ndarray,
               ekf_states:   np.ndarray,
               dr_states:    np.ndarray) -> plt.Figure:
    """
    Grafik 2: Robot Yol Karşılaştırması
    Planlanan yol / gerçek yol / EKF tahmini / Dead Reckoning.
    """
    fig, ax = plt.subplots(figsize=(9, 8))
    _draw_obstacles(ax, env)

    ax.plot(planned_path[:, 0], planned_path[:, 1],
            color=_C_PLANNED, lw=2.0, ls='-.',
            label='Planlanan Yol (Gürültüsüz APF)', zorder=3)
    ax.plot(true_states[:, 0], true_states[:, 1],
            color=_C_TRUE, lw=2.0, ls='-',
            label='Gerçek Yol', zorder=4)
    ax.plot(ekf_states[:, 0], ekf_states[:, 1],
            color=_C_EKF, lw=1.8, ls='--',
            label='EKF Tahmini', zorder=4)
    ax.plot(dr_states[:, 0], dr_states[:, 1],
            color=_C_DR, lw=1.5, ls=':',
            label='Dead Reckoning', zorder=4)

    ax.plot(*env.start, 'g*', markersize=16, zorder=6)
    ax.plot(*env.goal,  'r*', markersize=16, zorder=6)

    ax.set_xlim(-1, env.width  + 1)
    ax.set_ylim(-1, env.height + 1)
    ax.set_aspect('equal')
    ax.set_xlabel('x (m)', fontsize=12)
    ax.set_ylabel('y (m)', fontsize=12)
    ax.set_title('Robot Yol Karşılaştırması: Planlanan / Gerçek / EKF / Dead Reckoning',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────── #
def plot_lidar(raw_ranges:      np.ndarray,
               filtered_ranges: np.ndarray,
               robot_state:     np.ndarray,
               lidar_angles:    np.ndarray,
               max_range:       float) -> plt.Figure:
    """
    Grafik 3: LiDAR Sensör Görselleştirmesi
    Sol: Ham veri  |  Sağ: Filtrelenmiş veri
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    configs = [
        (axes[0], raw_ranges,      'LiDAR Ham Veri (Gürültülü)',         '#9E9E9E'),
        (axes[1], filtered_ranges, 'LiDAR Filtrelenmiş Veri (Hareketli Ort.)', '#1976D2'),
    ]

    x, y, theta = robot_state

    for ax, ranges, title, color in configs:
        mask   = ranges < max_range
        angles = (theta + lidar_angles)[mask]
        r      = ranges[mask]
        px     = x + r * np.cos(angles)
        py     = y + r * np.sin(angles)

        ax.scatter(px, py, s=3, c=color, alpha=0.7, label='Tarama Noktaları')
        ax.plot(x, y, 'ro', markersize=9, zorder=5, label='Robot Konumu')

        ax.set_xlabel('x (m)', fontsize=11)
        ax.set_ylabel('y (m)', fontsize=11)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)

    fig.suptitle('LiDAR Sensör Görselleştirmesi  (t ≈ 10 s anlık görüntü)',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────── #
def plot_localization(timestamps:  np.ndarray,
                      true_states: np.ndarray,
                      ekf_states:  np.ndarray,
                      dr_states:   np.ndarray) -> plt.Figure:
    """
    Grafik 4: Lokalizasyon Sonuçları
    x(t), y(t), theta(t) — Gerçek vs EKF vs Dead Reckoning
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    configs = [
        (0, 'x(t)  (m)',    'x Konumu Karşılaştırması'),
        (1, 'y(t)  (m)',    'y Konumu Karşılaştırması'),
        (2, 'θ(t)  (rad)',  'Yönelim θ Karşılaştırması'),
    ]

    for ax, (idx, ylabel, title) in zip(axes, configs):
        ax.plot(timestamps, true_states[:, idx],
                color=_C_TRUE, lw=2.0, ls='-',  label='Gerçek')
        ax.plot(timestamps, ekf_states[:, idx],
                color=_C_EKF,  lw=1.8, ls='--', label='EKF')
        ax.plot(timestamps, dr_states[:, idx],
                color=_C_DR,   lw=1.5, ls=':',  label='Dead Reckoning')
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title,   fontsize=11)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel('Zaman (s)', fontsize=12)
    fig.suptitle('Lokalizasyon Sonuçları: Gerçek Durum vs EKF vs Dead Reckoning',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────── #
def plot_errors(timestamps:  np.ndarray,
                true_states: np.ndarray,
                ekf_states:  np.ndarray,
                dr_states:   np.ndarray) -> tuple:
    """
    Grafik 5: Hata Analizi
    Pozisyon ve yönelim hatası zaman serisi; RMSE ve MAE hesabı.

    Döndürür
    --------
    (fig, metrics_dict)
    """
    pos_err_ekf = np.linalg.norm(
        true_states[:, :2] - ekf_states[:, :2], axis=1)
    pos_err_dr  = np.linalg.norm(
        true_states[:, :2] - dr_states[:, :2],  axis=1)

    def angle_err(a, b):
        return np.abs(np.arctan2(np.sin(a - b), np.cos(a - b)))

    th_err_ekf = angle_err(true_states[:, 2], ekf_states[:, 2])
    th_err_dr  = angle_err(true_states[:, 2], dr_states[:, 2])

    metrics = {
        'RMSE_pos_EKF':   float(np.sqrt(np.mean(pos_err_ekf ** 2))),
        'MAE_pos_EKF':    float(np.mean(pos_err_ekf)),
        'RMSE_pos_DR':    float(np.sqrt(np.mean(pos_err_dr  ** 2))),
        'MAE_pos_DR':     float(np.mean(pos_err_dr)),
        'RMSE_theta_EKF': float(np.sqrt(np.mean(th_err_ekf  ** 2))),
        'MAE_theta_EKF':  float(np.mean(th_err_ekf)),
        'RMSE_theta_DR':  float(np.sqrt(np.mean(th_err_dr   ** 2))),
        'MAE_theta_DR':   float(np.mean(th_err_dr)),
    }

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    axes[0].plot(timestamps, pos_err_ekf,
                 color=_C_EKF, lw=2.0, ls='--',
                 label=f'EKF  RMSE={metrics["RMSE_pos_EKF"]:.4f} m'
                       f'  MAE={metrics["MAE_pos_EKF"]:.4f} m')
    axes[0].plot(timestamps, pos_err_dr,
                 color=_C_DR,  lw=1.5, ls=':',
                 label=f'DR   RMSE={metrics["RMSE_pos_DR"]:.4f} m'
                       f'  MAE={metrics["MAE_pos_DR"]:.4f} m')
    axes[0].set_ylabel('Pozisyon Hatası (m)', fontsize=12)
    axes[0].set_title('Zaman Boyunca Pozisyon Hatası: EKF vs Dead Reckoning',
                      fontsize=12)
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(timestamps, th_err_ekf,
                 color=_C_EKF, lw=2.0, ls='--',
                 label=f'EKF  RMSE={metrics["RMSE_theta_EKF"]:.4f} rad'
                       f'  MAE={metrics["MAE_theta_EKF"]:.4f} rad')
    axes[1].plot(timestamps, th_err_dr,
                 color=_C_DR,  lw=1.5, ls=':',
                 label=f'DR   RMSE={metrics["RMSE_theta_DR"]:.4f} rad'
                       f'  MAE={metrics["MAE_theta_DR"]:.4f} rad')
    axes[1].set_xlabel('Zaman (s)', fontsize=12)
    axes[1].set_ylabel('Yönelim Hatası (rad)', fontsize=12)
    axes[1].set_title('Zaman Boyunca Yönelim Hatası: EKF vs Dead Reckoning',
                      fontsize=12)
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)

    fig.suptitle('Hata Analizi: EKF Sensör Füzyonu vs Dead Reckoning',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    return fig, metrics


# ─── Yardımcı ───────────────────────────────────────────────────────────────

def _draw_obstacles(ax, env):
    for obs in env.obstacles:
        circle = mpatches.Circle((obs.x, obs.y), obs.radius,
                                 color=_C_OBS, alpha=0.75, zorder=2)
        ax.add_patch(circle)
