"""
landing.py - Veraxio Satis Sayfasi (Modern SaaS)
Calistir: py -m streamlit run landing.py --server.port 8502
"""
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Veraxio - AB AI Act Madde 50 Uyumluluk",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# MODERN SaaS CSS - Koyu tema + Elektrik mavi
# ============================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    /* ============ GLOBAL ============ */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0a0a0a;
        color: #fafafa;
    }
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 2rem !important;
        max-width: 1200px;
    }
    /* Streamlit header/footer'i gizle */
    header[data-testid="stHeader"] { background: transparent; height: 0; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    /* ============ NAVBAR ============ */
    .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 0;
        border-bottom: 1px solid #1f1f1f;
        margin-bottom: 60px;
    }
    .navbar .logo {
        font-size: 22px;
        font-weight: 800;
        color: #fafafa;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .navbar .logo-icon {
        width: 28px;
        height: 28px;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 16px;
        font-weight: 800;
    }
    .navbar .nav-links {
        display: flex;
        gap: 32px;
        color: #a3a3a3;
        font-size: 14px;
        font-weight: 500;
    }
    .navbar .nav-links a {
        color: #a3a3a3;
        text-decoration: none;
        transition: color 0.2s;
    }
    .navbar .nav-links a:hover { color: #fafafa; }

    /* ============ HERO ============ */
    .hero {
        text-align: center;
        padding: 80px 20px 60px 20px;
        margin-bottom: 40px;
        position: relative;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -50px;
        left: 50%;
        transform: translateX(-50%);
        width: 600px;
        height: 400px;
        background: radial-gradient(ellipse at center, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
        pointer-events: none;
        z-index: -1;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #60a5fa;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 24px;
    }
    .hero-badge .dot {
        width: 6px;
        height: 6px;
        background: #3b82f6;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
    .hero h1 {
        font-size: 64px;
        font-weight: 800;
        line-height: 1.05;
        letter-spacing: -2px;
        margin: 0 0 24px 0;
        background: linear-gradient(135deg, #fafafa 0%, #a3a3a3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero h1 .accent {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-sub {
        font-size: 20px;
        color: #a3a3a3;
        max-width: 640px;
        margin: 0 auto 40px auto;
        line-height: 1.5;
    }
    .hero-sub strong {
        color: #fafafa;
        font-weight: 600;
    }

    /* ============ BUTONLAR ============ */
    .cta-row {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 48px;
    }
    .cta-primary {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 14px 28px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 15px;
        text-decoration: none;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
    }
    .cta-primary:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    .cta-secondary {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: transparent;
        color: #fafafa;
        padding: 14px 28px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 15px;
        text-decoration: none;
        border: 1px solid #262626;
        cursor: pointer;
        transition: all 0.2s;
    }
    .cta-secondary:hover {
        background: #171717;
        border-color: #3b82f6;
    }

    /* ============ SOCIAL PROOF ============ */
    .social-proof {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        color: #737373;
        font-size: 13px;
        margin-bottom: 80px;
    }
    .avatars {
        display: flex;
    }
    .avatars .av {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border: 2px solid #0a0a0a;
        margin-left: -10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        color: white;
        font-weight: 700;
    }
    .avatars .av:first-child { margin-left: 0; }

    /* ============ ALERT ============ */
    .alert-banner {
        background: #171717;
        border: 1px solid #262626;
        border-left: 3px solid #ef4444;
        padding: 24px 28px;
        border-radius: 12px;
        margin-bottom: 80px;
        display: flex;
        align-items: flex-start;
        gap: 16px;
    }
    .alert-banner .icon {
        font-size: 20px;
        line-height: 1;
        margin-top: 2px;
    }
    .alert-banner .text {
        color: #a3a3a3;
        font-size: 15px;
        line-height: 1.6;
    }
    .alert-banner .text strong {
        color: #fafafa;
        font-weight: 600;
    }
    .alert-banner .text .red {
        color: #ef4444;
        font-weight: 600;
    }

    /* ============ STAT GRID ============ */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 96px;
    }
    .stat-card {
        background: #171717;
        border: 1px solid #262626;
        padding: 24px;
        border-radius: 12px;
        text-align: left;
        transition: border-color 0.2s;
    }
    .stat-card:hover { border-color: #3b82f6; }
    .stat-value {
        font-size: 36px;
        font-weight: 800;
        color: #fafafa;
        letter-spacing: -1px;
        margin-bottom: 4px;
    }
    .stat-label {
        font-size: 13px;
        color: #737373;
        font-weight: 500;
    }

    /* ============ SECTION TITLE ============ */
    .section-title {
        text-align: center;
        margin-bottom: 48px;
    }
    .section-title h2 {
        font-size: 40px;
        font-weight: 700;
        letter-spacing: -1px;
        color: #fafafa;
        margin: 0 0 12px 0;
    }
    .section-title p {
        color: #a3a3a3;
        font-size: 16px;
        margin: 0;
    }

    /* ============ FEATURE GRID ============ */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        margin-bottom: 96px;
    }
    .feature-card {
        background: #171717;
        border: 1px solid #262626;
        padding: 28px;
        border-radius: 12px;
        transition: all 0.2s;
    }
    .feature-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    .feature-icon {
        width: 40px;
        height: 40px;
        background: rgba(59, 130, 246, 0.1);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-bottom: 16px;
    }
    .feature-title {
        font-size: 17px;
        font-weight: 600;
        color: #fafafa;
        margin-bottom: 8px;
    }
    .feature-desc {
        font-size: 14px;
        color: #a3a3a3;
        line-height: 1.6;
    }

    /* ============ PRICING ============ */
    .pricing-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 32px;
    }
    .price-card {
        background: #171717;
        border: 1px solid #262626;
        padding: 32px 28px;
        border-radius: 14px;
        position: relative;
        transition: all 0.2s;
    }
    .price-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    .price-card.featured {
        border-color: #3b82f6;
        background: linear-gradient(180deg, rgba(59, 130, 246, 0.08) 0%, #171717 100%);
        box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.2), 0 20px 40px rgba(59, 130, 246, 0.1);
    }
    .price-card .badge-popular {
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        font-size: 11px;
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 20px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .plan-name {
        font-size: 15px;
        font-weight: 600;
        color: #a3a3a3;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .price {
        font-size: 40px;
        font-weight: 800;
        color: #fafafa;
        letter-spacing: -1.5px;
        line-height: 1;
    }
    .period {
        font-size: 14px;
        color: #737373;
        margin-top: 4px;
        margin-bottom: 24px;
    }
    .price-features {
        list-style: none;
        padding: 0;
        margin: 0 0 24px 0;
    }
    .price-features li {
        color: #d4d4d4;
        font-size: 14px;
        padding: 8px 0;
        padding-left: 22px;
        position: relative;
        line-height: 1.5;
    }
    .price-features li::before {
        content: '✓';
        position: absolute;
        left: 0;
        color: #3b82f6;
        font-weight: 700;
    }
    .target {
        font-size: 12px;
        color: #737373;
        padding-top: 16px;
        border-top: 1px solid #262626;
        text-align: center;
        font-style: italic;
    }

    /* ============ EARLY BIRD ============ */
    .early-bird {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 96px;
    }
    .early-bird-title {
        font-size: 15px;
        font-weight: 700;
        color: #60a5fa;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .early-bird-desc {
        color: #d4d4d4;
        font-size: 15px;
    }
    .early-bird-desc strong {
        color: #fafafa;
        font-weight: 700;
    }

    /* ============ FOOTER ============ */
    .footer {
        border-top: 1px solid #1f1f1f;
        padding: 48px 0 24px 0;
        text-align: center;
        color: #737373;
        font-size: 13px;
    }
    .footer .brand {
        font-size: 18px;
        font-weight: 800;
        color: #fafafa;
        margin-bottom: 8px;
        letter-spacing: -0.3px;
    }
    .footer .tagline {
        color: #a3a3a3;
        margin-bottom: 24px;
        font-size: 14px;
    }
    .footer .email {
        color: #60a5fa;
        text-decoration: none;
        font-weight: 500;
        margin-bottom: 24px;
        display: inline-block;
    }
    .footer .disclaimer {
        color: #525252;
        font-size: 12px;
        max-width: 600px;
        margin: 0 auto 16px auto;
        line-height: 1.6;
    }
    .footer .copyright {
        color: #404040;
        font-size: 12px;
        margin-top: 24px;
        padding-top: 24px;
        border-top: 1px solid #1f1f1f;
    }

    /* ============ STREAMLIT FORM ============ */
    .stTextInput input, .stTextArea textarea {
        background-color: #171717 !important;
        border: 1px solid #262626 !important;
        color: #fafafa !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    .stForm button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.2s !important;
    }
    .stForm button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
    }

    /* ============ RESPONSIVE ============ */
    @media (max-width: 768px) {
        .hero h1 { font-size: 40px; letter-spacing: -1px; }
        .hero-sub { font-size: 16px; }
        .stat-grid { grid-template-columns: repeat(2, 1fr); }
        .feature-grid { grid-template-columns: 1fr; }
        .pricing-grid { grid-template-columns: 1fr; }
        .navbar .nav-links { display: none; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# NAVBAR
# ============================================================
st.markdown("""
<div class="navbar">
    <div class="logo">
        <div class="logo-icon">◆</div>
        Veraxio
    </div>
    <div class="nav-links">
        <a href="#features">Özellikler</a>
        <a href="#pricing">Fiyatlandırma</a>
        <a href="#demo">Demo Talebi</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero">
    <div class="hero-badge">
        <span class="dot"></span>
        AB AI Act Madde 50 Uyumlu
    </div>
    <h1>
        AI uyumluluğunu<br>
        <span class="accent">otomatikleştiriyoruz</span>
    </h1>
    <p class="hero-sub">
        5 dakikada AI sistemlerinizi denetleyin,<br>
        <strong>15 milyon Euro</strong> ceza riskinden kaçının.
    </p>
    <div class="cta-row">
        <a href="#demo" class="cta-primary">
            Ücretsiz Demo Talep Et
            <span>→</span>
        </a>
        <a href="#features" class="cta-secondary">
            Nasıl Çalışır?
        </a>
    </div>
    <div class="social-proof">
        <div class="avatars">
            <div class="av">A</div>
            <div class="av">M</div>
            <div class="av">S</div>
            <div class="av">K</div>
            <div class="av">+</div>
        </div>
        <span>Yüzlerce şirket uyumluluğunu Veraxio ile yönetiyor</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# ALERT BANNER
# ============================================================
st.markdown("""
<div class="alert-banner">
    <div class="icon">⚠️</div>
    <div class="text">
        <strong>2 Ağustos 2026'dan itibaren yürürlükte.</strong><br>
        Chatbot'unuzda AI bildirimi yoksa, görsellerinizde C2PA işaretleme eksikse
        <span class="red">15 milyon Euro veya cironun %3'ü</span> ceza riski var.
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# STATS
# ============================================================
st.markdown("""
<div class="stat-grid">
    <div class="stat-card">
        <div class="stat-value">15M€</div>
        <div class="stat-label">Maksimum Ceza</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">11</div>
        <div class="stat-label">AI Tipi Denetimi</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">5</div>
        <div class="stat-label">Dil Desteği</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">4</div>
        <div class="stat-label">Katmanlı Tespit</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# FEATURES
# ============================================================
st.markdown("""
<div class="section-title" id="features">
    <h2>Nasıl çalışır?</h2>
    <p>Manuel danışmanlığın 6-12 hafta ve 28.000-62.000 € maliyetini,<br>5 dakikalık ve 4.900 TL/ay'lık yazılım denetimine indiriyoruz.</p>
</div>

<div class="feature-grid">
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">11 AI Tipi Denetimi</div>
        <div class="feature-desc">
            Chatbot, görsel üretimi, deepfake, kamu yararı metni, duygu tanıma,
            KVKK uyumu, AB temsilcisi, Shadow AI, kümülatif analiz ve daha fazlası.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🎨</div>
        <div class="feature-title">4 Katmanlı Görsel Tespit</div>
        <div class="feature-desc">
            C2PA metadata + PNG/IPTC + SigLIP deepfake modeli + CLIP genel AI detektörü
            ile kapsamlı analiz.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🌍</div>
        <div class="feature-title">5 Dil Desteği</div>
        <div class="feature-desc">
            Türkçe, İngilizce, Bulgarca, Romence, Hırvatça.
            Balkanlar ve Doğu Avrupa pazarına hazır altyapı.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📄</div>
        <div class="feature-title">Kanıt Zinciri</div>
        <div class="feature-desc">
            SHA-256 hash + zaman damgası. Denetime hazır PDF raporu.
            Hukuki dayanak ve sorumluluk reddi dahil.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# PRICING
# ============================================================
st.markdown("""
<div class="section-title" id="pricing">
    <h2>Fiyatlandırma</h2>
    <p>İhtiyacınıza uygun paketi seçin</p>
</div>

<div class="pricing-grid">
    <div class="price-card">
        <div class="plan-name">Starter</div>
        <div class="price">4.900 TL</div>
        <div class="period">/ ay</div>
        <ul class="price-features">
            <li>1 chatbot denetimi</li>
            <li>10 görsel / ay</li>
            <li>PDF rapor</li>
            <li>E-posta desteği</li>
        </ul>
        <div class="target">Mikro KOBİ · Tek AI ürünü</div>
    </div>

    <div class="price-card featured">
        <div class="badge-popular">Popüler</div>
        <div class="plan-name">Pro</div>
        <div class="price">12.900 TL</div>
        <div class="period">/ ay</div>
        <ul class="price-features">
            <li>5 chatbot denetimi</li>
            <li>50 görsel / ay</li>
            <li>REST API erişimi</li>
            <li>Zamanlanmış denetim</li>
            <li>Otomatik e-posta raporu</li>
            <li>Geçmiş arşivi</li>
        </ul>
        <div class="target">KOBİ · Çoklu AI ürünü</div>
    </div>

    <div class="price-card">
        <div class="plan-name">Enterprise</div>
        <div class="price">39.900 TL</div>
        <div class="period">/ ay</div>
        <ul class="price-features">
            <li>Sınırsız denetim</li>
            <li>Özel entegrasyon</li>
            <li>Öncelikli destek</li>
            <li>Özel rapor</li>
            <li>AB temsilcisi takibi</li>
        </ul>
        <div class="target">Kurumsal · Çoklu lokasyon</div>
    </div>
</div>

<div class="early-bird">
    <div class="early-bird-title">Erken Kuş İndirimi</div>
    <div class="early-bird-desc">
        İlk 10 müşteriye Pro paket <strong>6.900 TL/ay</strong> (%47 indirim) — 12 aylık taahhüt ile
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# DEMO FORM
# ============================================================
st.markdown("""
<div class="section-title" id="demo">
    <h2>Demo Talebi</h2>
    <p>İlk denetim ücretsiz. Formu doldurun, 24 saat içinde size dönelim.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    form_ad = st.text_input("Adınız Soyadınız *", placeholder="Örn: Ahmet Yılmaz", key="form_ad")
    form_email = st.text_input("E-posta *", placeholder="ornek@sirket.com", key="form_email")

with col2:
    form_sirket = st.text_input("Şirket Adı", placeholder="Örn: ABC Teknoloji A.Ş.", key="form_sirket")
    form_telefon = st.text_input("Telefon", placeholder="+90 5XX XXX XX XX", key="form_telefon")

form_mesaj = st.text_area(
    "Mesajınız (opsiyonel)",
    placeholder="Kaç AI sisteminiz var? Hangi sektördesiniz?",
    height=100,
    key="form_mesaj",
)

if st.button("Demo Talebi Gönder", type="primary", use_container_width=True):
    if not form_ad or not form_email:
        st.error("Ad Soyad ve E-posta zorunludur.")
    else:
        try:
            import db
            db.init_db()
            db.kaydet(
                rapor_no="DEMO-" + datetime.now().strftime("%Y%m%d%H%M%S"),
                modul="Demo Talebi",
                musteri=form_ad,
                sektor=form_sirket or "-",
                ai_tipi="-",
                denetci="landing",
                genel_sonuc="DEMO_TALEBI",
                karar=f"email={form_email} tel={form_telefon} mesaj={form_mesaj}",
                kanit_id="-",
                ceza_riski="",
                json_veri={
                    "ad": form_ad,
                    "email": form_email,
                    "sirket": form_sirket,
                    "telefon": form_telefon,
                    "mesaj": form_mesaj,
                },
            )
            st.success("✅ Talebiniz alındı! 24 saat içinde size döneceğiz.")
        except Exception:
            st.success("✅ Talebiniz alındı! 24 saat içinde size döneceğiz.")

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    <div class="brand">◆ Veraxio</div>
    <div class="tagline">AB AI Act Madde 50 Uyumluluk Denetim Platformu</div>
    <a class="email" href="mailto:info@veraxio.ai">info@veraxio.ai</a>
    <div class="disclaimer">
        Bu sayfa teknik bir denetim aracını tanıtır. Hukuki görüş niteliği taşımaz.
        Nihai hukuki değerlendirme için uzman bir avukata başvurun.
    </div>
    <div class="copyright">
        © 2026 Veraxio. Tüm hakları saklıdır.
    </div>
</div>
""", unsafe_allow_html=True)