#!/usr/bin/env python3
"""Generate the animated 3D hero used by the GitHub profile README.

The output is a GitHub-compatible GIF plus a static PNG fallback. No runtime
JavaScript or external rendering service is required.
"""
from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1200, 360
FRAME_COUNT = 48
FRAME_DURATION_MS = 85
FINAL_HOLD_MS = 2600
OUT_DIR = Path(__file__).resolve().parents[1] / "assets"

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FONT_MEDIUM = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
FONT_REGULAR = "/usr/share/fonts/opentype/inter/InterDisplay-Regular.otf"

CYAN = (103, 232, 249)
BLUE = (56, 189, 248)
VIOLET = (167, 139, 250)
GREEN = (52, 211, 153)
WHITE = (241, 245, 249)
MUTED = (148, 163, 184)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def rotate_point(point: tuple[float, float, float], ax: float, ay: float, az: float) -> tuple[float, float, float]:
    x, y, z = point

    cy, sy = math.cos(ay), math.sin(ay)
    x, z = x * cy + z * sy, -x * sy + z * cy

    cx, sx = math.cos(ax), math.sin(ax)
    y, z = y * cx - z * sx, y * sx + z * cx

    cz, sz = math.cos(az), math.sin(az)
    x, y = x * cz - y * sz, x * sz + y * cz
    return x, y, z


def project(point: tuple[float, float, float], cx: float, cy: float, scale: float, camera: float = 4.4) -> tuple[float, float, float]:
    x, y, z = point
    depth = camera - z
    factor = scale / depth
    return cx + x * factor, cy + y * factor, z


def add_radial_glow(image: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int], opacity: int) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = center
    steps = 12
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        alpha = int(opacity * ((steps - i + 1) / steps) ** 2)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(radius / 6))
    image.alpha_composite(layer)


def draw_glow_line(base: Image.Image, points: Iterable[tuple[float, float]], color: tuple[int, int, int], width: int = 2, glow: int = 9) -> None:
    pts = list(points)
    glow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.line(pts, fill=(*color, 165), width=max(2, width + 2), joint="curve")
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(glow))
    base.alpha_composite(glow_layer)
    draw = ImageDraw.Draw(base)
    draw.line(pts, fill=(*color, 235), width=width, joint="curve")


def draw_glow_circle(base: Image.Image, xy: tuple[float, float], radius: int, color: tuple[int, int, int]) -> None:
    x, y = xy
    glow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.ellipse((x - radius * 2, y - radius * 2, x + radius * 2, y + radius * 2), fill=(*color, 160))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius * 1.8))
    base.alpha_composite(glow_layer)
    draw = ImageDraw.Draw(base)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, 255), outline=(255, 255, 255, 190), width=1)


def make_background() -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    px = image.load()
    top = (3, 7, 22)
    bottom = (4, 11, 28)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        row = tuple(int(lerp(top[i], bottom[i], t)) for i in range(3))
        for x in range(WIDTH):
            # Gentle horizontal vignette.
            edge = abs((x / WIDTH) - 0.5) * 2
            dim = 1.0 - 0.18 * edge**1.6
            px[x, y] = (int(row[0] * dim), int(row[1] * dim), int(row[2] * dim), 255)
    add_radial_glow(image, (930, 150), 260, (37, 99, 235), 42)
    add_radial_glow(image, (1040, 205), 170, (139, 92, 246), 35)
    add_radial_glow(image, (300, 80), 260, (6, 182, 212), 18)
    return image


random.seed(841)
PARTICLES = [
    (
        random.uniform(0, WIDTH),
        random.uniform(0, HEIGHT),
        random.uniform(0.25, 1.2),
        random.choice([CYAN, BLUE, VIOLET, GREEN]),
        random.choice([1, 1, 1, 2]),
    )
    for _ in range(92)
]

CUBE_VERTICES = [
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
]
CUBE_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
    (0, 6), (1, 7),
]


def render_frame(index: int, base_bg: Image.Image) -> Image.Image:
    phase = index / FRAME_COUNT
    image = base_bg.copy()
    draw = ImageDraw.Draw(image)

    # Subtle animated particles.
    for px, py, speed, color, radius in PARTICLES:
        y = (py + phase * HEIGHT * speed) % HEIGHT
        x = px + math.sin(phase * math.tau + py * 0.015) * 4
        alpha = int(55 + 100 * (0.5 + 0.5 * math.sin(phase * math.tau * speed + px)))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, alpha))

    # Perspective floor grid: depth and motion without browser-side animation.
    horizon_y = 225
    vanish_x = 920
    for bottom_x in range(570, 1280, 58):
        draw.line((vanish_x, horizon_y, bottom_x, HEIGHT), fill=(67, 101, 151, 38), width=1)
    for step in range(13):
        z = (step + phase * 1.6) % 13
        t = (z / 13) ** 2.25
        y = int(horizon_y + t * (HEIGHT - horizon_y))
        alpha = int(24 + 72 * t)
        draw.line((520, y, WIDTH, y), fill=(56, 189, 248, alpha), width=1)

    # Left glass panel and accent rails.
    panel = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle((42, 40, 750, 318), radius=24, fill=(5, 12, 31, 142), outline=(103, 232, 249, 32), width=1)
    panel = panel.filter(ImageFilter.GaussianBlur(0.2))
    image.alpha_composite(panel)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((64, 58, 248, 88), radius=15, fill=(13, 29, 54, 230), outline=(*CYAN, 90), width=1)
    draw.ellipse((79, 69, 87, 77), fill=(*GREEN, 255))

    # Typography.
    f_micro = font(FONT_BOLD, 16)
    f_name = font(FONT_BLACK, 43)
    f_title = font(FONT_BLACK, 49)
    f_sub = font(FONT_MEDIUM, 19)
    f_tag = font(FONT_BOLD, 14)

    draw.text((96, 66), "AVAILABLE FOR HIGH-IMPACT BUILDS", font=f_micro, fill=(*WHITE, 235))
    draw.text((70, 110), "BRANDON RODRIGUEZ", font=f_name, fill=(*WHITE, 255))

    # Animated sheen across the primary title.
    title_pos = (70, 160)
    draw.text(title_pos, "AGENTIC AI SYSTEMS", font=f_title, fill=(112, 223, 255, 255))
    sheen_x = int(-260 + phase * 1120)
    sheen = Image.new("RGBA", image.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen)
    sd.polygon([(sheen_x, 150), (sheen_x + 64, 150), (sheen_x - 20, 224), (sheen_x - 84, 224)], fill=(255, 255, 255, 48))
    image.alpha_composite(sheen)

    draw = ImageDraw.Draw(image)
    draw.text((71, 222), "FULL-STACK ARCHITECT  •  CLOUD & AUTOMATION SPECIALIST", font=f_sub, fill=(*MUTED, 245))

    tags = [
        ("LLM AGENTS", CYAN),
        ("RAG + OCR", VIOLET),
        ("COMPUTER VISION", BLUE),
        ("CLOUD PLATFORMS", GREEN),
    ]
    x = 70
    y = 267
    for label, color in tags:
        bbox = draw.textbbox((0, 0), label, font=f_tag)
        tw = bbox[2] - bbox[0]
        draw.rounded_rectangle((x, y, x + tw + 26, y + 31), radius=8, fill=(9, 20, 42, 225), outline=(*color, 105), width=1)
        draw.text((x + 13, y + 7), label, font=f_tag, fill=(*color, 255))
        x += tw + 38

    # Rotating 3D agent cube/network.
    ax = 0.58 + math.sin(phase * math.tau) * 0.15
    ay = phase * math.tau
    az = -0.16 + math.cos(phase * math.tau) * 0.1
    rotated = [rotate_point(v, ax, ay, az) for v in CUBE_VERTICES]
    projected = [project(v, 955, 160, 360) for v in rotated]

    # Orbit rings.
    ring_points = []
    for i in range(72):
        a = (i / 72) * math.tau
        p = (1.55 * math.cos(a), 0.22 * math.sin(a * 2), 1.55 * math.sin(a))
        p = rotate_point(p, ax * 0.45, ay * 0.42, az)
        ring_points.append(project(p, 955, 160, 360)[:2])
    draw_glow_line(image, ring_points + [ring_points[0]], VIOLET, width=1, glow=7)

    # Depth-sort edges so the nearest edges are brighter.
    edge_rows = []
    for a, b in CUBE_EDGES:
        depth = (projected[a][2] + projected[b][2]) / 2
        edge_rows.append((depth, a, b))
    for depth, a, b in sorted(edge_rows):
        t = (depth + 1.8) / 3.6
        color = tuple(int(lerp(VIOLET[i], CYAN[i], max(0, min(1, t)))) for i in range(3))
        draw_glow_line(image, [projected[a][:2], projected[b][:2]], color, width=2 if depth > 0 else 1, glow=10)

    for idx, (xv, yv, zv) in enumerate(projected):
        color = [CYAN, BLUE, VIOLET, GREEN][idx % 4]
        radius = 4 if zv < 0 else 6
        draw_glow_circle(image, (xv, yv), radius, color)

    # Central inference node.
    pulse = 7 + int(3 * (0.5 + 0.5 * math.sin(phase * math.tau * 2)))
    draw_glow_circle(image, (955, 160), pulse, WHITE)

    # HUD labels around the 3D object.
    f_hud = font(FONT_MEDIUM, 13)
    hud_items = [
        (810, 58, "ORCHESTRATE", CYAN),
        (1030, 58, "REASON", VIOLET),
        (1084, 230, "AUTOMATE", GREEN),
        (810, 249, "OBSERVE", BLUE),
    ]
    for hx, hy, label, color in hud_items:
        draw.rounded_rectangle((hx, hy, hx + 93, hy + 27), radius=8, fill=(6, 14, 35, 210), outline=(*color, 70), width=1)
        draw.text((hx + 11, hy + 6), label, font=f_hud, fill=(*color, 245))

    # Scan line and footer rail.
    scan_y = int(42 + phase * 276)
    draw.line((48, scan_y, 744, scan_y), fill=(103, 232, 249, 18), width=1)
    draw.line((42, 334, 1158, 334), fill=(71, 85, 105, 65), width=1)
    f_footer = font(FONT_MEDIUM, 13)
    draw.text((48, 339), "codingace.ai", font=f_footer, fill=(*CYAN, 210))
    draw.text((965, 339), "SAN ANTONIO, TEXAS", font=f_footer, fill=(*MUTED, 190))

    return image.convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    background = make_background()
    frames = [render_frame(i, background) for i in range(FRAME_COUNT)]

    static_path = OUT_DIR / "brandon-3d-banner.png"
    gif_path = OUT_DIR / "brandon-3d-banner.gif"
    frames[0].save(static_path, optimize=True)

    # Build a consistent adaptive palette from the first frame to reduce flicker.
    palette_frame = frames[0].convert("P", palette=Image.Palette.ADAPTIVE, colors=192)
    paletted = [palette_frame]
    for frame in frames[1:]:
        paletted.append(frame.quantize(palette=palette_frame, dither=Image.Dither.FLOYDSTEINBERG))

    # Play once, then remain on the final fully rendered frame. Omitting the
    # GIF loop extension prevents the animation from restarting on GitHub.
    durations = [FRAME_DURATION_MS] * (len(paletted) - 1) + [FINAL_HOLD_MS]
    paletted[0].save(
        gif_path,
        save_all=True,
        append_images=paletted[1:],
        duration=durations,
        optimize=True,
        disposal=2,
    )

    print(f"Wrote {gif_path} ({gif_path.stat().st_size / 1024 / 1024:.2f} MiB)")
    print(f"Wrote {static_path} ({static_path.stat().st_size / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
