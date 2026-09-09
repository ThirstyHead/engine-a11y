"""WCAG relative-luminance contrast math adhering strictly to W3C specifications."""
from typing import Optional, Tuple

THRESHOLD_NORMAL = 4.5  # WCAG 1.4.3 AA standard text
THRESHOLD_LARGE = 3.0   # WCAG 1.4.3 AA large text / 1.4.11 UI components


def hex_to_rgb(hexstr: str) -> Optional[Tuple[int, int, int]]:
    if hexstr is None:
        return None
    s = hexstr.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        return None
    try:
        return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
    except ValueError:
        return None


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    chans = []
    for c in rgb:
        cs = c / 255.0
        chans.append(cs / 12.92 if cs <= 0.04045 else ((cs + 0.055) / 1.055) ** 2.4)
    return 0.2126 * chans[0] + 0.7152 * chans[1] + 0.0722 * chans[2]


def contrast_ratio(fg: Tuple[int, int, int], bg: Tuple[int, int, int]) -> float:
    try:
        import wcag_contrast_ratio
        l1 = wcag_contrast_ratio.relative_luminance("#%02X%02X%02X" % fg)
        l2 = wcag_contrast_ratio.relative_luminance("#%02X%02X%02X" % bg)
        hi, lo = max(l1, l2), min(l1, l2)
        return (hi + 0.05) / (lo + 0.05)
    except Exception:
        l1, l2 = relative_luminance(fg), relative_luminance(bg)
        if l1 < l2:
            l1, l2 = l2, l1
        return (l1 + 0.05) / (l2 + 0.05)


def is_contrast_acceptable(fg_hex: str, bg_hex: str, is_large: bool = False) -> bool:
    fg = hex_to_rgb(fg_hex)
    bg = hex_to_rgb(bg_hex)
    if fg is None or bg is None:
        return False
    threshold = THRESHOLD_LARGE if is_large else THRESHOLD_NORMAL
    return contrast_ratio(fg, bg) >= threshold


def adjust_color_for_contrast(fg_hex: str, bg_hex: str, target_ratio: float = 4.5) -> str:
    fg = hex_to_rgb(fg_hex)
    bg = hex_to_rgb(bg_hex)
    if fg is None or bg is None:
        return "000000"

    current_ratio = contrast_ratio(fg, bg)
    if current_ratio >= target_ratio:
        return fg_hex.strip().lstrip("#").upper()

    bg_lum = relative_luminance(bg)

    if bg_lum >= 0.5:
        for step in range(99, -1, -1):
            factor = step / 100.0
            candidate = (int(fg[0] * factor), int(fg[1] * factor), int(fg[2] * factor))
            if contrast_ratio(candidate, bg) >= target_ratio:
                return rgb_to_hex(candidate)
        return "000000"
    else:
        for step in range(1, 101):
            factor = step / 100.0
            candidate = (
                int(fg[0] + (255 - fg[0]) * factor),
                int(fg[1] + (255 - fg[1]) * factor),
                int(fg[2] + (255 - fg[2]) * factor),
            )
            if contrast_ratio(candidate, bg) >= target_ratio:
                return rgb_to_hex(candidate)
        return "FFFFFF"
