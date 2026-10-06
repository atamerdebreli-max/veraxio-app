"""
4 hukuki sayfayi (gizlilik, kvkk, kullanim, dpa) 5 dile cevirir.
Her sayfa tek HTML + JS i18n.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

KOK = Path(".")
LOCALES = KOK / "locales"

# TR cevirileri yukle
tr = json.load(open(LOCALES / "tr.json", encoding="utf-8"))
en = json.load(open(LOCALES / "en.json", encoding="utf-8"))
bg = json.load(open(LOCALES / "bg.json", encoding="utf-8"))
ro = json.load(open(LOCALES / "ro.json", encoding="utf-8"))
hr = json.load(open(LOCALES / "hr.json", encoding="utf-8"))

H_TR = tr.get("hukuki", {})
H_EN = en.get("hukuki", {})
H_BG = bg.get("hukuki", {})
H_RO = ro.get("hukuki", {})
H_HR = hr.get("hukuki", {})


def _html_header(baslik):
    """Ortak header."""
    return f'''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{baslik} - Veraxio</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Inter', -apple-system, sans-serif;
        background: #0a0a0a;
        color: #fafafa;
        line-height: 1.7;
    }}
    .navbar {{
        padding: 20px 0;
        border-bottom: 1px solid #262626;
        background: rgba(10, 10, 10, 0.85);
        backdrop-filter: blur(12px);
        position: sticky; top: 0; z-index: 100;
    }}
    .container {{ max-width: 900px; margin: 0 auto; padding: 0 24px; }}
    .navbar .container {{
        display: flex; align-items: center; justify-content: space-between;
        max-width: 1200px;
    }}
    .logo {{
        font-size: 22px; font-weight: 800; letter-spacing: -0.5px;
        display: flex; align-items: center; gap: 10px; color: #fafafa;
        text-decoration: none;
    }}
    .logo-icon {{
        width: 28px; height: 28px;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 8px;
        display: inline-flex; align-items: center; justify-content: center;
        color: white; font-size: 14px; font-weight: 800;
    }}
    .nav-right {{ display: flex; align-items: center; gap: 16px; }}
    .nav-back {{
        color: #a3a3a3; text-decoration: none; font-size: 14px; font-weight: 500;
    }}
    .nav-back:hover {{ color: #fafafa; }}
    .lang-select {{
        background: #171717;
        border: 1px solid #262626;
        color: #fafafa;
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 13px;
        font-family: inherit;
        cursor: pointer;
        outline: none;
    }}
    .lang-select:hover {{ border-color: #3b82f6; }}
    .content {{ padding: 60px 0 100px; }}
    .page-header {{
        margin-bottom: 48px;
        padding-bottom: 24px;
        border-bottom: 2px solid #1f1f1f;
    }}
    .page-header h1 {{
        font-size: 44px; font-weight: 800; letter-spacing: -1.5px;
        margin-bottom: 12px;
    }}
    .page-header .meta {{ color: #737373; font-size: 14px; }}
    h2 {{
        font-size: 22px; font-weight: 700; letter-spacing: -0.5px;
        margin-top: 40px; margin-bottom: 16px;
        color: #fafafa;
    }}
    p {{
        color: #a3a3a3; font-size: 16px;
        margin-bottom: 16px;
    }}
    .info-box {{
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(139, 92, 246, 0.05) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-left: 4px solid #3b82f6;
        padding: 20px 24px;
        border-radius: 10px;
        margin: 24px 0;
        color: #d4d4d4;
        font-size: 15px;
    }}
    footer {{
        border-top: 1px solid #1f1f1f;
        padding: 40px 0 30px;
        text-align: center;
        color: #525252;
        font-size: 13px;
    }}
    footer a {{ color: #60a5fa; text-decoration: none; margin: 0 8px; }}
    footer a:hover {{ text-decoration: underline; }}
    .footer-links {{ margin-bottom: 16px; }}
    .footer-copy {{ font-size: 12px; color: #404040; }}
    @media (max-width: 768px) {{
        .page-header h1 {{ font-size: 32px; }}
        h2 {{ font-size: 18px; }}
        p {{ font-size: 15px; }}
        .nav-right {{ gap: 8px; }}
        .nav-back {{ display: none; }}
    }}
</style>
</head>
<body>

<nav class="navbar">
    <div class="container">
        <a href="index.html" class="logo">
            <span class="logo-icon">◆</span>
            Veraxio
        </a>
        <div class="nav-right">
            <a href="index.html" class="nav-back" data-i18n="back">← {H_TR.get("geri", "Geri")}</a>
            <select id="langSelector" class="lang-select" onchange="changeLang(this.value)">
                <option value="tr">🇹🇷 TR</option>
                <option value="en">🇬🇧 EN</option>
                <option value="bg">🇧🇬 BG</option>
                <option value="ro">🇷🇴 RO</option>
                <option value="hr">🇭🇷 HR</option>
            </select>
        </div>
    </div>
</nav>

<section class="content">
    <div class="container">
        <div class="page-header">
            <h1 id="page-title">{baslik}</h1>
            <div class="meta" data-i18n="meta">Son güncelleme: 4 Ekim 2026</div>
        </div>

        <div id="content-body">
'''

def _html_footer():
    return '''
        </div>
    </div>
</section>

<footer>
    <div class="container">
        <div class="footer-links">
            <a href="gizlilik.html" data-i18n="lnk_gizlilik">Gizlilik Politikası</a> ·
            <a href="kvkk.html" data-i18n="lnk_kvkk">KVKK Aydınlatma</a> ·
            <a href="kullanim.html" data-i18n="lnk_kullanim">Kullanım Şartları</a> ·
            <a href="dpa.html" data-i18n="lnk_dpa">Veri İşleme Sözleşmesi</a>
        </div>
        <div class="footer-copy" data-i18n="footer_copy">© 2026 Veraxio. Tüm hakları saklıdır.</div>
    </div>
</footer>

<script>
const HUKUKI = '''


def _html_js_sonu():
    return ''';

let currentLang = localStorage.getItem("veraxio_lang") || "tr";

function changeLang(lang) {
    currentLang = lang;
    localStorage.setItem("veraxio_lang", lang);
    render(lang);
}

function render(lang) {
    const t = HUKUKI[lang];
    if (!t) return;

    // Baslik
    const baslik = document.getElementById("page-title");
    if (baslik && t.baslik) baslik.textContent = t.baslik;

    // Icerik bolumleri
    let html = "";
    if (t.bolumler) {
        for (const [b, m] of t.bolumler) {
            if (b) html += "<h2>" + b + "</h2>";
            if (m) html += "<p>" + m + "</p>";
        }
    }
    document.getElementById("content-body").innerHTML = html;

    // Sayfa meta
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        const ceviriler = {
            "back": t.geri || "← Geri",
            "meta": t.meta || "Son güncelleme: 4 Ekim 2026",
            "lnk_gizlilik": t.lnk_gizlilik || "Gizlilik Politikası",
            "lnk_kvkk": t.lnk_kvkk || "KVKK Aydınlatma",
            "lnk_kullanim": t.lnk_kullanim || "Kullanım Şartları",
            "lnk_dpa": t.lnk_dpa || "Veri İşleme Sözleşmesi",
            "footer_copy": t.footer_copy || "© 2026 Veraxio. Tüm hakları saklıdır.",
        };
        if (ceviriler[key]) el.textContent = ceviriler[key];
    });

    document.documentElement.lang = lang;
    const sel = document.getElementById("langSelector");
    if (sel) sel.value = lang;
}

document.addEventListener("DOMContentLoaded", () => {
    const sel = document.getElementById("langSelector");
    if (sel) sel.value = currentLang;
    render(currentLang);
});
</script>

</body>
</html>'''


def _hukuki_json(h, geri="← Geri"):
    """Bir dilin hukuki icerigini JS objesi olarak dondurur."""
    def b(baslik_key, metin_key):
        return [h.get(baslik_key, ""), h.get(metin_key, "")]

    return {
        "baslik": h.get("gizlilik_baslik", "Gizlilik"),
        "geri": geri,
        "meta": h.get("son_guncelleme", "Son güncelleme: 4 Ekim 2026"),
        "lnk_gizlilik": h.get("tab_gizlilik", "Gizlilik"),
        "lnk_kvkk": h.get("tab_kvkk", "KVKK"),
        "lnk_kullanim": h.get("tab_kullanim", "Kullanım"),
        "lnk_dpa": h.get("tab_dpa", "DPA"),
        "footer_copy": "© 2026 Veraxio.",
        "bolumler": [],
    }


# ============================================================
# 1) GIZLILIK.HTML
# ============================================================
print("=" * 60)
print("1) gizlilik.html")
print("=" * 60)

def gizlilik_bolumler(h):
    return [
        [h.get("gizlilik_1_baslik", ""), h.get("gizlilik_1_metin", "")],
        [h.get("gizlilik_2_baslik", ""), h.get("gizlilik_2_metin", "")],
        [h.get("gizlilik_3_baslik", ""), h.get("gizlilik_3_metin", "")],
        [h.get("gizlilik_4_baslik", ""), h.get("gizlilik_4_metin", "")],
        [h.get("gizlilik_5_baslik", ""), h.get("gizlilik_5_metin", "")],
    ]

HUKUKI_GIZLILIK = {
    "tr": {"baslik": H_TR.get("gizlilik_baslik", "Gizlilik Politikası"), "bolumler": gizlilik_bolumler(H_TR)},
    "en": {"baslik": H_EN.get("gizlilik_baslik", "Privacy Policy"), "bolumler": gizlilik_bolumler(H_EN)},
    "bg": {"baslik": H_BG.get("gizlilik_baslik", "Политика за поверителност"), "bolumler": gizlilik_bolumler(H_BG)},
    "ro": {"baslik": H_RO.get("gizlilik_baslik", "Politica de confidentialitate"), "bolumler": gizlilik_bolumler(H_RO)},
    "hr": {"baslik": H_HR.get("gizlilik_baslik", "Politika privatnosti"), "bolumler": gizlilik_bolumler(H_HR)},
}

html = _html_header("Gizlilik Politikası") + _html_footer() + _html_js_sonu()
# JS objesini ekle
html = html.replace("const HUKUKI = ;", f"const HUKUKI = {json.dumps(HUKUKI_GIZLILIK, ensure_ascii=False)};")

# Yedek
if (KOK / "gizlilik.html").exists():
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(KOK / "gizlilik.html", KOK / f"gizlilik_i18n_oncesi_{zaman}.html.bak")

(KOK / "gizlilik.html").write_text(html, encoding="utf-8")
print("[+] gizlilik.html guncellendi.")

# ============================================================
# 2) KVKK.HTML
# ============================================================
print()
print("=" * 60)
print("2) kvkk.html")
print("=" * 60)

def kvkk_bolumler(h):
    return [
        [h.get("kvkk_1_baslik", ""), h.get("kvkk_1_metin", "")],
        [h.get("kvkk_2_baslik", ""), h.get("kvkk_2_metin", "")],
        [h.get("kvkk_3_baslik", ""), h.get("kvkk_3_metin", "")],
        [h.get("kvkk_4_baslik", ""), h.get("kvkk_4_metin", "")],
        [h.get("kvkk_5_baslik", ""), h.get("kvkk_5_metin", "")],
        [h.get("kvkk_6_baslik", ""), h.get("kvkk_6_metin", "")],
        ["Başvuru", h.get("kvkk_basvuru_bilgi", "")],
    ]

HUKUKI_KVKK = {
    "tr": {"baslik": H_TR.get("kvkk_baslik", "KVKK Aydınlatma"), "bolumler": kvkk_bolumler(H_TR)},
    "en": {"baslik": H_EN.get("kvkk_baslik", "KVKK Disclosure"), "bolumler": kvkk_bolumler(H_EN)},
    "bg": {"baslik": H_BG.get("kvkk_baslik", "KVKK разкритие"), "bolumler": kvkk_bolumler(H_BG)},
    "ro": {"baslik": H_RO.get("kvkk_baslik", "Divulgare KVKK"), "bolumler": kvkk_bolumler(H_RO)},
    "hr": {"baslik": H_HR.get("kvkk_baslik", "KVKK objava"), "bolumler": kvkk_bolumler(H_HR)},
}

html = _html_header("KVKK Aydınlatma") + _html_footer() + _html_js_sonu()
html = html.replace("const HUKUKI = ;", f"const HUKUKI = {json.dumps(HUKUKI_KVKK, ensure_ascii=False)};")

if (KOK / "kvkk.html").exists():
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(KOK / "kvkk.html", KOK / f"kvkk_i18n_oncesi_{zaman}.html.bak")

(KOK / "kvkk.html").write_text(html, encoding="utf-8")
print("[+] kvkk.html guncellendi.")

# ============================================================
# 3) KULLANIM.HTML
# ============================================================
print()
print("=" * 60)
print("3) kullanim.html")
print("=" * 60)

def kullanim_bolumler(h):
    return [
        [h.get("kullanim_1_baslik", ""), h.get("kullanim_1_metin", "")],
        [h.get("kullanim_2_baslik", ""), h.get("kullanim_2_metin", "")],
        [h.get("kullanim_3_baslik", ""), h.get("kullanim_3_metin", "")],
        [h.get("kullanim_4_baslik", ""), h.get("kullanim_4_metin", "")],
        ["", h.get("kullanim_sorumluluk", "")],
    ]

HUKUKI_KULLANIM = {
    "tr": {"baslik": H_TR.get("kullanim_baslik", "Kullanım Şartları"), "bolumler": kullanim_bolumler(H_TR)},
    "en": {"baslik": H_EN.get("kullanim_baslik", "Terms of Service"), "bolumler": kullanim_bolumler(H_EN)},
    "bg": {"baslik": H_BG.get("kullanim_baslik", "Условия за ползване"), "bolumler": kullanim_bolumler(H_BG)},
    "ro": {"baslik": H_RO.get("kullanim_baslik", "Termeni de utilizare"), "bolumler": kullanim_bolumler(H_RO)},
    "hr": {"baslik": H_HR.get("kullanim_baslik", "Uvjeti koristenja"), "bolumler": kullanim_bolumler(H_HR)},
}

html = _html_header("Kullanım Şartları") + _html_footer() + _html_js_sonu()
html = html.replace("const HUKUKI = ;", f"const HUKUKI = {json.dumps(HUKUKI_KULLANIM, ensure_ascii=False)};")

if (KOK / "kullanim.html").exists():
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(KOK / "kullanim.html", KOK / f"kullanim_i18n_oncesi_{zaman}.html.bak")

(KOK / "kullanim.html").write_text(html, encoding="utf-8")
print("[+] kullanim.html guncellendi.")

# ============================================================
# 4) DPA.HTML
# ============================================================
print()
print("=" * 60)
print("4) dpa.html")
print("=" * 60)

def dpa_bolumler(h):
    return [
        ["Özet", h.get("dpa_ozet", "")],
        [h.get("dpa_1_baslik", ""), h.get("dpa_1_metin", "")],
        [h.get("dpa_2_baslik", ""), h.get("dpa_2_metin", "")],
        [h.get("dpa_3_baslik", ""), h.get("dpa_3_metin", "")],
        [h.get("dpa_4_baslik", ""), h.get("dpa_4_metin", "")],
        ["Talep", h.get("dpa_talep", "")],
    ]

HUKUKI_DPA = {
    "tr": {"baslik": H_TR.get("dpa_baslik", "Veri İşleme Sözleşmesi"), "bolumler": dpa_bolumler(H_TR)},
    "en": {"baslik": H_EN.get("dpa_baslik", "Data Processing Agreement"), "bolumler": dpa_bolumler(H_EN)},
    "bg": {"baslik": H_BG.get("dpa_baslik", "Споразумение за обработка на данни"), "bolumler": dpa_bolumler(H_BG)},
    "ro": {"baslik": H_RO.get("dpa_baslik", "Acord de prelucrare a datelor"), "bolumler": dpa_bolumler(H_RO)},
    "hr": {"baslik": H_HR.get("dpa_baslik", "Ugovor o obradi podataka"), "bolumler": dpa_bolumler(H_HR)},
}

html = _html_header("Veri İşleme Sözleşmesi") + _html_footer() + _html_js_sonu()
html = html.replace("const HUKUKI = ;", f"const HUKUKI = {json.dumps(HUKUKI_DPA, ensure_ascii=False)};")

if (KOK / "dpa.html").exists():
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(KOK / "dpa.html", KOK / f"dpa_i18n_oncesi_{zaman}.html.bak")

(KOK / "dpa.html").write_text(html, encoding="utf-8")
print("[+] dpa.html guncellendi.")

print()
print("=" * 60)
print("TAMAM! 4 hukuki sayfa 5 dilde hazir.")
print()
print("TEST: py landing_server.py -> Ctrl+F5")
print("=" * 60)