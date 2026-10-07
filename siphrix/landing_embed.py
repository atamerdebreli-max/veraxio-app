"""
landing_embed.py - Veraxio Landing Sayfasi (Streamlit icine gomulu)
Logo + Hero + Fiyatlar + Ucretsiz Demo + Dil Secenegi
"""
import streamlit as st


def _dil_secici_landing():
    """Landing sayfasi icin basit dil secici."""
    col1, col2 = st.columns([6, 1])
    with col2:
        dil = st.selectbox(
            "🌐",
            ["TR", "EN", "BG", "RO", "HR"],
            index=0,
            key="landing_dil",
            label_visibility="collapsed",
        )
        if dil == "TR":
            st.session_state["dil"] = "tr"
        elif dil == "EN":
            st.session_state["dil"] = "en"
        elif dil == "BG":
            st.session_state["dil"] = "bg"
        elif dil == "RO":
            st.session_state["dil"] = "ro"
        elif dil == "HR":
            st.session_state["dil"] = "hr"


def goster():
    """Landing sayfasini gosterir."""

    # ============================================================
    # CSS
    # ============================================================
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            background-color: #0a0a0a;
            color: #fafafa;
        }
        .block-container { padding-top: 1rem !important; max-width: 1200px; }
        header[data-testid="stHeader"] { background: transparent; }
        footer { visibility: hidden; }
        #MainMenu { visibility: hidden; }

        /* NAVBAR */
        .vx-navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 18px 0;
            border-bottom: 1px solid #1f1f1f;
            margin-bottom: 40px;
        }
        .vx-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 22px;
            font-weight: 800;
            color: #fafafa;
            letter-spacing: -0.5px;
        }
        .vx-logo-icon {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
            font-weight: 800;
        }
        .vx-nav-links {
            display: flex;
            gap: 28px;
            color: #a3a3a3;
            font-size: 14px;
            font-weight: 500;
        }

        /* HERO */
        .vx-hero {
            text-align: center;
            padding: 50px 20px 40px 20px;
            position: relative;
        }
        .vx-hero::before {
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
        .vx-badge {
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
        .vx-badge .dot {
            width: 6px;
            height: 6px;
            background: #3b82f6;
            border-radius: 50%;
        }
        .vx-hero h1 {
            font-size: 58px;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -2px;
            margin: 0 0 24px 0;
            background: linear-gradient(135deg, #fafafa 0%, #a3a3a3 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .vx-hero h1 .accent {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .vx-hero-sub {
            font-size: 19px;
            color: #a3a3a3;
            max-width: 640px;
            margin: 0 auto 36px auto;
            line-height: 1.5;
        }
        .vx-hero-sub strong { color: #fafafa; font-weight: 600; }

        /* ALERT */
        .vx-alert {
            background: #171717;
            border: 1px solid #262626;
            border-left: 3px solid #ef4444;
            padding: 20px 24px;
            border-radius: 12px;
            margin: 30px 0;
            color: #a3a3a3;
            font-size: 15px;
            line-height: 1.6;
        }
        .vx-alert strong { color: #fafafa; }
        .vx-alert .red { color: #ef4444; font-weight: 600; }

        /* STATS */
        .vx-stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin: 40px 0;
        }
        .vx-stat {
            background: #171717;
            border: 1px solid #262626;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .vx-stat-value {
            font-size: 32px;
            font-weight: 800;
            color: #fafafa;
            letter-spacing: -1px;
        }
        .vx-stat-label {
            font-size: 12px;
            color: #737373;
            font-weight: 500;
            margin-top: 4px;
        }

        /* SECTION */
        .vx-section {
            text-align: center;
            margin: 60px 0 32px 0;
        }
        .vx-section h2 {
            font-size: 36px;
            font-weight: 700;
            letter-spacing: -1px;
            color: #fafafa;
            margin: 0 0 10px 0;
        }
        .vx-section p {
            color: #a3a3a3;
            font-size: 16px;
            margin: 0;
        }

        /* PRICING */
        .vx-pricing {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin: 30px 0;
        }
        .vx-price-card {
            background: #171717;
            border: 1px solid #262626;
            padding: 28px 24px;
            border-radius: 14px;
            position: relative;
        }
        .vx-price-card.featured {
            border-color: #3b82f6;
            background: linear-gradient(180deg, rgba(59, 130, 246, 0.08) 0%, #171717 100%);
        }
        .vx-badge-pop {
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
        .vx-plan-name {
            font-size: 14px;
            font-weight: 600;
            color: #a3a3a3;
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .vx-price {
            font-size: 36px;
            font-weight: 800;
            color: #fafafa;
            letter-spacing: -1.5px;
            line-height: 1;
        }
        .vx-period { font-size: 13px; color: #737373; margin: 4px 0 20px 0; }
        .vx-features { list-style: none; padding: 0; margin: 0; }
        .vx-features li {
            color: #d4d4d4;
            font-size: 13px;
            padding: 7px 0 7px 20px;
            position: relative;
            line-height: 1.5;
        }
        .vx-features li::before {
            content: '✓';
            position: absolute;
            left: 0;
            color: #3b82f6;
            font-weight: 700;
        }

        /* EARLY BIRD */
        .vx-early {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(59, 130, 246, 0.3);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin: 20px 0 40px 0;
        }
        .vx-early-title {
            font-size: 14px;
            font-weight: 700;
            color: #60a5fa;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .vx-early-desc { color: #d4d4d4; font-size: 15px; }
        .vx-early-desc strong { color: #fafafa; }

        /* FOOTER */
        .vx-footer {
            border-top: 1px solid #1f1f1f;
            padding: 40px 0 20px 0;
            text-align: center;
            color: #737373;
            font-size: 13px;
            margin-top: 60px;
        }
        .vx-footer .brand {
            font-size: 18px;
            font-weight: 800;
            color: #fafafa;
            margin-bottom: 6px;
        }
        .vx-footer .tagline { color: #a3a3a3; margin-bottom: 16px; font-size: 13px; }
        .vx-footer .copyright { color: #404040; font-size: 11px; margin-top: 20px; }

        @media (max-width: 768px) {
            .vx-hero h1 { font-size: 36px; letter-spacing: -1px; }
            .vx-hero-sub { font-size: 15px; }
            .vx-stats { grid-template-columns: repeat(2, 1fr); }
            .vx-pricing { grid-template-columns: 1fr; }
            .vx-nav-links { display: none; }
        }
    </style>
    """, unsafe_allow_html=True)

    # ============================================================
    # DIL SECICI (sag ust)
    # ============================================================
    _dil_secici_landing()

    # ============================================================
    # NAVBAR + LOGO
    # ============================================================
    st.markdown("""
    <div class="vx-navbar">
        <div class="vx-logo">
            <span class="vx-logo-icon">◆</span>
            Veraxio
        </div>
        <div class="vx-nav-links">
            <span>Özellikler</span>
            <span>Fiyatlandırma</span>
            <span>İletişim</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # HERO
    # ============================================================
    st.markdown("""
    <div class="vx-hero">
        <div class="vx-badge">
            <span class="dot"></span>
            AB AI Act Madde 50 Uyumlu
        </div>
        <h1>
            AI uyumluluğunu<br>
            <span class="accent">otomatikleştiriyoruz</span>
        </h1>
        <p class="vx-hero-sub">
            5 dakikada AI sistemlerinizi denetleyin,<br>
            <strong>15 milyon Euro</strong> ceza riskinden kaçının.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # GIRIS / UCRETSIZ DEMO BUTONU
    # ============================================================
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("🔐  Giriş Yap", type="primary", use_container_width=True, key="landing_login_btn"):
                st.session_state["landing_goster"] = False
                st.rerun()
        with btn2:
            if st.button("🎁  Ücretsiz Dene", use_container_width=True, key="landing_demo_btn"):
                st.session_state["landing_goster"] = False
                st.session_state["ucretsiz_demo"] = True
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================
    # ALERT
    # ============================================================
    st.markdown("""
    <div class="vx-alert">
        ⚠️ <strong>2 Ağustos 2026'dan itibaren yürürlükte.</strong><br>
        Chatbot'unuzda AI bildirimi yoksa, görsellerinizde C2PA işaretleme eksikse
        <span class="red">15 milyon Euro veya cironun %3'ü</span> ceza riski var.
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # STATS
    # ============================================================
    st.markdown("""
    <div class="vx-stats">
        <div class="vx-stat">
            <div class="vx-stat-value">15M€</div>
            <div class="vx-stat-label">Maksimum Ceza</div>
        </div>
        <div class="vx-stat">
            <div class="vx-stat-value">11</div>
            <div class="vx-stat-label">AI Tipi Denetimi</div>
        </div>
        <div class="vx-stat">
            <div class="vx-stat-value">5</div>
            <div class="vx-stat-label">Dil Desteği</div>
        </div>
        <div class="vx-stat">
            <div class="vx-stat-value">4</div>
            <div class="vx-stat-label">Katmanlı Tespit</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # FIYATLANDIRMA
    # ============================================================
    st.markdown("""
    <div class="vx-section">
        <h2>Fiyatlandırma</h2>
        <p>İhtiyacınıza uygun paketi seçin</p>
    </div>

    <div class="vx-pricing">
        <div class="vx-price-card">
            <div class="vx-plan-name">Starter</div>
            <div class="vx-price">4.900 TL</div>
            <div class="vx-period">/ ay</div>
            <ul class="vx-features">
                <li>1 chatbot denetimi</li>
                <li>10 görsel / ay</li>
                <li>PDF rapor</li>
                <li>E-posta desteği</li>
            </ul>
        </div>
        <div class="vx-price-card featured">
            <div class="vx-badge-pop">Popüler</div>
            <div class="vx-plan-name">Pro</div>
            <div class="vx-price">12.900 TL</div>
            <div class="vx-period">/ ay</div>
            <ul class="vx-features">
                <li>5 chatbot denetimi</li>
                <li>50 görsel / ay</li>
                <li>REST API erişimi</li>
                <li>Zamanlanmış denetim</li>
                <li>Otomatik e-posta raporu</li>
            </ul>
        </div>
        <div class="vx-price-card">
            <div class="vx-plan-name">Enterprise</div>
            <div class="vx-price">39.900 TL</div>
            <div class="vx-period">/ ay</div>
            <ul class="vx-features">
                <li>Sınırsız denetim</li>
                <li>Özel entegrasyon</li>
                <li>Öncelikli destek</li>
                <li>AB temsilcisi takibi</li>
            </ul>
        </div>
    </div>

    <div class="vx-early">
        <div class="vx-early-title">Erken Kuş İndirimi</div>
        <div class="vx-early-desc">
            İlk 10 müşteriye Pro paket <strong>6.900 TL/ay</strong> (%47 indirim) — 12 aylık taahhüt ile
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # UCRETSIZ DEMO CTA (en altta tekrar)
    # ============================================================
    st.markdown("""
    <div class="vx-section">
        <h2>14 Gün Ücretsiz Deneyin</h2>
        <p>Kredi kartı gerekmez. İstediğiniz an iptal edin.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀  Hemen Başla — Ücretsiz", type="primary", use_container_width=True, key="landing_cta_btn"):
            st.session_state["landing_goster"] = False
            st.session_state["ucretsiz_demo"] = True
            st.rerun()

    # ============================================================
    # FOOTER
    # ============================================================
    st.markdown("""
    <div class="vx-footer">
        <div class="brand">◆ Veraxio</div>
        <div class="tagline">AB AI Act Madde 50 Uyumluluk Platformu</div>
        <div>info@veraxio.ai</div>
        <div class="copyright">© 2026 Veraxio. Tüm hakları saklıdır.</div>
    </div>
    """, unsafe_allow_html=True)
