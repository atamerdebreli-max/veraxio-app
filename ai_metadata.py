"""
ai_metadata.py - Detect EXPLICIT AI-provenance metadata in image bytes.

Looks for:
  1. IPTC DigitalSourceType "trainedAlgorithmicMedia" (C2PA manifests)
  2. Generator-specific PNG text chunks: Stable Diffusion, ComfyUI, InvokeAI
  3. Known AI tool names inside metadata segments

Pure stdlib, no dependencies.
"""


# Definitive IPTC/C2PA declaration of GENERATIVE-AI origin
_DEFINITIVE_MARKERS = (
    b"trainedalgorithmicmedia",
    b"compositesynthetic",
)

# PNG text-chunk keywords written by specific generators
_PNG_AI_KEYS = {
    b"parameters",          # Stable Diffusion WebUI (A1111/Forge)
    b"sd-metadata",         # InvokeAI (older)
    b"invokeai_metadata",   # InvokeAI (newer)
}

# ComfyUI writes BOTH of these keys
_PNG_COMFY_KEYS = (b"prompt", b"workflow")

# Known tool names - only searched inside metadata segments
_TOOL_MARKERS = (
    (b"midjourney", "Midjourney"),
    (b"stable diffusion", "Stable Diffusion"),
    (b"novelai", "NovelAI"),
    (b"comfyui", "ComfyUI"),
    (b"invokeai", "InvokeAI"),
    (b"adobe firefly", "Adobe Firefly"),
    (b"dall-e", "DALL-E"),
    (b"dall\xc2\xb7e", "DALL-E"),
    (b"bing image creator", "Bing Image Creator"),
    (b"leonardo.ai", "Leonardo.Ai"),
    (b"ideogram.ai", "Ideogram"),
    (b"recraft.ai", "Recraft"),
)


def _collect_metadata(data: bytes):
    """Extract metadata segments and PNG text chunks from raw bytes."""
    metadata_blob = b""
    png_keys = set()
    c2pa_present = False

    # Collect metadata segments
    if b"<x:xmpmeta" in data or b"<rdf:RDF" in data:
        metadata_blob += data
    if b"c2pa" in data.lower() or b"contentcredentials" in data.lower():
        c2pa_present = True
        metadata_blob += data

    # PNG text chunks
    if data.startswith(b"\x89PNG"):
        pos = 8
        while pos < len(data) - 8:
            length = int.from_bytes(data[pos:pos+4], "big")
            ctype = data[pos+4:pos+8]
            if ctype in (b"tEXt", b"iTXt", b"zTXt"):
                chunk_data = data[pos+8:pos+8+length]
                keyword = chunk_data.split(b"\x00", 1)[0]
                png_keys.add(keyword.lower())
            pos += 12 + length
            if ctype == b"IEND":
                break

    return metadata_blob, png_keys, c2pa_present


def detect_ai_metadata(data: bytes) -> dict:
    """Inspect raw image bytes for explicit AI-provenance metadata."""
    result = {"ai_declared": False, "source": None, "c2pa_present": False}
    if not data or len(data) < 12:
        return result

    try:
        blob, png_keys, c2pa_present = _collect_metadata(data)
    except Exception:
        return result

    result["c2pa_present"] = c2pa_present

    # 1) Definitive IPTC/C2PA declaration
    for marker in _DEFINITIVE_MARKERS:
        if marker in blob.lower():
            result["ai_declared"] = True
            result["source"] = "C2PA/IPTC (trainedAlgorithmicMedia)"
            return result

    # 2) Generator-specific PNG keys
    for key in _PNG_AI_KEYS:
        if key in png_keys:
            result["ai_declared"] = True
            result["source"] = f"PNG metadata: {key.decode()}"
            return result

    # 3) ComfyUI (both keys required)
    if all(k in png_keys for k in _PNG_COMFY_KEYS):
        result["ai_declared"] = True
        result["source"] = "ComfyUI (PNG workflow)"
        return result

    # 4) Known tool names inside metadata
    for marker, name in _TOOL_MARKERS:
        if marker in blob.lower():
            result["ai_declared"] = True
            result["source"] = f"Metadata: {name}"
            return result

    return result