"""
Generates Peak app icons — minimalist Mount Fuji with brand "P".
Outputs: apple-touch-icon.png (180), icon-192.png (192), icon-512.png (512)
"""
from PIL import Image, ImageDraw, ImageFont


def cubic_pts(p0, p1, p2, p3, steps=100):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1 - t
        x = mt**3*p0[0] + 3*mt**2*t*p1[0] + 3*mt*t**2*p2[0] + t**3*p3[0]
        y = mt**3*p0[1] + 3*mt**2*t*p1[1] + 3*mt*t**2*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts


def quad_pts(p0, p1, p2, steps=40):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1 - t
        x = mt**2*p0[0] + 2*mt*t*p1[0] + t**2*p2[0]
        y = mt**2*p0[1] + 2*mt*t*p1[1] + t**2*p2[1]
        pts.append((x, y))
    return pts


def generate(output_size):
    # Draw at 2× for antialiasing, then downscale
    D = output_size * 2
    S = D / 512

    img = Image.new("RGB", (D, D), (7, 7, 15))
    draw = ImageDraw.Draw(img)

    def sc(pts):
        return [(x * S, y * S) for x, y in pts]

    # ── Mountain silhouette ──────────────────────────────────────────────────
    # Classic Fuji: steep upper slope, broad flaring apron at the base
    PEAK = (256, 128)
    left  = cubic_pts(PEAK, (228, 186), (142, 358), (0, 468))
    right = cubic_pts(PEAK, (284, 186), (370, 358), (512, 468))

    mountain = (
        sc(left)
        + [(0, D), (D, D)]
        + sc(list(reversed(right)))
    )
    draw.polygon(mountain, fill=(20, 20, 44))

    # ── Snow cap ─────────────────────────────────────────────────────────────
    # Take the first 27% of each slope (approx y ≈ 196)
    N = 27
    l_snow = left[:N + 1]
    r_snow = right[:N + 1]

    sl, sr = l_snow[-1], r_snow[-1]
    base = quad_pts(sl, ((sl[0] + sr[0]) / 2, sl[1] + 10), sr, steps=40)

    # Upper snow: bright near-white
    snow_poly = sc(l_snow) + sc(base) + sc(list(reversed(r_snow)))
    draw.polygon(snow_poly, fill=(237, 242, 252))

    # Lower snow: blue-grey shadow for depth
    shade_start = N // 2
    shade = (
        sc(l_snow[shade_start:])
        + sc(base)
        + sc(list(reversed(r_snow[shade_start:])))
    )
    draw.polygon(shade, fill=(195, 210, 235))

    # ── "P" brand mark ───────────────────────────────────────────────────────
    peak_y  = PEAK[1] * S
    snow_y  = l_snow[-1][1] * S
    center_x = 256 * S
    center_y = (peak_y + snow_y) / 2

    font_size = int(46 * S)
    font = None
    for path, idx in [
        ("/System/Library/Fonts/HelveticaNeue.ttc", 1),   # Helvetica Neue Bold
        ("/System/Library/Fonts/HelveticaNeue.ttc", 0),
    ]:
        try:
            font = ImageFont.truetype(path, font_size, index=idx)
            break
        except Exception:
            pass
    if font is None:
        font = ImageFont.load_default()

    draw.text((center_x, center_y), "P", font=font, fill=(0, 220, 130), anchor="mm")

    # Downscale for clean antialiasing
    return img.resize((output_size, output_size), Image.LANCZOS)


if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    for name, size in [
        ("apple-touch-icon.png", 180),
        ("icon-192.png", 192),
        ("icon-512.png", 512),
    ]:
        path = os.path.join(base, name)
        generate(size).save(path)
        print(f"  ✓  {name}  ({size}×{size})")
    print("Done.")
