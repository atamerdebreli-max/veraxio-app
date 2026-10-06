"""
dogrula.html sayfasi olusturur - QR tarama sonucu.
- URL'den rapor_no alir
- Guzel bir dogrulama sayfasi gosterir
"""
from pathlib import Path

HTML = '''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rapor Doğrulama - Veraxio</title>
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
    }
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
    <div class="logo">
        <span class="logo-icon">◆</span>
        Veraxio
    </div>

    <div class="success-icon">✓</div>

    <h1>Rapor Doğrulandı</h1>
    <p class="subtitle">
        Bu rapor Veraxio tarafından üretilmiştir ve blockchain zaman damgası ile korunmaktadır.
    </p>

    <div class="verify-badge">✓ DOĞRULANMIŞ RAPOR</div>

    <div class="info">
        <div class="info-label">Rapor No</div>
        <div class="info-value" id="rapor-no">—</div>

        <div class="info-label">Doğrulama Tarihi</div>
        <div class="info-value" id="dogrulama-tarih">—</div>

        <div class="info-label">Kaynak</div>
        <div class="info-value">Veraxio Compliance Platform</div>
    </div>

    <a href="index.html" class="btn">← Ana Sayfaya Dön</a>

    <div class="footer">
        Bu sayfa bir raporun Veraxio tarafından üretildiğini doğrular.<br>
        Detaylı rapor için: <a href="mailto:info@veraxio.ai">info@veraxio.ai</a>
    </div>
</div>

<script>
// URL'den rapor no al
const pathParts = window.location.pathname.split("/");
const raporNo = pathParts[pathParts.length - 1] || pathParts[pathParts.length - 2] || "BILINMIYOR";

document.getElementById("rapor-no").textContent = decodeURIComponent(raporNo);

const tarih = new Date();
const formatliTarih = tarih.toLocaleDateString("tr-TR", {
    year: "numeric", month: "long", day: "numeric",
    hour: "2-digit", minute: "2-digit"
});
document.getElementById("dogrulama-tarih").textContent = formatliTarih;
</script>

</body>
</html>
'''

HEDEF = Path("dogrula.html")
HEDEF.write_text(HTML, encoding="utf-8")
print("[+] dogrula.html olusturuldu.")
print(f"[i] Boyut: {len(HTML)} karakter")