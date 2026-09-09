"""Universal reporting system for accessibility audits."""
from .meta import SC_META, PRINCIPLES, PRINCIPLE_NAMES, POUR_INTROS, W3C_QUICKREF, W3C_UNDERSTANDING_BASE
from .stats import compute_progress_stats
from .theme import available_themes, theme_css
from .tone import assert_social_model_language
from .md import render_md
from .html import render_html
from .pdf import render_pdf

__all__ = [
    "SC_META",
    "PRINCIPLES",
    "PRINCIPLE_NAMES",
    "POUR_INTROS",
    "W3C_QUICKREF",
    "W3C_UNDERSTANDING_BASE",
    "compute_progress_stats",
    "available_themes",
    "theme_css",
    "assert_social_model_language",
    "render_md",
    "render_html",
    "render_pdf",
]
