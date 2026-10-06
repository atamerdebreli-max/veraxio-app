"""dogrula.html'i 5 dile cevirir."""
from pathlib import Path

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Report Verification - Veraxio</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Inter', -apple-system, sans-serif;
        background: #0a0a0a;
        color: #fafafa;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 24px;
    }
    .card {
        max-width: 520px;
        width: 100%;
        background: #171717;
        border: 1px solid #262626;
        border-radius: 16px;
        padding: 40px 32px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        position: relative;
    }
    .lang-select {
        position: absolute;
        top: 16px;
        right: 16px;
        background: #0f0f0f;
        border: 1px solid #262626;
        color: #fafafa;
        padding: 5px 8px;
        border-radius: 8px;
        font-size: 12px;
        font-family: inherit;
        cursor: pointer;
        outline: none;
    }
    .lang-select:hover { border-color: #3b82f6; }
    .logo {
        font-size: 22px;
        font-weight: 800;
        color: #fafafa;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    .logo-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 16px;
        font-weight: 800;
    }
    .success-icon {
        width: 80px;
        height: 80px;
        background: rgba(34, 197, 94, 0.15);
        border: 2px solid #22c55e;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 44px;
        margin: 0 auto 24px auto;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.3); }
        50% { box-shadow: 0 0 0 15px rgba(34, 197, 94, 0); }
    }
    h1 {
        font-size: 28px;
        font-weight: 800;
        color: #fafafa;
        margin-bottom: 12px;
        letter-spacing: -0.5px;
    }
    .subtitle {
        color: #a3a3a3;
        font-size: 15px;
        margin-bottom: 32px;
        line-height: 1.6;
    }
    .info {
        background: #0f0f0f;
        border: 1px solid #1f1f1f;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 24px;
        text-align: left;
    }
    .info-label {
        color: #737373;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .info-value {
        color: #fafafa;
        font-size: 15px;
        font-family: 'SF Mono', 'Monaco', monospace;
        word-break: break-all;
        margin-bottom: 14px;
    }
    .info-value:last-child { margin-bottom: 0; }
    .verify-badge {
        display: inline-block;
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 24px;
    }
    .footer {
        color: #525252;
        font-size: 12px;
        margin-top: 24px;
        padding-top: 24px;
        border-top: 1px solid #1f1f1f;
        line-height: 1.6;
    }
    .footer a {
        color: #60a5fa;
        text-decoration: none;
    }
    .btn {
        display: inline-block;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 12px 28px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
    }
    .btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    @media (max-width: 500px) {
        .card { padding: 32px 24px; }
        h1 { font-size: 22px; }
        .success-icon { width: 64px; height: 64px; font-size: 34px; }
    }
</style>
</head>
<body>

<div class="card">
    <select class="lang-select" id="langSelector" onchange="changeLang(this.value)">
        <option value="en">🇬🇧 EN</option>
        <option value="tr">🇹🇷 TR</option>
        <option value="bg">🇧🇬 BG</option>
        <option value="ro">🇷🇴 RO</option>
        <option value="hr">🇭🇷 HR</option>
    </select>

    <div class="logo">
        <span class="logo-icon">◆</span>
        Veraxio
    </div>

    <div class="success-icon">✓</div>

    <h1 data-i18n="title">Report Verified</h1>
    <p class="subtitle" data-i18n="subtitle">
        This report was generated by Veraxio and is protected by a blockchain timestamp.
    </p>

    <div class="verify-badge" data-i18n="badge">✓ VERIFIED REPORT</div>

    <div class="info">
        <div class="info-label" data-i18n="lbl_report">Report No</div>
        <div class="info-value" id="rapor-no">—</div>

        <div class="info-label" data-i18n="lbl_verified">Verification Date</div>
        <div class="info-value" id="dogrulama-tarih">—</div>

        <div class="info-label" data-i18n="lbl_source">Source</div>
        <div class="info-value">Veraxio Compliance Platform</div>
    </div>

    <a href="index.html" class="btn" data-i18n="back">← Back to Home</a>

    <div class="footer" data-i18n="footer">
        This page verifies that a report was generated by Veraxio.<br>
        For the full report: <a href="mailto:info@veraxio.ai">info@veraxio.ai</a>
    </div>
</div>

<script>
const I18N = {
    en: {
        title: "Report Verified",
        subtitle: "This report was generated by Veraxio and is protected by a blockchain timestamp.",
        badge: "✓ VERIFIED REPORT",
        lbl_report: "Report No",
        lbl_verified: "Verification Date",
        lbl_source: "Source",
        back: "← Back to Home",
        footer: "This page verifies that a report was generated by Veraxio.<br>For the full report: <a href='mailto:info@veraxio.ai'>info@veraxio.ai</a>",
    },
    tr: {
        title: "Rapor Doğrulandı",
        subtitle: "Bu rapor Veraxio tarafından üretilmiştir ve blockchain zaman damgası ile korunmaktadır.",
        badge: "✓ DOĞRULANMIŞ RAPOR",
        lbl_report: "Rapor No",
        lbl_verified: "Doğrulama Tarihi",
        lbl_source: "Kaynak",
        back: "← Ana Sayfaya Dön",
        footer: "Bu sayfa bir raporun Veraxio tarafından üretildiğini doğrular.<br>Detaylı rapor için: <a href='mailto:info@veraxio.ai'>info@veraxio.ai</a>",
    },
    bg: {
        title: "Докладът е потвърден",
        subtitle: "Този доклад е генериран от Veraxio и е защитен с блокчейн времеви печат.",
        badge: "✓ ПОТВЪРДЕН ДОКЛАД",
        lbl_report: "No доклад",
        lbl_verified: "Дата на потвърждение",
        lbl_source: "Източник",
        back: "← Обратно към началото",
        footer: "Тази страница потвърждава, че докладът е генериран от Veraxio.<br>За пълен доклад: <a href='mailto:info@veraxio.ai'>info@veraxio.ai</a>",
    },
    ro: {
        title: "Raport verificat",
        subtitle: "Acest raport a fost generat de Veraxio și este protejat de o marcă temporală blockchain.",
        badge: "✓ RAPORT VERIFICAT",
        lbl_report: "Nr. raport",
        lbl_verified: "Data verificarii",
        lbl_source: "Sursa",
        back: "← Inapoi la inceput",
        footer: "Aceasta pagina verifica faptul ca un raport a fost generat de Veraxio.<br>Pentru raportul complet: <a href='mailto:info@veraxio.ai'>info@veraxio.ai</a>",
    },
    hr: {
        title: "Izvjesce potvrdeno",
        subtitle: "Ovo izvjesce generirao je Veraxio i zasticeno je blockchain vremenskim zigom.",
        badge: "✓ POTVRDENO IZVJESCE",
        lbl_report: "Br. izvjesca",
        lbl_verified: "Datum potvrde",
        lbl_source: "Izvor",
        back: "← Natrag na pocetnu",
        footer: "Ova stranica potvrduje da je izvjesce generirao Veraxio.<br>Za potpuno izvjesce: <a href='mailto:info@veraxio.ai'>info@veraxio.ai</a>",
    },
};

// Aktif dil - default ENGLISH
let currentLang = localStorage.getItem("veraxio_lang") || "en";

function changeLang(lang) {
    currentLang = lang;
    localStorage.setItem("veraxio_lang", lang);
    applyLang(lang);
}

function applyLang(lang) {
    const t = I18N[lang] || I18N.en;
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (t[key]) el.innerHTML = t[key];
    });
    document.documentElement.lang = lang;
    document.title = t.title + " - Veraxio";
    const sel = document.getElementById("langSelector");
    if (sel) sel.value = lang;

    // Tarihi yeniden formatla
    formatDate(lang);
}

function formatDate(lang) {
    const LOCALES = { tr: "tr-TR", en: "en-US", bg: "bg-BG", ro: "ro-RO", hr: "hr-HR" };
    const tarih = new Date();
    const formatliTarih = tarih.toLocaleDateString(LOCALES[lang] || "en-US", {
        year: "numeric", month: "long", day: "numeric",
        hour: "2-digit", minute: "2-digit"
    });
    const el = document.getElementById("dogrulama-tarih");
    if (el) el.textContent = formatliTarih;
}

// Rapor no URL'den al
const params = new URLSearchParams(window.location.search);
let raporNo = params.get("rapor");
if (!raporNo) {
    const pathParts = window.location.pathname.split("/");
    raporNo = pathParts[pathParts.length - 1] || "UNKNOWN";
}
document.getElementById("rapor-no").textContent = decodeURIComponent(raporNo);

document.addEventListener("DOMContentLoaded", () => {
    const sel = document.getElementById("langSelector");
    if (sel) sel.value = currentLang;
    applyLang(currentLang);
});
</script>

</body>
</html>
'''

Path("dogrula.html").write_text(HTML, encoding="utf-8")
print("[+] dogrula.html 5 dile cevrildi.")
print("[i] Default dil: EN (AB uyumu)")