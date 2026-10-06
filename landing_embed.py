"""
landing_embed.py - Landing sayfasi (dashboard icine gomulu)
"""
import streamlit as st


def goster():
    """Landing page'i gosterir + Giris Yap butonu ekler."""

    # CSS
    st.markdown("""
    <style>
        .hero {
            text-align: center;
            padding: 60px 20px 40px 20px;
        }
        .hero h1 {
            font-size: 56px;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -2px;
            margin: 0 0 24px 0;
            background: linear-gradient(135deg, #fafafa 0%, #a3a3a3 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero h1 .accent {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-badge {
            display: inline-block;
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.4);
            color: #60a5fa;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 24px;
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
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin: 48px 0;
        }
        .stat-card {
            background: #171717;
            border: 1px solid #262626;
            padding: 24px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-value {
            font-size: 36px;
            font-weight: 800;
            color: #fafafa;
            margin-bottom: 4px;
        }
        .stat-label {
            font-size: 13px;
            color: #737373;
        }
        .alert-banner {
            background: #171717;
            border: 1px solid #262626;
            border-left: 3px solid #ef4444;
            padding: 24px 28px;
            border-radius: 12px;
            margin: 24px 0;
            color: #a3a3a3;
            font-size: 15px;
            line-height: 1.6;
        }
        .alert-banner strong { color: #fafafa; }
        .alert-banner .red { color: #ef4444; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

    # HERO
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">● AB AI Act Madde 50 Uyumlu</div>
        <h1>AI uyumluluğunu<br><span class="accent">otomatikleştiriyoruz</span></h1>
        <p class="hero-sub">
            5 dakikada AI sistemlerinizi denetleyin,<br>
            <strong>15 milyon Euro</strong> ceza riskinden kaçının.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # GIRIS YAP BUTONU
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐  Giriş Yap  /  Kayıt Ol", type="primary", use_container_width=True, key="landing_giris_btn"):
            st.session_state["landing_goster"] = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ALERT
    st.markdown("""
    <div class="alert-banner">
        ⚠️ <strong>2 Ağustos 2026'dan itibaren yürürlükte.</strong><br>
        Chatbot'unuzda AI bildirimi yoksa, görsellerinizde C2PA işaretleme eksikse
        <span class="red">15 milyon Euro veya cironun %3'ü</span> ceza riski var.
    </div>
    """, unsafe_allow_html=True)

    # STATS
    st.markdown("""
    <div class="stat-grid">
        <div class="stat-card"><div class="stat-value">15M€</div><div class="stat-label">Maksimum Ceza</div></div>
        <div class="stat-card"><div class="stat-value">11</div><div class="stat-label">AI Tipi Denetimi</div></div>
        <div class="stat-card"><div class="stat-value">5</div><div class="stat-label">Dil Desteği</div></div>
        <div class="stat-card"><div class="stat-value">4</div><div class="stat-label">Katmanlı Tespit</div></div>
    </div>
    """, unsafe_allow_html=True)

    # FOOTER
    st.markdown("""
    <div style="text-align:center;color:#737373;padding:40px 0;border-top:1px solid #1f1f1f;margin-top:40px;">
        <div style="font-size:18px;font-weight:800;color:#fafafa;">◆ Veraxio</div>
        <div style="color:#a3a3a3;margin:8px 0;">AB AI Act Madde 50 Uyumluluk Platformu</div>
        <div style="font-size:12px;color:#525252;margin-top:20px;">© 2026 Veraxio. Tüm hakları saklıdır.</div>
    </div>
    """, unsafe_allow_html=True)
