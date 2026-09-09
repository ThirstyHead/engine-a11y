"""Canonical W3C WCAG 2.1 / 2.2 metadata, Understanding URLs, and POUR taxonomy."""
from typing import Dict, Tuple
from ..profile import WCAG_CATALOG, W3C_UNDERSTANDING

W3C_UNDERSTANDING_BASE = W3C_UNDERSTANDING
W3C_QUICKREF = "https://www.w3.org/WAI/WCAG21/quickref/?currentsidebar=%23col_customize&levels=aaa"

PRINCIPLES = [
    ("1", "Perceivable"),
    ("2", "Operable"),
    ("3", "Understandable"),
    ("4", "Robust"),
]

PRINCIPLE_NAMES = dict(PRINCIPLES)

POUR_INTROS = {
    "1": (
        "Perceivable content ensures that information and document components can be received by everyone's "
        "senses. Visuals have text descriptions, colors provide high contrast, and structural elements "
        "are explicitly styled so assistive technologies can read them."
    ),
    "2": (
        "Operable documents let every reader navigate with ease: clear document titles serve as landmarks, "
        "a consistent heading hierarchy allows predictable outline exploration, and hyperlinks "
        "clearly state where they lead."
    ),
    "3": (
        "Understandable material is clear and predictable: the document declares its natural language so "
        "speech synthesizers pronounce terms correctly, and layout choices avoid unexpected behavior."
    ),
    "4": (
        "Robust documents use standard structured accessibility elements "
        "so content can be reliably interpreted across operating systems, assistive tech, and screen readers."
    ),
}

# Exhaustive SC_META mapping derived from authoritative WCAG_CATALOG
SC_META: Dict[str, Tuple[str, str, str, str]] = {}
for sc, meta in WCAG_CATALOG.items():
    p_num = meta["principle"]
    p_name = PRINCIPLE_NAMES.get(p_num, "")
    principle_str = f"{p_num} {p_name}".strip()
    url = f"{W3C_UNDERSTANDING_BASE}{meta['slug']}.html"
    SC_META[sc] = (meta["title"], meta["level"], principle_str, url)
