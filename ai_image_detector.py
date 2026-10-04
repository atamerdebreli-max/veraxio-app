"""
ai_image_detector.py - Genel AI gorsel tespit modulu
Model: wkaandemir/ai-image-detector (CLIP ViT-B/16 + LoRA)
Dogruluk: %95.9
Belirsizlik bandi: 0.91 - 0.93
"""

from PIL import Image  # LAZY_IMPORT_FIX

_MODEL_ID = "wkaandemir/ai-image-detector"
_model = None
_tfm = None


def _model_yukle():
    """Model ve transform'u ilk kullanimda yukler (lazy loading)."""
    global _model, _tfm
    if _model is None:
        # Agir importlari buraya tasidik
        import torch
        from safetensors.torch import load_file
        import timm
        from torchvision import transforms
        from huggingface_hub import hf_hub_download
        # 1. Agirliklari indir ve yukle
        weights_path = hf_hub_download(
            repo_id=_MODEL_ID,
            filename="model.safetensors"
        )
        state = load_file(weights_path)

        # 2. Mimariyi kur ve agirliklari yukle
        model = timm.create_model(
            "vit_base_patch16_clip_224.openai",
            pretrained=False,
            num_classes=1,
            img_size=256
        )
        model.load_state_dict(state, strict=False)
        model.eval()

        # 3. On-isleme (256x256, CLIP normalizasyonu)
        tfm = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.481, 0.458, 0.408],
                std=[0.269, 0.261, 0.276]
            ),
        ])

        _model = model
        _tfm = tfm

    return _model, _tfm


def ai_image_tespit_et(gorsel_yolu):
    """
    Gorseli genel AI gorsel tespiti modeli ile analiz eder.
    Model p(real) skoru uretir: 0 = fake, 1 = real.

    Karar esikleri:
      - p(real) < 0.91  -> YAPAY (fake)
      - p(real) >= 0.93 -> GERCEK (real)
      - 0.91 <= p(real) < 0.93 -> BELIRSIZ (uncertain)

    Returns:
        dict: {
            "durum": "YAPAY" | "GERCEK" | "BELIRSIZ" | "HATA",
            "p_real": float,
            "p_fake": float,
            "model": str
        }
    """
    try:
        model, tfm = _model_yukle()
        image = Image.open(gorsel_yolu).convert("RGB")
        tensor = tfm(image).unsqueeze(0)

        with torch.no_grad():
            logit = model(tensor).squeeze()
            # Model tek skor uretiyor (sigmoid oncesi logit)
            # Temperature-scaled sigmoid (T=0.595)
            T = 0.595
            p_real = torch.sigmoid(logit / T).item()

        # Karar esikleri
        if p_real < 0.91:
            durum = "YAPAY"
        elif p_real >= 0.93:
            durum = "GERCEK"
        else:
            durum = "BELIRSIZ"

        return {
            "durum": durum,
            "p_real": round(p_real, 4),
            "p_fake": round(1 - p_real, 4),
            "model": "wkaandemir/ai-image-detector",
        }
    except Exception as e:
        return {
            "durum": "HATA",
            "hata": str(e)[:100],
            "model": "wkaandemir/ai-image-detector",
        }