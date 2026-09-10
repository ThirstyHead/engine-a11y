"""Shared icon generator for a11y auditor suite."""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Tuple
from PIL import Image, ImageDraw

THEME_COLORS = {
    "pdf": (180, 40, 40, 255),    # Crimson Red
    "docx": (43, 87, 154, 255),   # Word Blue (#2B579A)
    "pptx": (208, 68, 35, 255),   # PowerPoint Orange (#D04423)
    "xlsx": (16, 124, 65, 255),   # Excel Green (#107C41)
}


def render_master_image(
    size: int = 1024,
    bg_color: Tuple[int, int, int, int] = (43, 87, 154, 255),
    symbol_text: str = "A11Y",
) -> Image.Image:
    """Render a high-resolution base master icon."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = int(size * 0.08)
    corner_radius = int(size * 0.22)
    x0, y0 = margin, margin
    x1, y1 = size - margin, size - margin

    # Draw rounded rectangle background
    draw.rounded_rectangle(
        [(x0, y0), (x1, y1)],
        radius=corner_radius,
        fill=bg_color,
        outline=(255, 255, 255, 60),
        width=int(size * 0.015),
    )

    # Inner subtle frame
    inner_pad = int(size * 0.05)
    draw.rounded_rectangle(
        [(x0 + inner_pad, y0 + inner_pad), (x1 - inner_pad, y1 - inner_pad)],
        radius=int(corner_radius * 0.8),
        outline=(255, 255, 255, 40),
        width=int(size * 0.008),
    )

    # Document fold corner top-right
    fold_size = int(size * 0.20)
    fx0, fy0 = x1 - fold_size, y0
    draw.polygon(
        [(fx0, fy0), (x1, fy0 + fold_size), (fx0, fy0 + fold_size)],
        fill=(255, 255, 255, 70),
    )

    # Accessibility 'human' emblem symbol
    center_x = size // 2
    head_y = int(size * 0.32)
    head_r = int(size * 0.08)
    draw.ellipse(
        [(center_x - head_r, head_y - head_r), (center_x + head_r, head_y + head_r)],
        fill=(255, 255, 255, 240),
    )

    # Torso & outstretched arms
    arm_y = int(size * 0.50)
    arm_span = int(size * 0.26)
    arm_thickness = int(size * 0.065)
    draw.rounded_rectangle(
        [(center_x - arm_span, arm_y - arm_thickness // 2),
         (center_x + arm_span, arm_y + arm_thickness // 2)],
        radius=arm_thickness // 2,
        fill=(255, 255, 255, 240),
    )

    # Body trunk
    body_top = arm_y
    body_bottom = int(size * 0.72)
    body_w = int(size * 0.08)
    draw.rounded_rectangle(
        [(center_x - body_w, body_top), (center_x + body_w, body_bottom)],
        radius=body_w // 2,
        fill=(255, 255, 255, 240),
    )

    # Legs
    leg_span = int(size * 0.16)
    draw.line(
        [(center_x - body_w // 2, body_bottom - int(size * 0.03)),
         (center_x - leg_span, int(size * 0.84))],
        fill=(255, 255, 255, 240),
        width=int(size * 0.065),
    )
    draw.line(
        [(center_x + body_w // 2, body_bottom - int(size * 0.03)),
         (center_x + leg_span, int(size * 0.84))],
        fill=(255, 255, 255, 240),
        width=int(size * 0.065),
    )

    return img


def generate_app_icons(
    app_name: str,
    bg_color: Tuple[int, int, int, int],
    symbol_text: str = "A11Y",
    output_dir: Path | None = None,
) -> Dict[str, Path]:
    """Generate .png, .ico, and .icns icons into target output directory."""
    if output_dir is None:
        output_dir = Path("packaging/icons")
    output_dir.mkdir(parents=True, exist_ok=True)

    master = render_master_image(size=1024, bg_color=bg_color, symbol_text=symbol_text)

    # 1. High-res PNG (256x256)
    png_path = output_dir / f"{app_name}.png"
    png_img = master.resize((256, 256), Image.Resampling.LANCZOS)
    png_img.save(png_path, format="PNG")

    # 2. Windows ICO (multi-res: 16, 32, 48, 64, 128, 256)
    ico_path = output_dir / f"{app_name}.ico"
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    master.save(ico_path, format="ICO", sizes=ico_sizes)

    # 3. macOS ICNS (via iconutil if on macOS)
    icns_path = output_dir / f"{app_name}.icns"
    generated = {"png": png_path, "ico": ico_path}

    if shutil.which("iconutil"):
        iconset_dir = output_dir / f"{app_name}.iconset"
        iconset_dir.mkdir(exist_ok=True)
        sizes = [
            ("icon_16x16.png", 16),
            ("icon_16x16@2x.png", 32),
            ("icon_32x32.png", 32),
            ("icon_32x32@2x.png", 64),
            ("icon_128x128.png", 128),
            ("icon_128x128@2x.png", 256),
            ("icon_256x256.png", 256),
            ("icon_256x256@2x.png", 512),
            ("icon_512x512.png", 512),
            ("icon_512x512@2x.png", 1024),
        ]
        for fname, dim in sizes:
            resized = master.resize((dim, dim), Image.Resampling.LANCZOS)
            resized.save(iconset_dir / fname, format="PNG")

        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(icns_path)],
            check=True,
            capture_output=True,
        )
        shutil.rmtree(iconset_dir, ignore_errors=True)
        if icns_path.exists():
            generated["icns"] = icns_path

    return generated
