"""
deepfake_detector.py - SigLIP tabanli deepfake tespit modulu
Model: prithivMLmods/deepfake-detector-model-v1
Dogruluk: %94.4
"""

from PIL import Image  # LAZY_IMPORT_FIX

_MODEL_NAME = "prithivMLmods/deepfake-detector-model-v1"
_model = None
_processor = None


def _model_yukle():
    """Model ve processor'u ilk kullanimda yukler (lazy loading)."""
    global _model, _processor
    if _model is None:
        # Agir importlari buraya tasidik - sayfa acilisinda yuklenmesin
        from transformers import AutoImageProcessor, SiglipForImageClassification
        import torch  # noqa
        _model = SiglipForImageClassification.from_pretrained(_MODEL_NAME)
        _processor = AutoImageProcessor.from_pretrained(_MODEL_NAME)
    return _model, _processor


def deepfake_tespit_et(gorsel_yolu):
    """
    Gorseli deepfake modeli ile analiz eder.
    Returns:
        dict: {
            "durum": "DEEPFAKE" | "GERCEK" | "HATA",
            "fake_olasilik": float,
            "gercek_olasilik": float,
            "model": str
        }
    """
    try:
        model, processor = _model_yukle()
        image = Image.open(gorsel_yolu).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1).squeeze().tolist()

        fake_olasilik = probs[0]
        gercek_olasilik = probs[1]

        return {
            "durum": "DEEPFAKE" if fake_olasilik > 0.5 else "GERCEK",
            "fake_olasilik": round(fake_olasilik, 3),
            "gercek_olasilik": round(gercek_olasilik, 3),
            "model": "prithivMLmods/deepfake-detector-model-v1",
        }
    except Exception as e:
        return {
            "durum": "HATA",
            "hata": str(e)[:100],
            "model": "prithivMLmods/deepfake-detector-model-v1",
        }