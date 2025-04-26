import re


def get_img_id_by_public_url(url: str) -> str | None:
    allowed_extensions = ["jpg", "jpeg", "png", "gif", "webp", "bmp", "tiff", "svg"]
    extensions_pattern = "|".join(allowed_extensions)

    pattern = rf'/([^/]+)\.({extensions_pattern})$'
    match = re.search(pattern, url, re.IGNORECASE)
    if match:
        return match.group(1)
    return None