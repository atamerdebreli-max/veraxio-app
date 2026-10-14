"""
landing_embed.py - Veraxio Landing Sayfasi
Logo + 5 Dil + Fiyatlar + Ucretsiz Demo
"""
import streamlit as st


# ============================================================
# 5 DIL SOZLUGU
# ============================================================
L = {
    "tr": {
        "lang_label": "Dil",
        "badge": "AB AI Act Madde 50 Uyumlu",
        "h1_1": "AI uyumluluğunu",
        "h1_2": "otomatikleştiriyoruz",
        "sub_1": "5 dakikada AI sistemlerinizi denetleyin,",
        "sub_2": "15 milyon Euro",
        "sub_3": "ceza riskinden kaçının.",
        "login_btn": "🔐  Giriş Yap",
        "demo_btn": "🎁  Ücretsiz Dene",
        "alert_title": "2 Ağustos 2026'dan itibaren yürürlükte.",
        "alert_body": "Chatbot'unuzda AI bildirimi yoksa, görsellerinizde C2PA işaretleme eksikse",
        "alert_red": "15 milyon Euro veya cironun %3'ü",
        "alert_end": "ceza riski var.",
        "stat1": "Maksimum Ceza",
        "stat2": "AI Tipi Denetimi",
        "stat3": "Dil Desteği",
        "stat4": "Katmanlı Tespit",
        "pricing_title": "Fiyatlandırma",
        "pricing_sub": "İhtiyacınıza uygun paketi seçin",
        "popular": "Popüler",
        "select_btn": "Seç",
        "starter_name": "Starter",
        "pro_name": "Pro",
        "ent_name": "Kurumsal",
        "starter_f1": "1 chatbot denetimi",
        "starter_f2": "10 görsel / ay",
        "starter_f3": "PDF rapor",
        "starter_f4": "E-posta desteği",
        "pro_f1": "5 chatbot denetimi",
        "pro_f2": "50 görsel / ay",
        "pro_f3": "REST API erişimi",
        "pro_f4": "Zamanlanmış denetim",
        "pro_f5": "Otomatik e-posta raporu",
        "ent_f1": "Sınırsız denetim",
        "ent_f2": "Özel entegrasyon",
        "ent_f3": "Öncelikli destek",
        "ent_f4": "AB temsilcisi takibi",
        "early_title": "Erken Kuş İndirimi",
        "early_desc_1": "İlk 10 müşteriye Pro paket",
        "early_desc_2": "%47 indirim",
        "early_desc_3": "12 aylık taahhüt ile",
        "cta_title": "14 Gün Ücretsiz Deneyin",
        "cta_sub": "Kredi kartı gerekmez. İstediğiniz an iptal edin.",
        "cta_btn": "🚀  Hemen Başla — Ücretsiz",
        "footer_tagline": "AB AI Act Madde 50 Uyumluluk Platformu",
        "copyright": "© 2026 Veraxio. Tüm hakları saklıdır.",
    },
    "en": {
        "lang_label": "Language",
        "badge": "EU AI Act Article 50 Compliant",
        "h1_1": "We automate",
        "h1_2": "AI compliance",
        "sub_1": "Audit your AI systems in 5 minutes,",
        "sub_2": "15 million Euro",
        "sub_3": "avoid the fine risk.",
        "login_btn": "🔐  Sign In",
        "demo_btn": "🎁  Try Free",
        "alert_title": "In effect from August 2, 2026.",
        "alert_body": "If your chatbot lacks AI disclosure, if your images lack C2PA marking",
        "alert_red": "15 million Euro or 3% of turnover",
        "alert_end": "fine risk exists.",
        "stat1": "Maximum Fine",
        "stat2": "AI Type Audits",
        "stat3": "Language Support",
        "stat4": "Layer Detection",
        "pricing_title": "Pricing",
        "pricing_sub": "Choose the plan that fits your needs",
        "popular": "Popular",
        "select_btn": "Select",
        "starter_name": "Starter",
        "pro_name": "Pro",
        "ent_name": "Enterprise",
        "starter_f1": "1 chatbot audit",
        "starter_f2": "10 images / month",
        "starter_f3": "PDF report",
        "starter_f4": "Email support",
        "pro_f1": "5 chatbot audits",
        "pro_f2": "50 images / month",
        "pro_f3": "REST API access",
        "pro_f4": "Scheduled audits",
        "pro_f5": "Automatic email report",
        "ent_f1": "Unlimited audits",
        "ent_f2": "Custom integration",
        "ent_f3": "Priority support",
        "ent_f4": "EU representative tracking",
        "early_title": "Early Bird Discount",
        "early_desc_1": "For the first 10 customers, Pro plan",
        "early_desc_2": "47% off",
        "early_desc_3": "with 12-month commitment",
        "cta_title": "Try Free for 14 Days",
        "cta_sub": "No credit card required. Cancel anytime.",
        "cta_btn": "🚀  Start Now — Free",
        "footer_tagline": "EU AI Act Article 50 Compliance Platform",
        "copyright": "© 2026 Veraxio. All rights reserved.",
    },
    "bg": {
        "lang_label": "Език",
        "badge": "Съответствие с член 50 от AI Act на ЕС",
        "h1_1": "Ние автоматизираме",
        "h1_2": "AI съответствието",
        "sub_1": "Одитирайте AI системите си за 5 минути,",
        "sub_2": "15 милиона евро",
        "sub_3": "избегнете риска от глоба.",
        "login_btn": "🔐  Вход",
        "demo_btn": "🎁  Безплатен тест",
        "alert_title": "В сила от 2 август 2026 г.",
        "alert_body": "Ако вашият чатбот няма AI декларация, ако изображенията ви нямат C2PA маркировка",
        "alert_red": "15 милиона евро или 3% от оборота",
        "alert_end": "съществува риск от глоба.",
        "stat1": "Максимална глоба",
        "stat2": "AI одити",
        "stat3": "Езикова поддръжка",
        "stat4": "Слойно откриване",
        "pricing_title": "Ценообразуване",
        "pricing_sub": "Изберете подходящия план",
        "popular": "Популярен",
        "select_btn": "Избор",
        "starter_name": "Starter",
        "pro_name": "Pro",
        "ent_name": "Корпоративен",
        "starter_f1": "1 одит на чатбот",
        "starter_f2": "10 изображения / месец",
        "starter_f3": "PDF отчет",
        "starter_f4": "Имейл поддръжка",
        "pro_f1": "5 одита на чатбот",
        "pro_f2": "50 изображения / месец",
        "pro_f3": "REST API достъп",
        "pro_f4": "Планирани одити",
        "pro_f5": "Автоматичен имейл отчет",
        "ent_f1": "Неограничени одити",
        "ent_f2": "Персонализирана интеграция",
        "ent_f3": "Приоритетна поддръжка",
        "ent_f4": "Проследяване на ЕС представител",
        "early_title": "Ранна отстъпка",
        "early_desc_1": "За първите 10 клиенти, Pro план",
        "early_desc_2": "47% отстъпка",
        "early_desc_3": "с 12-месечен ангажимент",
        "cta_title": "Опитайте безплатно 14 дни",
        "cta_sub": "Без кредитна карта. Отказ по всяко време.",
        "cta_btn": "🚀  Започнете сега — безплатно",
        "footer_tagline": "Платформа за съответствие с член 50 от AI Act на ЕС",
        "copyright": "© 2026 Veraxio. Всички права запазени.",
    },
    "ro": {
        "lang_label": "Limbă",
        "badge": "Conform Regulamentului AI Act Articolul 50",
        "h1_1": "Automatizăm",
        "h1_2": "conformitatea AI",
        "sub_1": "Auditați-vă sistemele AI în 5 minute,",
        "sub_2": "15 milioane Euro",
        "sub_3": "evitați riscul de amendă.",
        "login_btn": "🔐  Autentificare",
        "demo_btn": "🎁  Încearcă gratuit",
        "alert_title": "În vigoare din 2 august 2026.",
        "alert_body": "Dacă chatbotul dvs. nu are declarare AI, dacă imaginile dvs. nu au marcaj C2PA",
        "alert_red": "15 milioane Euro sau 3% din cifra de afaceri",
        "alert_end": "există risc de amendă.",
        "stat1": "Amendă maximă",
        "stat2": "Audituri AI",
        "stat3": "Suport lingvistic",
        "stat4": "Detecție pe straturi",
        "pricing_title": "Prețuri",
        "pricing_sub": "Alegeți planul potrivit",
        "popular": "Popular",
        "select_btn": "Selectează",
        "starter_name": "Starter",
        "pro_name": "Pro",
        "ent_name": "Enterprise",
        "starter_f1": "1 audit chatbot",
        "starter_f2": "10 imagini / lună",
        "starter_f3": "Raport PDF",
        "starter_f4": "Suport email",
        "pro_f1": "5 audituri chatbot",
        "pro_f2": "50 imagini / lună",
        "pro_f3": "Acces REST API",
        "pro_f4": "Audituri programate",
        "pro_f5": "Raport automat prin email",
        "ent_f1": "Audituri nelimitate",
        "ent_f2": "Integrare personalizată",
        "ent_f3": "Suport prioritar",
        "ent_f4": "Urmărire reprezentant UE",
        "early_title": "Reducere Early Bird",
        "early_desc_1": "Pentru primii 10 clienți, planul Pro",
        "early_desc_2": "47% reducere",
        "early_desc_3": "cu angajament de 12 luni",
        "cta_title": "Încercați gratuit 14 zile",
        "cta_sub": "Fără card de credit. Anulați oricând.",
        "cta_btn": "🚀  Începeți acum — gratuit",
        "footer_tagline": "Platformă de conformitate AI Act Articolul 50",
        "copyright": "© 2026 Veraxio. Toate drepturile rezervate.",
    },
    "hr": {
        "lang_label": "Jezik",
        "badge": "Usklađeno s člankom 50 AI Act EU-a",
        "h1_1": "Automatiziramo",
        "h1_2": "AI usklađenost",
        "sub_1": "Revidirajte svoje AI sustave u 5 minuta,",
        "sub_2": "15 milijuna eura",
        "sub_3": "izbjegnite rizik od kazne.",
        "login_btn": "🔐  Prijava",
        "demo_btn": "🎁  Besplatno isprobaj",
        "alert_title": "Na snazi od 2. kolovoza 2026.",
        "alert_body": "Ako vaš chatbot nema AI objavu, ako vaše slike nemaju C2PA oznaku",
        "alert_red": "15 milijuna eura ili 3% prometa",
        "alert_end": "postoji rizik od kazne.",
        "stat1": "Maksimalna kazna",
        "stat2": "AI revizije",
        "stat3": "Jezična podrška",
        "stat4": "Slojevito otkrivanje",
        "pricing_title": "Cijene",
        "pricing_sub": "Odaberite odgovarajući plan",
        "popular": "Popularno",
        "select_btn": "Odaberi",
        "starter_name": "Starter",
        "pro_name": "Pro",
        "ent_name": "Enterprise",
        "starter_f1": "1 revizija chatbota",
        "starter_f2": "10 slika / mjesec",
        "starter_f3": "PDF izvještaj",
        "starter_f4": "Email podrška",
        "pro_f1": "5 revizija chatbota",
        "pro_f2": "50 slika / mjesec",
        "pro_f3": "REST API pristup",
        "pro_f4": "Zakazane revizije",
        "pro_f5": "Automatski email izvještaj",
        "ent_f1": "Neograničene revizije",
        "ent_f2": "Prilagođena integracija",
        "ent_f3": "Prioritetna podrška",
        "ent_f4": "Praćenje EU predstavnika",
        "early_title": "Rani popust",
        "early_desc_1": "Za prvih 10 kupaca, Pro plan",
        "early_desc_2": "47% popusta",
        "early_desc_3": "uz 12-mjesečnu obvezu",
        "cta_title": "Isprobajte besplatno 14 dana",
        "cta_sub": "Bez kreditne kartice. Otkažite bilo kada.",
        "cta_btn": "🚀  Započnite sada — besplatno",
        "footer_tagline": "Platforma za usklađenost s člankom 50 AI Act EU-a",
        "copyright": "© 2026 Veraxio. Sva prava pridržana.",
    },
}


def _t():
    """Aktif dile gore ceviri sozlugunu dondurur."""
    dil = st.session_state.get("dil", "tr")
    if dil not in L:
        dil = "tr"
    return L[dil]


def _dil_secici_ust():
    """Sag ustte 5 dilli secici."""
    dil_kodlari = ["tr", "en", "bg", "ro", "hr"]
    etiketler = ["🇹🇷 TR", "🇬🇧 EN", "🇧🇬 BG", "🇷🇴 RO", "🇭🇷 HR"]
    mevcut = st.session_state.get("dil", "tr")
    if mevcut not in dil_kodlari:
        mevcut = "tr"
    mevcut_idx = dil_kodlari.index(mevcut)

    secilen_etiket = st.selectbox(
        "dil",
        etiketler,
        index=mevcut_idx,
        key="landing_dil_secim",
        label_visibility="collapsed",
    )
    yeni_dil = dil_kodlari[etiketler.index(secilen_etiket)]
    if yeni_dil != mevcut:
        st.session_state["dil"] = yeni_dil
        st.rerun()


def goster():
    """Landing sayfasi."""
    T = _t()

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

        .vx-logo-wrap {
            display: flex; align-items: center; gap: 10px; padding: 12px 0;
        }
        .vx-logo-icon {
            width: 34px; height: 34px;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            border-radius: 8px;
            display: inline-flex; align-items: center; justify-content: center;
            color: white; font-size: 18px; font-weight: 800;
        }
        .vx-logo-text {
            font-size: 24px; font-weight: 800; color: #fafafa;
            letter-spacing: -0.5px;
        }
        .vx-divider {
            border-bottom: 1px solid #1f1f1f; margin: 8px 0 30px 0;
        }

        .vx-hero {
            text-align: center; padding: 40px 20px 20px 20px; position: relative;
        }
        .vx-hero::before {
            content: '';
            position: absolute; top: -50px; left: 50%;
            transform: translateX(-50%);
            width: 600px; height: 400px;
            background: radial-gradient(ellipse at center, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
            pointer-events: none; z-index: -1;
        }
        .vx-badge {
            display: inline-flex; align-items: center; gap: 8px;
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            color: #60a5fa; padding: 6px 14px; border-radius: 20px;
            font-size: 13px; font-weight: 500; margin-bottom: 24px;
        }
        .vx-badge .dot {
            width: 6px; height: 6px; background: #3b82f6; border-radius: 50%;
        }
        .vx-hero h1 {
            font-size: 58px; font-weight: 800; line-height: 1.05;
            letter-spacing: -2px; margin: 0 0 24px 0;
            background: linear-gradient(135deg, #fafafa 0%, #a3a3a3 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .vx-hero h1 .accent {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .vx-hero-sub {
            font-size: 19px; color: #a3a3a3; max-width: 640px;
            margin: 0 auto 20px auto; line-height: 1.5;
        }
        .vx-hero-sub strong { color: #fafafa; font-weight: 600; }

        .vx-alert {
            background: #171717; border: 1px solid #262626;
            border-left: 3px solid #ef4444;
            padding: 20px 24px; border-radius: 12px;
            margin: 30px 0; color: #a3a3a3;
            font-size: 15px; line-height: 1.6;
        }
        .vx-alert strong { color: #fafafa; }
        .vx-alert .red { color: #ef4444; font-weight: 600; }

        .vx-stats {
            display: grid; grid-template-columns: repeat(4, 1fr);
            gap: 14px; margin: 40px 0;
        }
        .vx-stat {
            background: #171717; border: 1px solid #262626;
            padding: 20px; border-radius: 12px; text-align: center;
        }
        .vx-stat-value {
            font-size: 32px; font-weight: 800; color: #fafafa;
            letter-spacing: -1px;
        }
        .vx-stat-label {
            font-size: 12px; color: #737373;
            font-weight: 500; margin-top: 4px;
        }

        .vx-section {
            text-align: center; margin: 50px 0 24px 0;
        }
        .vx-section h2 {
            font-size: 36px; font-weight: 700;
            letter-spacing: -1px; color: #fafafa;
            margin: 0 0 10px 0;
        }
        .vx-section p {
            color: #a3a3a3; font-size: 16px; margin: 0;
        }

        .vx-price-card {
            background: #171717; border: 1px solid #262626;
            padding: 24px 20px; border-radius: 14px;
            position: relative; min-height: 280px;
        }
        .vx-price-card.featured {
            border-color: #3b82f6;
            background: linear-gradient(180deg, rgba(59, 130, 246, 0.08) 0%, #171717 100%);
        }
        .vx-badge-pop {
            position: absolute; top: -12px; left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white; font-size: 11px; font-weight: 700;
            padding: 5px 12px; border-radius: 20px;
            letter-spacing: 0.5px; text-transform: uppercase;
        }
        .vx-plan-name {
            font-size: 14px; font-weight: 600; color: #a3a3a3;
            margin-bottom: 14px; text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .vx-price {
            font-size: 34px; font-weight: 800; color: #fafafa;
            letter-spacing: -1.5px; line-height: 1;
        }
        .vx-period { font-size: 13px; color: #737373; margin: 4px 0 18px 0; }
        .vx-features { list-style: none; padding: 0; margin: 0; }
        .vx-features li {
            color: #d4d4d4; font-size: 13px;
            padding: 6px 0 6px 20px; position: relative; line-height: 1.5;
        }
        .vx-features li::before {
            content: '✓'; position: absolute; left: 0;
            color: #3b82f6; font-weight: 700;
        }

        .vx-early {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(59, 130, 246, 0.3);
            padding: 20px; border-radius: 12px;
            text-align: center; margin: 24px 0 40px 0;
        }
        .vx-early-title {
            font-size: 14px; font-weight: 700; color: #60a5fa;
            margin-bottom: 6px; text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .vx-early-desc { color: #d4d4d4; font-size: 15px; }
        .vx-early-desc strong { color: #fafafa; }

        .vx-footer {
            border-top: 1px solid #1f1f1f;
            padding: 40px 0 20px 0; text-align: center;
            color: #737373; font-size: 13px; margin-top: 60px;
        }
        .vx-footer .brand {
            font-size: 18px; font-weight: 800;
            color: #fafafa; margin-bottom: 6px;
        }
        .vx-footer .tagline {
            color: #a3a3a3; margin-bottom: 16px; font-size: 13px;
        }
        .vx-footer .copyright {
            color: #404040; font-size: 11px; margin-top: 20px;
        }

        @media (max-width: 768px) {
            .vx-hero h1 { font-size: 34px; letter-spacing: -1px; }
            .vx-hero-sub { font-size: 15px; }
            .vx-stats { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
    """, unsafe_allow_html=True)

    # ============================================================
    # NAVBAR: logo (sol) + dil secici + giris (sag)
    # ============================================================
    nav1, nav2, nav3 = st.columns([4, 2, 1])

    with nav1:
        st.markdown("""
        <div class="vx-logo-wrap">
            <span class="vx-logo-icon">◆</span>
            <span class="vx-logo-text">Veraxio</span>
        </div>
        """, unsafe_allow_html=True)

    with nav2:
        st.markdown("<br>", unsafe_allow_html=True)
        _dil_secici_ust()

    with nav3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔐", key="nav_giris_btn", type="primary", use_container_width=True):
            st.session_state["landing_goster"] = False
            st.rerun()

    st.markdown('<div class="vx-divider"></div>', unsafe_allow_html=True)

    # ============================================================
    # HERO
    # ============================================================
    st.markdown(f"""
    <div class="vx-hero">
        <div class="vx-badge">
            <span class="dot"></span>
            {T['badge']}
        </div>
        <h1>
            {T['h1_1']}<br>
            <span class="accent">{T['h1_2']}</span>
        </h1>
        <p class="vx-hero-sub">
            {T['sub_1']}<br>
            <strong>{T['sub_2']}</strong> {T['sub_3']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # GIRIS / DEMO BUTONLARI
    # ============================================================
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button(T['login_btn'], type="primary", use_container_width=True, key="hero_login_btn"):
                st.session_state["landing_goster"] = False
                st.rerun()
        with btn2:
            if st.button(T['demo_btn'], use_container_width=True, key="hero_demo_btn"):
                st.session_state["landing_goster"] = False
                st.session_state["ucretsiz_demo"] = True
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================
    # ALERT
    # ============================================================
    st.markdown(f"""
    <div class="vx-alert">
        ⚠️ <strong>{T['alert_title']}</strong><br>
        {T['alert_body']}
        <span class="red">{T['alert_red']}</span> {T['alert_end']}
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # STATS
    # ============================================================
    st.markdown(f"""
    <div class="vx-stats">
        <div class="vx-stat">
            <div class="vx-stat-value">15M€</div>
            <div class="vx-stat-label">{T['stat1']}</div>
        </div>
        <div class="vx-stat">
            <div class="vx-stat-value">11</div>
            <div class="vx-stat-label">{T['stat2']}</div>
        </div>
        <div class="vx-stat">
            <div class="vx-stat-value">5</div>
            <div class="vx-stat-label">{T['stat3']}</div>
        </div>
        <div class="vx-stat">
            <div class="vx-stat-value">4</div>
            <div class="vx-stat-label">{T['stat4']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # FIYATLANDIRMA
    # ============================================================
    st.markdown(f"""
    <div class="vx-section">
        <h2>{T['pricing_title']}</h2>
        <p>{T['pricing_sub']}</p>
    </div>
    """, unsafe_allow_html=True)

    fcol1, fcol2, fcol3 = st.columns(3)

    # STARTER
    with fcol1:
        st.markdown(f"""
        <div class="vx-price-card">
            <div class="vx-plan-name">{T['starter_name']}</div>
            <div class="vx-price">4.900 TL</div>
            <div class="vx-period">/ ay</div>
            <ul class="vx-features">
                <li>{T['starter_f1']}</li>
                <li>{T['starter_f2']}</li>
                <li>{T['starter_f3']}</li>
                <li>{T['starter_f4']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"{T['select_btn']} →", key="plan_starter_btn", use_container_width=True):
            st.session_state["landing_goster"] = False
            st.session_state["secilen_plan"] = "starter"
            st.rerun()

    # PRO
    with fcol2:
        st.markdown(f"""
        <div class="vx-price-card featured">
            <div class="vx-badge-pop">{T['popular']}</div>
            <div class="vx-plan-name">{T['pro_name']}</div>
            <div class="vx-price">12.900 TL</div>
            <div class="vx-period">/ ay</div>
            <ul class="vx-features">
                <li>{T['pro_f1']}</li>
                <li>{T['pro_f2']}</li>
                <li>{T['pro_f3']}</li>
                <li>{T['pro_f4']}</li>
                <li>{T['pro_f5']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"{T['select_btn']} →", key="plan_pro_btn", type="primary", use_container_width=True):
            st.session_state["landing_goster"] = False
            st.session_state["secilen_plan"] = "pro"
            st.rerun()

    # ENTERPRISE
    with fcol3:
        st.markdown(f"""
        <div class="vx-price-card">
            <div class="vx-plan-name">{T['ent_name']}</div>
            <div class="vx-price">39.900 TL</div>
            <div class="vx-period">/ ay</div>
            <ul class="vx-features">
                <li>{T['ent_f1']}</li>
                <li>{T['ent_f2']}</li>
                <li>{T['ent_f3']}</li>
                <li>{T['ent_f4']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"{T['select_btn']} →", key="plan_ent_btn", use_container_width=True):
            st.session_state["landing_goster"] = False
            st.session_state["secilen_plan"] = "enterprise"
            st.rerun()

    # ============================================================
    # EARLY BIRD
    # ============================================================
    st.markdown(f"""
    <div class="vx-early">
        <div class="vx-early-title">{T['early_title']}</div>
        <div class="vx-early-desc">
            {T['early_desc_1']} <strong>6.900 TL/ay</strong> ({T['early_desc_2']}) — {T['early_desc_3']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # CTA
    # ============================================================
    st.markdown(f"""
    <div class="vx-section">
        <h2>{T['cta_title']}</h2>
        <p>{T['cta_sub']}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(T['cta_btn'], type="primary", use_container_width=True, key="cta_bottom_btn"):
            st.session_state["landing_goster"] = False
            st.session_state["ucretsiz_demo"] = True
            st.rerun()

    # ============================================================
    # FOOTER
    # ============================================================
    st.markdown(f"""
    <div class="vx-footer">
        <div class="brand">◆ Veraxio</div>
        <div class="tagline">{T['footer_tagline']}</div>
        <div>info@veraxio.ai</div>
        <div class="copyright">{T['copyright']}</div>
    </div>
    """, unsafe_allow_html=True)
