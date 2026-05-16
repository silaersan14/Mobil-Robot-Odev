# Sensör Füzyonu ve Lokalizasyon Kullanarak LiDAR Tabanlı Otonom Navigasyon

**[ÖĞRENCİ ADI SOYADI]** — **[ÖĞRENCİ NUMARASI]**  
Mobil Robotlar Dersi, [DÖNEM], [ÜNİVERSİTE ADI]  
GitHub: `https://github.com/[KULLANICI_ADI]/lidar_navigation`

---

## Yapay Zeka Kullanım Beyanı

Bu projede aşağıdaki yapay zeka araçları kullanılmıştır:

- **Kullanılan araçlar:** Claude (claude-sonnet-4-6)
- **Kullanım alanları:** EKF matematiksel yapısının iskeletinin oluşturulması, kod hata ayıklama desteği, README ve rapor metninin dil açısından düzenlenmesi.
- **Öğrencinin katkıları:** Proje senaryosunun tasarlanması; kodların test edilmesi, çalıştırılması ve düzeltilmesi; sonuç grafiklerinin, hata analizinin ve değerlendirme yorumlarının hazırlanması; tüm akademik içeriğin ve atıfların denetlenmesi.

Açıklama: Yapay zeka araçları yardımcı araç olarak kullanılmıştır. Nihai kod, senaryo, deney sonuçları ve rapor değerlendirmeleri öğrenci tarafından kontrol edilerek teslim edilmiştir.

---

## 1. Giriş ve Senaryo Tanımı

Otonom mobil robotların bilinmeyen veya yarı-bilinen ortamlarda güvenli biçimde hareket edebilmesi için kendi konumlarını doğru tahmin etmeleri ve çevredeki engelleri gerçek zamanlı olarak algılamaları gerekmektedir. Bu ihtiyaç, sensör füzyonu ve lokalizasyon tekniklerini otonom navigasyonun temel bileşeni haline getirmektedir [1].

Bu projede, Python programlama dili kullanılarak 2B bir simülasyon ortamında LiDAR tabanlı otonom navigasyon gerçekleştirilmiştir. Sistemde farklı gürültü özelliklerine sahip üç sensörden (LiDAR, IMU, tekerlek enkoderi) elde edilen veriler Extended Kalman Filter (EKF) aracılığıyla birleştirilmiş; robot, Yapay Potansiyel Alan (APF) yöntemiyle engellerden kaçınarak hedefe yönlendirilmiştir.

### 1.1 Proje Senaryosu

**Görev:** Teslimat — robotun belirtilen başlangıç noktasından hedef noktasına engellere çarpmadan ulaşması.

| Parametre | Değer |
|-----------|-------|
| Ortam | 50 m × 50 m kapalı alan |
| Başlangıç noktası | (2, 2) m |
| Hedef noktası | (45, 45) m |
| Engel sayısı | 12 adet (dairesel, r = 1.5–2.0 m) |
| Engel konumları | Bkz. Şekil 1 (ortam haritası) |
| Sensör gürültüsü | Gaussian: LiDAR σ=0.05 m; Enkoder σ_v=0.02 m/s, σ_ω=0.01 rad/s; IMU σ=0.01 rad/s + bias=0.002 rad/s |
| Simülasyon adımı | dt = 0.1 s |

Ortam haritası, başlangıç ve hedef noktaları ile engeller Şekil 1'de gösterilmiştir.

> **[Şekil 1 buraya yapıştırılacak — `python main.py` çalıştırıldıktan sonra Şekil 1 kaydedilip eklenecek]**

---

## 2. Kullanılan Yöntemler

### 2.1 Non-holonomic Robot Modeli: Diferansiyel Sürüş

Robot, yalnızca ileri-geri hareket eden ve dönmesi için iki ayrı tekerleğin hız farkından yararlanan diferansiyel sürüşlü (non-holonomic) bir modeldir. Durum vektörü **x** = [x, y, θ]ᵀ'dir. Kinematik denklemler aşağıdaki gibi ifade edilir [2]:

```
x_{t+1}     = x_t + v · cos(θ_t) · dt
y_{t+1}     = y_t + v · sin(θ_t) · dt
θ_{t+1}     = θ_t + ω · dt
```

Burada v doğrusal hız (m/s), ω açısal hız (rad/s) ve dt zaman adımıdır. Robotun giriş kısıtlaması (non-holonomic kısıt) yalnızca ileriye doğru hız komutuna izin verir; yana kayma yoktur.

### 2.2 LiDAR Simülasyonu

LiDAR sensörü 360 ışın gönderir (1° açısal çözünürlük). Her ışın için ray-circle kesişim algoritması kullanılarak engellere olan mesafe hesaplanır:

Işın: **P**(t) = (r_x + t·d_x, r_y + t·d_y), t ≥ 0  
Daire: (x − c_x)² + (y − c_y)² = R²

Kesişim mesafesi:  
```
t_c = (O_x·d_x + O_y·d_y)
d_perp² = ‖O‖² − t_c²
t_hit = t_c − √(R² − d_perp²)
```

Gerçek mesafeye Gaussian gürültü eklenerek ham LiDAR verisi elde edilir:

```
r_noisy = r_ideal + N(0, σ_lidar²)
```

Ham veri üzerinde hareketli ortalama filtresi (pencere boyutu = 5) uygulanarak filtrelenmiş veri elde edilir. LiDAR ham ve filtrelenmiş verileri Şekil 3'te gösterilmiştir.

Engel tespiti için DBSCAN-lite kümeleme algoritması kullanılmıştır: yakın mesafedeki (ε = 1.5 m) ve yeterli sayıda (min_pts = 4) komşuya sahip tarama noktaları aynı kümeye atanmaktadır.

### 2.3 Sensör Modelleri

**Tekerlek Enkoderi:**
```
v_meas     = v_true     + N(0, σ_v²)
ω_meas     = ω_true     + N(0, σ_ω²)
```

**IMU (Açısal Hız):**
```
ω_imu = ω_true + bias + N(0, σ_imu²)
```

### 2.4 Dead Reckoning

Dead reckoning, yalnızca enkoder ölçümleri kullanılarak robotun konumunun tahmin edilmesidir. Herhangi bir dış referans ya da füzyon uygulanmaz:

```
x_dr_{t+1}     = x_dr_t + v_enc · cos(θ_dr_t) · dt
y_dr_{t+1}     = y_dr_t + v_enc · sin(θ_dr_t) · dt
θ_dr_{t+1}     = θ_dr_t + ω_enc · dt
```

Enkoder gürültüsü zaman içinde birikerek (drift) konumsal hatanın büyümesine neden olur. EKF'in dead reckoning'e kıyasla üstünlüğü Bölüm 4'te hata analizi ile gösterilmiştir.

### 2.5 Extended Kalman Filter (EKF)

EKF, doğrusal olmayan sistem denklemlerini yerel linearizasyonla ele alan standart bir Bayesçi füzyon yöntemidir [1]. Durum vektörü **x** = [x, y, θ]ᵀ'dir.

#### Predict Adımı (Enkoder Girişi)

Durum tahmini:
```
x̂_{k|k-1} = f(x̂_{k-1|k-1}, u_k)
```

Kovaryans yayılımı:
```
P_{k|k-1} = F_k · P_{k-1|k-1} · F_kᵀ + Q
```

Süreç Jacobianı F = ∂f/∂**x** (enkoder (v, ω) girişiyle):
```
F = [[1,  0,  -v·sin(θ)·dt],
     [0,  1,   v·cos(θ)·dt],
     [0,  0,   1           ]]
```

Süreç gürültüsü kovaryansı:
```
Q = diag([σ_x², σ_y², σ_θ²]) = diag([0.02², 0.02², 0.015²])
```

#### Update Adımı (IMU Ölçümü)

IMU açısal hız ölçümünden θ gözlemi:
```
z_θ = θ_{k-1} + ω_imu · dt
```

Ölçüm modeli: h(**x**) = x[2] = θ  
Ölçüm Jacobianı: **H** = [0, 0, 1]

İnovasyon:
```
ỹ = angle_wrap(z_θ − θ̂_{k|k-1})
```

Kalman kazancı:
```
S   = H · P_{k|k-1} · Hᵀ + R_imu
K   = P_{k|k-1} · Hᵀ · S⁻¹
```

Durum ve kovaryans güncelleme:
```
x̂_{k|k} = x̂_{k|k-1} + K · ỹ
P_{k|k}  = (I − K · H) · P_{k|k-1}
```

IMU ölçüm gürültüsü varyansı: R_imu = 0.012² (rad²)

### 2.6 Yapay Potansiyel Alan (APF) Navigasyonu

APF yöntemi, sanal kuvvetler aracılığıyla reaktif yol planlaması gerçekleştirir [3].

**Çekici potansiyel fonksiyonu:**
```
U_att(q) = ½ · k_att · ‖q − q_goal‖²
F_att    = k_att · (q_goal − q)
```

**İtici potansiyel fonksiyonu** (d = engel yüzeyine mesafe, d₀ = etki yarıçapı):
```
U_rep(q) = ½ · k_rep · (1/d − 1/d₀)²   eğer d < d₀
F_rep    = k_rep · (1/d − 1/d₀) / d² · (q − q_obs) / ‖q − q_obs‖
```

**Toplam kuvvet:**
```
F_total = F_att + Σ F_rep_i
```

Kuvvet vektöründen hız komutları türetimi:
```
θ_desired = atan2(F_y, F_x)
θ_error   = angle_wrap(θ_desired − θ)
v         = v_max · max(0, cos(θ_error))
ω         = clip(k_ω · θ_error, ±ω_max)
```

| Parametre | Değer |
|-----------|-------|
| k_att | 1.2 |
| k_rep | 8.0 |
| d₀ | 4.0 m |
| v_max | 2.0 m/s |
| ω_max | 1.8 rad/s |

Yerel minimum durumundan kaçış için robotun belirli adım sayısı boyunca ilerleme kaydetmediği tespit edildiğinde kuvvet vektörü 90° döndürülmektedir.

---

## 3. Sonuçlar ve Grafikler

Bu bölümde `python main.py` çalıştırılarak elde edilen simülasyon sonuçları verilmiştir.

### 3.1 Ortam Haritası

> **[Şekil 1: 2B Ortam Haritası]**  
> *12 engel, başlangıç noktası (2,2) ve hedef noktası (45,45) üstten görünüş olarak gösterilmektedir.*

### 3.2 Robot Yol Planı

> **[Şekil 2: Robot Yol Karşılaştırması]**  
> *Planlanan yol (gürültüsüz APF), gerçek yol, EKF tahmini ve dead reckoning yolu aynı grafik üzerinde gösterilmektedir.*

Şekil 2 incelendiğinde EKF tahmininin gerçek yola yakın seyrettiği, dead reckoning'in ise sensör drift'i nedeniyle zamanla sapma gösterdiği görülmektedir.

### 3.3 LiDAR Sensör Görselleştirmesi

> **[Şekil 3: LiDAR Ham ve Filtrelenmiş Veri]**  
> *Sol: ham gürültülü LiDAR tarama noktaları. Sağ: hareketli ortalama filtresi uygulanmış veri. t ≈ 10 s anlık görüntüsü.*

### 3.4 Lokalizasyon Sonuçları

> **[Şekil 4: x(t), y(t), θ(t) Karşılaştırması]**  
> *Gerçek durum, EKF tahmini ve dead reckoning; zaman ekseninde x, y ve θ olarak karşılaştırılmaktadır.*

EKF'in IMU açısal hız ölçümünü füzyon yoluyla kullanması, özellikle θ bileşenindeki drift'i önemli ölçüde azaltmakta; bu da dolaylı olarak x ve y tahminlerini iyileştirmektedir.

---

## 4. Hata Analizi ve Tartışma

### 4.1 Hata Metrikleri

> **[Şekil 5: Hata Analizi — Pozisyon ve Yönelim Hatası Zaman Serisi]**

`python main.py` çalıştırıldıktan sonra terminal çıktısından elde edilen değerler:

| Metrik | EKF | Dead Reckoning |
|--------|-----|----------------|
| Pozisyon RMSE (m) | 0.2781 | 0.6606 |
| Pozisyon MAE (m) | 0.2250 | 0.5326 |
| Yönelim RMSE (rad) | 0.0096 | 0.0237 |
| Yönelim MAE (rad) | 0.0085 | 0.0222 |

### 4.2 Tartışma

Hata analizi sonuçları, EKF'in dead reckoning'e kıyasla daha düşük pozisyon ve yönelim hatası ürettiğini göstermektedir. Bunun temel nedeni, EKF'in IMU açısal hız ölçümünü Kalman güncelleme adımında kullanarak enkoder kaynaklı θ drift'ini periyodik olarak düzeltmesidir. θ hatasının azaltılması, ilerleyen adımlarda x ve y tahminlerinin de daha doğru kalmasını sağlar.

Dead reckoning'de ise enkoder gürültüsü her adımda birikerek (random walk davranışı) konum hatasının zaman içinde büyümesine yol açmaktadır. Bu durum özellikle uzun süreli navigasyon görevlerinde belirginleşir.

LiDAR tabanlı engel kümeleme, robotun çevresindeki engelleri doğru tespit etmesini sağlamış; APF navigasyonu ise robotun tüm engellerden güvenli biçimde kaçınmasına ve hedefe ulaşmasına imkân tanımıştır.

---

## 5. Kaynaklar

[1] V. Ušinskis, M. Nowicki, A. Dzedzickis ve V. Bučinskas, "Sensor-fusion based navigation for autonomous mobile robot," *Sensors*, cilt 25, sayı 4, makale 1248, 2025, doi: 10.3390/s25041248.

[2] Y. Ou, Y. Cai, Y. Sun ve T. Qin, "Autonomous navigation by mobile robot with sensor fusion based on deep reinforcement learning," *Sensors*, cilt 24, sayı 12, makale 3895, 2024, doi: 10.3390/s24123895.

[3] B. Zhang ve C. Li, "The optimization and application research of the RRT-APF-based path planning algorithm," *Electronics*, cilt 13, sayı 24, makale 4963, 2024, doi: 10.3390/electronics13244963.

---

*Bu rapor [LaTeX / Word / Google Docs] kullanılarak hazırlanmıştır.*
