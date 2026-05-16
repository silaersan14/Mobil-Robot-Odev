# Mobil-Robot-Odev
# LiDAR Tabanlı Otonom Navigasyon — Sensör Füzyonu ve Lokalizasyon

> **Mobil Robotlar Dersi — Proje Ödevi**  
> Konu: *Sensör Füzyonu ve Lokalizasyon Kullanarak LiDAR Tabanlı Otonom Navigasyon (2B Simülasyon)*


## İçindekiler

1. [Proje Özeti](#proje-özeti)
2. [Senaryo](#senaryo)
3. [Kullanılan Yöntemler](#kullanılan-yöntemler)
4. [Dosya Yapısı](#dosya-yapısı)
5. [Kurulum](#kurulum)
6. [Çalıştırma](#çalıştırma)
7. [Çıktılar](#çıktılar)
8. [Yapay Zeka Kullanım Beyanı](#yapay-zeka-kullanım-beyanı)


## Proje Özeti

Bu proje, Python kullanarak 2B bir simülasyon ortamında LiDAR tabanlı otonom navigasyon gerçekleştirir. Sistemde:

- **Non-holonomic** diferansiyel sürüşlü robot modeli
- **LiDAR** sensör simülasyonu (ray-casting, Gaussian gürültü, engel kümeleme)
- **IMU** ve **Tekerlek Enkoderi** sensör simülasyonu
- **Extended Kalman Filter (EKF)** ile sensör füzyonu ve lokalizasyon
- **Dead reckoning** referans lokalizasyonu
- **Yapay Potansiyel Alan (APF)** tabanlı reaktif navigasyon

yer almaktadır.

## Senaryo

| Özellik | Değer |
|---------|-------|
| Ortam boyutu | 50 m × 50 m |
| Başlangıç noktası | (2, 2) m |
| Hedef noktası | (45, 45) m |
| Engel sayısı | 12 (dairesel) |
| Robot görevi | Teslimat — başlangıçtan hedefe ulaşma |
| Sensör gürültüsü | Gaussian (LiDAR σ=0.05 m, Enkoder σ=0.02 m/s, IMU σ=0.01 rad/s + bias) |


## Kullanılan Yöntemler

### 1. Non-holonomic Robot Modeli (Diferansiyel Sürüş)
```
x_{t+1}     = x_t + v·cos(θ_t)·dt
y_{t+1}     = y_t + v·sin(θ_t)·dt
θ_{t+1}     = θ_t + ω·dt
```

### 2. LiDAR Simülasyonu
- 360 ışın, 1° çözünürlük
- Ray-circle kesişim algoritması
- Gaussian gürültü: σ = 0.05 m
- Hareketli ortalama filtresi (pencere = 5)
- DBSCAN-lite mesafe tabanlı kümeleme

### 3. Extended Kalman Filter (EKF)
- **Predict**: Enkoder (v, ω) ile kinematik model yayılımı  
- **Update**: IMU açısal hız ölçümü ile θ düzeltmesi  
- Jacobian: `F = ∂f/∂x` (3×3 süreç Jacobianı)

### 4. Yapay Potansiyel Alan (APF)
- Çekici kuvvet: `F_att = k_att · (goal − pos)`
- İtici kuvvet: `F_rep = k_rep · (1/d − 1/d₀)/d² · (pos − obs)/‖…‖`
- Yerel minimum kaçış: stuck tespiti + 90° döndürme


## Dosya Yapısı

lidar_navigation/
├── main.py            # Simülasyon giriş noktası
├── environment.py     # 2B ortam ve engel tanımları
├── robot.py           # Diferansiyel sürüş robot modeli
├── lidar_sensor.py    # LiDAR simülasyonu
├── imu_sensor.py      # IMU simülasyonu
├── encoder_sensor.py  # Tekerlek enkoderi simülasyonu
├── ekf.py             # Extended Kalman Filter
├── navigation.py      # APF reaktif navigasyon
├── visualization.py   # Matplotlib grafik fonksiyonları
├── requirements.txt   # Python bağımlılıkları
└── README.md          # Bu dosya
```


## Kurulum

### Ön Koşullar
- Python 3.9 veya üzeri

### Adımlar

```bash
# 1. Depoyu klonla
git clone https://github.com/KULLANICI_ADI/lidar_navigation.git
cd lidar_navigation

# 2. Sanal ortam oluştur (önerilir)
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Bağımlılıkları yükle
pip install -r requirements.txt
```

---

## Çalıştırma

```bash
python main.py
```

Simülasyon tamamlandığında:
- **5 matplotlib grafik penceresi** açılır
- **Terminal'de** RMSE ve MAE değerleri yazdırılır


## Çıktılar

| Grafik | İçerik |
|--------|--------|
| Şekil 1 | 2B Ortam Haritası — engeller, başlangıç, hedef |
| Şekil 2 | Robot Yol Karşılaştırması — planlanan / gerçek / EKF / DR |
| Şekil 3 | LiDAR Görselleştirmesi — ham veri vs filtrelenmiş veri |
| Şekil 4 | Lokalizasyon — x(t), y(t), θ(t) karşılaştırması |
| Şekil 5 | Hata Analizi — pozisyon ve yönelim hataları, RMSE, MAE |


## Yapay Zeka Kullanım Beyanı

Bu projede aşağıdaki yapay zeka araçları kullanılmıştır:

| Araç | Sürüm | Kullanım Alanı |
|------|-------|---------------|
| Claude | claude-sonnet-4-6 | Kod iskeleti oluşturma, EKF matematiksel yapısı, hata ayıklama desteği, README ve rapor metin düzenlemesi |

**Katkılarım:**
- Proje senaryosunun ve sistem mimarisinin tasarlanması
- Kodların test edilmesi, çalıştırılması ve gerekli düzeltmelerin yapılması
- Sonuç grafiklerinin, hata analizinin ve değerlendirme yorumlarının hazırlanması
- Nihai raporun ve akademik atıfların düzenlenmesi

**Açıklama:** Yapay zeka araçları yardımcı araç olarak kullanılmıştır. Nihai kod, senaryo, deney sonuçları ve rapor değerlendirmeleri öğrenci tarafından kontrol edilerek teslim edilmiştir.


## Lisans

Bu proje akademik amaçlıdır.

    
