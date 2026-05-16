"""
generate_report.py
Akademik proje raporunu PDF olarak olusturur.

Calistirma:
    python generate_report.py

Cikti:
    rapor.pdf  (projenin ana dizininde)
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Image, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Turkce karakter destekli fontlar (Windows sistem fontlari) ─────────────
_FONT_DIR = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("Ar",   _FONT_DIR + "arial.ttf"))
pdfmetrics.registerFont(TTFont("ArB",  _FONT_DIR + "arialbd.ttf"))
pdfmetrics.registerFont(TTFont("ArI",  _FONT_DIR + "ariali.ttf"))
pdfmetrics.registerFont(TTFont("ArBI", _FONT_DIR + "arialbi.ttf"))

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(SCRIPT_DIR, "figures")
OUTPUT_PDF  = os.path.join(SCRIPT_DIR, "rapor.pdf")

# ── Hata metrikleri (main.py ciktisi) ─────────────────────────────────────
METRICS = {
    "ekf_pos_rmse":   "0.2781",
    "ekf_pos_mae":    "0.2250",
    "dr_pos_rmse":    "0.6606",
    "dr_pos_mae":     "0.5326",
    "ekf_theta_rmse": "0.0096",
    "ekf_theta_mae":  "0.0085",
    "dr_theta_rmse":  "0.0237",
    "dr_theta_mae":   "0.0222",
}

# ══════════════════════════════════════════════════════════════════════════ #
# STILLER
# ══════════════════════════════════════════════════════════════════════════ #
C_DARK  = colors.HexColor("#1a237e")
C_MED   = colors.HexColor("#283593")
C_LIGHT = colors.HexColor("#e8eaf6")
C_BG    = colors.HexColor("#f5f5f5")

def _s(name, **kw):
    return ParagraphStyle(name, **kw)

ST = {
    "title":    _s("title",    fontName="ArB",  fontSize=17, leading=24,
                    spaceAfter=6,  alignment=1, textColor=C_DARK),
    "subtitle": _s("subtitle", fontName="Ar",   fontSize=12, leading=16,
                    spaceAfter=4,  alignment=1),
    "course":   _s("course",   fontName="ArI",  fontSize=11, leading=15,
                    spaceAfter=3,  alignment=1, textColor=colors.HexColor("#546e7a")),
    "h1":       _s("h1",       fontName="ArB",  fontSize=13, leading=18,
                    spaceBefore=16, spaceAfter=6, textColor=C_DARK),
    "h2":       _s("h2",       fontName="ArB",  fontSize=11, leading=16,
                    spaceBefore=10, spaceAfter=4, textColor=C_MED),
    "h3":       _s("h3",       fontName="ArBI", fontSize=10, leading=14,
                    spaceBefore=6,  spaceAfter=3, textColor=colors.HexColor("#37474f")),
    "body":     _s("body",     fontName="Ar",   fontSize=10, leading=15,
                    spaceAfter=6),
    "eq":       _s("eq",       fontName="Courier", fontSize=9, leading=13,
                    spaceAfter=4,  leftIndent=30, backColor=C_BG,
                    borderPadding=5),
    "caption":  _s("caption",  fontName="ArI",  fontSize=9,  leading=12,
                    spaceAfter=10, alignment=1,
                    textColor=colors.HexColor("#546e7a")),
    "ref":      _s("ref",      fontName="Ar",   fontSize=9,  leading=13,
                    spaceAfter=4,  leftIndent=18, firstLineIndent=-18),
    "ai":       _s("ai",       fontName="ArI",  fontSize=10, leading=14,
                    leftIndent=8,  rightIndent=8, spaceAfter=5,
                    backColor=colors.HexColor("#fff8e1"),
                    textColor=colors.HexColor("#4e342e"),
                    borderPadding=6),
    "bullet":   _s("bullet",   fontName="Ar",   fontSize=10, leading=15,
                    leftIndent=20, spaceAfter=3),
}


def P(text, style="body"):
    return Paragraph(text, ST[style])

def SP(n=6):
    return Spacer(1, n)

def HR():
    return HRFlowable(width="100%", thickness=0.5,
                      color=colors.HexColor("#9fa8da"), spaceAfter=6)

def fig(name, w_cm=14.5, caption=""):
    path = os.path.join(FIGURES_DIR, name)
    items = []
    if os.path.exists(path):
        from PIL import Image as PILImage
        with PILImage.open(path) as im:
            pw, ph = im.size
        aspect = ph / pw
        items.append(Image(path, width=w_cm*cm, height=w_cm*aspect*cm))
    else:
        items.append(P(f"[Sekil bulunamadi: {name}]"))
    if caption:
        items.append(P(caption, "caption"))
    return KeepTogether(items)

def tbl(data, col_widths, row_heights=None):
    t = Table(data, colWidths=[c*cm for c in col_widths],
              rowHeights=row_heights)
    header_bg  = colors.HexColor("#1a237e")
    even_bg    = colors.white
    odd_bg     = colors.HexColor("#e8eaf6")
    ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1,  0), header_bg),
        ("TEXTCOLOR",     (0, 0), (-1,  0), colors.white),
        ("FONTNAME",      (0, 0), (-1,  0), "ArB"),
        ("FONTSIZE",      (0, 0), (-1,  0), 9),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",      (0, 1), (-1, -1), "Ar"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID",          (0, 0), (-1, -1), 0.4,
         colors.HexColor("#9fa8da")),
    ])
    for i in range(1, len(data)):
        bg = even_bg if i % 2 == 0 else odd_bg
        ts.add("BACKGROUND", (0, i), (-1, i), bg)
    t.setStyle(ts)
    return t


# ══════════════════════════════════════════════════════════════════════════ #
# RAPOR ICERIGI
# ══════════════════════════════════════════════════════════════════════════ #
def build_story():
    story = []

    # ── KAPAK ──────────────────────────────────────────────────────────── #
    story += [SP(60)]
    story.append(HR())
    story.append(P("Sensör Füzyonu ve Lokalizasyon Kullanarak\n"
                   "LiDAR Tabanlı Otonom Navigasyon", "title"))
    story.append(SP(4))
    story.append(P("(2B Simülasyon)", "subtitle"))
    story.append(HR())
    story += [SP(30)]
    story.append(P("<b>Ad Soyad :</b>  [AD SOYAD]", "subtitle"))
    story.append(P("<b>Öğrenci No :</b>  [ÖĞRENCİ NUMARASI]", "subtitle"))
    story += [SP(8)]
    story.append(P("Mobil Robotlar Dersi", "course"))
    story.append(P("[ÜNİVERSİTE ADI] — [BÖLÜM ADI]", "course"))
    story.append(P("Mayıs 2026", "course"))
    story += [SP(40)]
    story.append(P(
        "GitHub: <u>https://github.com/[KULLANICI_ADI]/lidar_navigation</u>",
        "course"))
    story.append(PageBreak())

    # ── YZ BEYANI ──────────────────────────────────────────────────────── #
    story.append(P("Yapay Zeka Kullanım Beyanı", "h1"))
    story.append(HR())
    story.append(P(
        "Bu projede aşağıdaki yapay zeka araçları kullanılmıştır:", "body"))
    story.append(tbl([
        ["Araç", "Sürüm", "Kullanım Alanı"],
        ["Claude", "claude-sonnet-4-6",
         "Kod iskeleti oluşturma, EKF matematiksel yapısı,\n"
         "hata ayıklama desteği, README ve rapor\nmetin düzenlemesi"],
    ], [3.5, 3.5, 8.5]))
    story.append(SP(8))
    story.append(P("<b>Öğrencinin Katkıları:</b>", "body"))
    for item in [
        "Proje senaryosunun ve sistem mimarisinin tasarlanması",
        "Kodların test edilmesi, çalıştırılması ve düzeltilmesi",
        "Sonuç grafiklerinin ve hata analizinin hazırlanması",
        "Nihai raporun ve akademik atıfların denetlenmesi",
    ]:
        story.append(P(f"• {item}", "bullet"))
    story.append(P(
        "<i>Açıklama: Yapay zeka araçları yardımcı araç olarak kullanılmıştır. "
        "Nihai kod, senaryo, deney sonuçları ve rapor değerlendirmeleri "
        "öğrenci tarafından kontrol edilerek teslim edilmiştir.</i>", "ai"))
    story.append(SP(10))

    # ── 1. GİRİŞ ───────────────────────────────────────────────────────── #
    story.append(P("1. Giriş ve Senaryo Tanımı", "h1"))
    story.append(HR())
    story.append(P(
        "Otonom mobil robotların bilinmeyen veya yarı-bilinen ortamlarda "
        "güvenli biçimde hareket edebilmesi için kendi konumlarını doğru "
        "tahmin etmeleri ve çevredeki engelleri gerçek zamanlı olarak "
        "algılamaları gerekmektedir. Bu ihtiyaç, sensör füzyonu ve "
        "lokalizasyon tekniklerini otonom navigasyonun temel bileşeni haline "
        "getirmektedir [1].", "body"))
    story.append(P(
        "Bu projede Python kullanılarak 2B bir simülasyon ortamında LiDAR "
        "tabanlı otonom navigasyon gerçekleştirilmiştir. Sistemde farklı "
        "gürültü özelliklerine sahip üç sensörden — LiDAR, IMU ve tekerlek "
        "enkoderi — elde edilen veriler Extended Kalman Filter (EKF) "
        "aracılığıyla birleştirilmiş; robot Yapay Potansiyel Alan (APF) "
        "yöntemiyle engellerden kaçınarak hedefe yönlendirilmiştir [2].",
        "body"))

    story.append(P("1.1 Proje Senaryosu", "h2"))
    story.append(P(
        "<b>Görev:</b> Teslimat — robotun (2, 2) başlangıç noktasından "
        "(45, 45) hedef noktasına, 12 engel içeren 50 m × 50 m'lik "
        "bir alanda engellere çarpmadan ulaşması.", "body"))
    story.append(tbl([
        ["Parametre", "Değer"],
        ["Ortam boyutu", "50 m × 50 m"],
        ["Başlangıç noktası", "(2, 2) m"],
        ["Hedef noktası", "(45, 45) m"],
        ["Engel sayısı", "12 adet (dairesel, r = 1.5–2.0 m)"],
        ["LiDAR gürültüsü", "Gaussian  σ = 0.05 m"],
        ["Enkoder gürültüsü", "σ_v = 0.02 m/s,  σ_ω = 0.01 rad/s"],
        ["IMU gürültüsü", "σ = 0.01 rad/s,  bias = 0.002 rad/s"],
        ["Simülasyon adımı", "dt = 0.1 s"],
        ["Hedefe ulaşma adımı", "Adım 327  (t = 32.7 s)"],
    ], [7, 8.5]))
    story.append(SP(6))
    story.append(fig("fig1_ortam_haritasi.png", 12.0,
                     "Şekil 1. 2B Ortam Haritası: 12 dairesel engel, "
                     "başlangıç noktası (yeşil yıldız) ve hedef noktası (kırmızı yıldız)."))
    story.append(PageBreak())

    # ── 2. YÖNTEMLER ───────────────────────────────────────────────────── #
    story.append(P("2. Kullanılan Yöntemler", "h1"))
    story.append(HR())

    # 2.1 Robot modeli
    story.append(P("2.1 Non-holonomic Robot Modeli: Diferansiyel Sürüş", "h2"))
    story.append(P(
        "Robot, iki bağımsız tahrikli tekerlekten oluşan ve yalnızca ileri "
        "doğru hız üretebilen diferansiyel sürüşlü (non-holonomic) bir "
        "modeldir [2]. Durum vektörü <b>x</b> = [x, y, θ]<super>T</super>'dir. "
        "Kinematik denklemler:", "body"))
    for eq in [
        "x_{t+1}  =  x_t  +  v · cos(θ_t) · dt",
        "y_{t+1}  =  y_t  +  v · sin(θ_t) · dt",
        "θ_{t+1}  =  θ_t  +  ω · dt",
    ]:
        story.append(P(eq, "eq"))
    story.append(P(
        "Burada v doğrusal hız (m/s), ω açısal hız (rad/s) ve dt zaman "
        "adımıdır. Non-holonomic kısıt, robota yalnızca kendi yönünde "
        "hareket imkânı tanır; yanal kayma yoktur.", "body"))

    # 2.2 LiDAR
    story.append(P("2.2 LiDAR Simülasyonu", "h2"))
    story.append(P(
        "LiDAR sensörü 360 ışın gönderir (1° açısal çözünürlük). Her ışın "
        "için ışın-daire kesişim (ray-circle intersection) algoritması "
        "kullanılarak engellere olan ideal mesafe hesaplanır:", "body"))
    for eq in [
        "t_c  =  O_x·d_x  +  O_y·d_y          (obs merkezinin ışına izdüşümü)",
        "d_perp²  =  ||O||²  -  t_c²",
        "t_hit  =  t_c  -  sqrt(R²  -  d_perp²)   (kesişim mesafesi)",
    ]:
        story.append(P(eq, "eq"))
    story.append(P(
        "İdeal mesafeye Gaussian gürültü eklenerek ham LiDAR verisi elde "
        "edilir: r_noisy = r_ideal + N(0, σ²). Ham veriye 5 noktalı "
        "hareketli ortalama filtresi uygulanarak filtrelenmiş veri elde edilir. "
        "Engel kümeleme için DBSCAN-lite algoritması kullanılmıştır "
        "(ε = 1.5 m, min_pts = 4).", "body"))
    story.append(fig("fig3_lidar.png", 15.5,
                     "Şekil 3. LiDAR Sensör Görselleştirmesi (t ≈ 10 s). "
                     "Sol: gürültülü ham veri. Sağ: hareketli ortalama filtresi "
                     "uygulanmış filtrelenmiş veri."))

    # 2.3 Sensör modelleri
    story.append(P("2.3 Sensör Modelleri", "h2"))
    story.append(P("<b>Tekerlek Enkoderi:</b>", "body"))
    for eq in [
        "v_meas   =  v_true   +  N(0, σ_v²)",
        "ω_meas   =  ω_true   +  N(0, σ_ω²)",
    ]:
        story.append(P(eq, "eq"))
    story.append(P("<b>IMU (Açısal Hız):</b>", "body"))
    story.append(P("ω_imu  =  ω_true  +  bias  +  N(0, σ_imu²)", "eq"))

    # 2.4 Dead reckoning
    story.append(P("2.4 Dead Reckoning", "h2"))
    story.append(P(
        "Dead reckoning, herhangi bir dış referans ya da füzyon "
        "uygulanmaksızın yalnızca enkoder ölçümleri entegre edilerek "
        "konumun tahmin edilmesidir:", "body"))
    for eq in [
        "x_dr_{t+1}  =  x_dr_t  +  v_enc · cos(θ_dr_t) · dt",
        "y_dr_{t+1}  =  y_dr_t  +  v_enc · sin(θ_dr_t) · dt",
        "θ_dr_{t+1}  =  θ_dr_t  +  ω_enc · dt",
    ]:
        story.append(P(eq, "eq"))
    story.append(P(
        "Enkoder gürültüsü zaman içinde birikerek (drift) konumsal hatanın "
        "büyümesine neden olur. Bu etki Bölüm 4'teki hata analizinde "
        "açıkça görülmektedir.", "body"))
    story.append(PageBreak())

    # 2.5 EKF
    story.append(P("2.5 Extended Kalman Filter (EKF)", "h2"))
    story.append(P(
        "EKF, doğrusal olmayan sistem denklemlerini yerel linearizasyonla "
        "ele alan Bayesçi bir sensör füzyon yöntemidir [1]. Durum vektörü "
        "<b>x</b> = [x, y, θ]<super>T</super>, kovaryans matrisi "
        "<b>P</b> ∈ ℝ<super>3×3</super>'tür.", "body"))

    story.append(P("Predict Adımı (Enkoder Girişi):", "h3"))
    for eq in [
        "x̂_{k|k-1}  =  f(x̂_{k-1|k-1}, u_k)",
        "P_{k|k-1}  =  F_k · P_{k-1|k-1} · F_k^T  +  Q",
    ]:
        story.append(P(eq, "eq"))
    story.append(P("Süreç Jacobianı F = ∂f/∂x:", "body"))
    story.append(P(
        "F  =  [[1,  0,  -v·sin(θ)·dt],\n"
        "       [0,  1,   v·cos(θ)·dt],\n"
        "       [0,  0,   1          ]]", "eq"))
    story.append(P(
        "Süreç gürültüsü: Q = diag([0.02², 0.02², 0.015²])", "eq"))

    story.append(P("Update Adımı (IMU Ölçümü):", "h3"))
    story.append(P(
        "IMU açısal hız ölçümünden θ gözlemi türetilir ve EKF güncelleme "
        "adımında kullanılır:", "body"))
    for eq in [
        "z_θ  =  θ_{k-1}  +  ω_imu · dt        (IMU'dan θ tahmini)",
        "H    =  [0,  0,  1]                    (ölçüm Jacobianı)",
        "ỹ    =  angle_wrap(z_θ − θ̂_{k|k-1})   (inovasyon)",
        "S    =  H · P_{k|k-1} · H^T  +  R_imu",
        "K    =  P_{k|k-1} · H^T · S^{-1}      (Kalman kazancı)",
        "x̂_{k|k}  =  x̂_{k|k-1}  +  K · ỹ",
        "P_{k|k}   =  (I − K·H) · P_{k|k-1}",
    ]:
        story.append(P(eq, "eq"))
    story.append(P(
        "IMU ölçüm gürültüsü: R_imu = 0.012² (rad²). Kalman kazancı K, "
        "enkoder ve IMU ölçümlerinin göreli güvenilirliğine göre ağırlık "
        "dağılımını otomatik olarak belirler.", "body"))

    # 2.6 APF
    story.append(P("2.6 Yapay Potansiyel Alan (APF) Navigasyonu", "h2"))
    story.append(P(
        "APF yöntemi, sanal kuvvetler aracılığıyla reaktif yol planlaması "
        "gerçekleştirir [3]. Çekici kuvvet robotu hedefe yönlendirirken "
        "itici kuvvetler engellerden uzaklaştırır:", "body"))
    for eq in [
        "F_att  =  k_att · (q_goal − q)                              (çekici kuvvet)",
        "F_rep  =  k_rep · (1/d − 1/d₀) / d² · (q−q_obs)/||q−q_obs||   (itici kuvvet, d < d₀)",
        "F_toplam  =  F_att  +  Σ F_rep_i",
    ]:
        story.append(P(eq, "eq"))
    story.append(P("Kuvvet vektöründen hız komutları:", "body"))
    for eq in [
        "θ_desired  =  atan2(F_y, F_x)",
        "v          =  v_max · max(0, cos(θ_desired − θ))",
        "ω          =  clip(k_ω · (θ_desired − θ),  ±ω_max)",
    ]:
        story.append(P(eq, "eq"))
    story.append(tbl([
        ["Parametre", "Değer", "Açıklama"],
        ["k_att", "1.2", "Çekici alan katsayısı"],
        ["k_rep", "8.0", "İtici alan katsayısı"],
        ["d₀", "4.0 m", "İtici alanın etkili mesafesi"],
        ["v_max", "2.0 m/s", "Maksimum doğrusal hız"],
        ["ω_max", "1.8 rad/s", "Maksimum açısal hız"],
        ["k_ω", "3.0", "Açısal hız kontrolcü kazancı"],
    ], [4, 3, 8.5]))
    story.append(SP(6))
    story.append(P(
        "Yerel minimum tuzaklarından kaçış için robotun belirli adım "
        "sayısı boyunca ilerleme kaydetmediği tespit edildiğinde kuvvet "
        "vektörü 90° döndürülmektedir.", "body"))
    story.append(PageBreak())

    # ── 3. SONUÇLAR ────────────────────────────────────────────────────── #
    story.append(P("3. Sonuçlar ve Grafikler", "h1"))
    story.append(HR())
    story.append(P(
        "Simülasyon 3.000 adım sınırı içinde tamamlanmıştır. Robot, "
        "<b>327. adımda (t = 32.7 s)</b> hedef noktasına (45, 45) 1.5 m "
        "yakınlık eşiği içinde ulaşmıştır.", "body"))

    story.append(P("3.1 Robot Yol Planı", "h2"))
    story.append(P(
        "Şekil 2'de gürültüsüz APF ile hesaplanan planlanan yol, "
        "gerçek robot yolu, EKF tahmini ve dead reckoning yolu "
        "karşılaştırmalı olarak gösterilmiştir.", "body"))
    story.append(fig("fig2_yol_karsilastirma.png", 13.0,
                     "Şekil 2. Robot Yol Karşılaştırması: Planlanan yol (yeşil kesik-nokta), "
                     "gerçek yol (mavi), EKF tahmini (turuncu kesik) ve "
                     "Dead Reckoning (kırmızı noktalı)."))

    story.append(P("3.2 Lokalizasyon Sonuçları", "h2"))
    story.append(P(
        "Şekil 4'te x(t), y(t) ve θ(t) bileşenleri zaman ekseninde "
        "karşılaştırmalı olarak verilmiştir. EKF tahmini gerçek yola "
        "belirgin biçimde daha yakın seyretmekte, dead reckoning ise "
        "özellikle θ bileşeninde drift göstermektedir.", "body"))
    story.append(fig("fig4_lokalizasyon.png", 15.5,
                     "Şekil 4. Lokalizasyon Sonuçları: x(t), y(t), θ(t) "
                     "karşılaştırması — Gerçek durum (mavi), EKF (turuncu kesik), "
                     "Dead Reckoning (kırmızı noktalı)."))
    story.append(PageBreak())

    # ── 4. HATA ANALİZİ ────────────────────────────────────────────────── #
    story.append(P("4. Hata Analizi ve Tartışma", "h1"))
    story.append(HR())
    story.append(fig("fig5_hata_analizi.png", 15.5,
                     "Şekil 5. Hata Analizi: Zaman boyunca pozisyon hatası (üst) "
                     "ve yönelim hatası (alt) — EKF vs Dead Reckoning. "
                     "RMSE ve MAE değerleri grafik başlığında gösterilmiştir."))
    story.append(SP(6))

    story.append(P("4.1 Hata Metrikleri", "h2"))
    m = METRICS
    story.append(tbl([
        ["Metrik", "EKF", "Dead Reckoning", "İyileşme"],
        ["Pozisyon RMSE (m)", m["ekf_pos_rmse"], m["dr_pos_rmse"],
         f"×{float(m['dr_pos_rmse'])/float(m['ekf_pos_rmse']):.1f}"],
        ["Pozisyon MAE (m)", m["ekf_pos_mae"], m["dr_pos_mae"],
         f"×{float(m['dr_pos_mae'])/float(m['ekf_pos_mae']):.1f}"],
        ["Yönelim RMSE (rad)", m["ekf_theta_rmse"], m["dr_theta_rmse"],
         f"×{float(m['dr_theta_rmse'])/float(m['ekf_theta_rmse']):.1f}"],
        ["Yönelim MAE (rad)", m["ekf_theta_mae"], m["dr_theta_mae"],
         f"×{float(m['dr_theta_mae'])/float(m['ekf_theta_mae']):.1f}"],
    ], [5.5, 3.5, 4.0, 2.5]))

    story.append(P("4.2 Tartışma", "h2"))
    story.append(P(
        "Hata analizi sonuçları, EKF'in dead reckoning'e kıyasla "
        "belirgin biçimde daha düşük pozisyon ve yönelim hatası "
        "ürettiğini doğrulamaktadır. Pozisyon RMSE'de "
        f"×{float(m['dr_pos_rmse'])/float(m['ekf_pos_rmse']):.1f}, "
        f"yönelim RMSE'de ×{float(m['dr_theta_rmse'])/float(m['ekf_theta_rmse']):.1f} "
        "oranında iyileşme elde edilmiştir.", "body"))
    story.append(P(
        "Bu farkın temel nedeni, EKF'in IMU açısal hız ölçümünü Kalman "
        "güncelleme adımında kullanarak enkoder kaynaklı θ drift'ini "
        "periyodik olarak düzeltmesidir. θ hatasının baskılanması, "
        "ilerleyen adımlarda x ve y tahminlerinin de daha doğru kalmasını "
        "sağlar — pozisyon hatası ise x ve y hatalarının bileşkesidir.", "body"))
    story.append(P(
        "Dead reckoning'de enkoder gürültüsü her adımda birikerek "
        "rastgele yürüyüş (random walk) davranışı sergiler; bu durum "
        "özellikle uzun süreli navigasyon görevlerinde belirginleşir "
        "(Şekil 5 üst grafik). APF navigasyonu ise tüm engellerden "
        "güvenli biçimde kaçınarak robotu hedefe ulaştırmıştır.", "body"))
    story.append(PageBreak())

    # ── 5. KAYNAKLAR ───────────────────────────────────────────────────── #
    story.append(P("5. Kaynaklar", "h1"))
    story.append(HR())
    for ref in [
        "[1] V. Ušinskis, M. Nowicki, A. Dzedzickis ve V. Bučinskas, "
        "\"Sensor-fusion based navigation for autonomous mobile robot,\" "
        "<i>Sensors</i>, cilt 25, sayı 4, makale 1248, 2025, "
        "doi: 10.3390/s25041248.",
        "[2] Y. Ou, Y. Cai, Y. Sun ve T. Qin, "
        "\"Autonomous navigation by mobile robot with sensor fusion based on "
        "deep reinforcement learning,\" <i>Sensors</i>, cilt 24, sayı 12, "
        "makale 3895, 2024, doi: 10.3390/s24123895.",
        "[3] B. Zhang ve C. Li, "
        "\"The optimization and application research of the RRT-APF-based "
        "path planning algorithm,\" <i>Electronics</i>, cilt 13, sayı 24, "
        "makale 4963, 2024, doi: 10.3390/electronics13244963.",
    ]:
        story.append(P(ref, "ref"))
        story.append(SP(4))

    return story


# ══════════════════════════════════════════════════════════════════════════ #
# SAYFA DÜZENI
# ══════════════════════════════════════════════════════════════════════════ #
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Ar", 8)
    canvas.setFillColor(colors.HexColor("#78909c"))
    # Alt orta — sayfa numarası
    canvas.drawCentredString(A4[0] / 2, 1.2*cm,
                             f"— {doc.page} —")
    # Alt sag — baslik
    canvas.drawRightString(A4[0] - 1.8*cm, 1.2*cm,
                           "LiDAR Tabanlı Otonom Navigasyon")
    canvas.restoreState()


def generate():
    try:
        from PIL import Image  # noqa: F401 — PIL varsa yüksek kalite
    except ImportError:
        pass  # PIL yoksa da calışır

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.5*cm,  bottomMargin=2.5*cm,
    )
    story = build_story()
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"[OK] PDF olusturuldu: {OUTPUT_PDF}")


if __name__ == "__main__":
    generate()
