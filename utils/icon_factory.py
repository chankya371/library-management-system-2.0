import math
from typing import Dict, Tuple
from PIL import Image, ImageDraw
import customtkinter as ctk


class IconFactory:
    """
    Generates crisp, anti-aliased vector-style modern icons using PIL drawing.
    Produces CTkImage instances compatible with both Light and Dark modes.
    """
    _cache: Dict[str, ctk.CTkImage] = {}

    @classmethod
    def get_icon(cls, name: str, size: Tuple[int, int] = (20, 20), color_light: str = "#334155", color_dark: str = "#94a3b8") -> ctk.CTkImage:
        cache_key = f"{name}_{size[0]}x{size[1]}_{color_light}_{color_dark}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        img_light = cls._render_icon(name, 64, color_light)
        img_dark = cls._render_icon(name, 64, color_dark)

        ctk_img = ctk.CTkImage(light_image=img_light, dark_image=img_dark, size=size)
        cls._cache[cache_key] = ctk_img
        return ctk_img

    @classmethod
    def _render_icon(cls, name: str, canvas_size: int, color: str) -> Image.Image:
        # Render on high-res canvas (128x128) then downsample for super-smooth anti-aliased lines
        scale = 2
        dim = canvas_size * scale
        img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        w = int(2.5 * scale)

        c = (dim // 2, dim // 2)

        if name == "dashboard":
            # 4 grid rounded rects
            pad = int(14 * scale)
            b = int(22 * scale)
            draw.rounded_rectangle([pad, pad, pad + b, pad + b], radius=int(4 * scale), outline=color, width=w)
            draw.rounded_rectangle([dim - pad - b, pad, dim - pad, pad + b], radius=int(4 * scale), outline=color, width=w)
            draw.rounded_rectangle([pad, dim - pad - b, pad + b, dim - pad], radius=int(4 * scale), outline=color, width=w)
            draw.rounded_rectangle([dim - pad - b, dim - pad - b, dim - pad, dim - pad], radius=int(4 * scale), outline=color, width=w)

        elif name == "books":
            # Book spine / open book
            pad_x = int(14 * scale)
            pad_y = int(18 * scale)
            draw.rounded_rectangle([pad_x, pad_y, dim - pad_x, dim - pad_y], radius=int(4 * scale), outline=color, width=w)
            # Spine line
            draw.line([(pad_x + int(12 * scale), pad_y), (pad_x + int(12 * scale), dim - pad_y)], fill=color, width=w)
            # Page lines
            draw.line([(pad_x + int(20 * scale), pad_y + int(12 * scale)), (dim - pad_x - int(8 * scale), pad_y + int(12 * scale))], fill=color, width=w)
            draw.line([(pad_x + int(20 * scale), pad_y + int(20 * scale)), (dim - pad_x - int(8 * scale), pad_y + int(20 * scale))], fill=color, width=w)

        elif name == "members":
            # User profile / silhouette
            head_r = int(11 * scale)
            draw.ellipse([c[0] - head_r, int(16 * scale), c[0] + head_r, int(16 * scale) + head_r * 2], outline=color, width=w)
            # Shoulders arc
            draw.arc([int(15 * scale), int(34 * scale), dim - int(15 * scale), dim + int(10 * scale)], start=190, end=350, fill=color, width=w)

        elif name == "circulation":
            # Two cycling arrows
            pad = int(18 * scale)
            draw.arc([pad, pad, dim - pad, dim - pad], start=45, end=200, fill=color, width=w)
            draw.arc([pad, pad, dim - pad, dim - pad], start=225, end=380, fill=color, width=w)
            # Arrow heads
            draw.polygon([(dim - pad - int(2 * scale), c[1] - int(6 * scale)), (dim - pad + int(8 * scale), c[1] + int(2 * scale)), (dim - pad - int(6 * scale), c[1] + int(4 * scale))], fill=color)
            draw.polygon([(pad + int(2 * scale), c[1] + int(6 * scale)), (pad - int(8 * scale), c[1] - int(2 * scale)), (pad + int(6 * scale), c[1] - int(4 * scale))], fill=color)

        elif name == "fines":
            # Currency circle with dollar/coin symbol
            r = int(24 * scale)
            draw.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=color, width=w)
            # '$' or fine balance symbol
            draw.line([(c[0], c[1] - int(14 * scale)), (c[0], c[1] + int(14 * scale))], fill=color, width=w)
            draw.arc([c[0] - int(7 * scale), c[1] - int(10 * scale), c[0] + int(7 * scale), c[1] + int(1 * scale)], start=90, end=270, fill=color, width=w)
            draw.arc([c[0] - int(7 * scale), c[1] - int(1 * scale), c[0] + int(7 * scale), c[1] + int(10 * scale)], start=270, end=90, fill=color, width=w)

        elif name == "reports":
            # Bar chart
            pad = int(16 * scale)
            draw.line([(pad, dim - pad), (dim - pad, dim - pad)], fill=color, width=w)  # base
            # Bars
            b_w = int(7 * scale)
            h1 = int(16 * scale)
            h2 = int(28 * scale)
            h3 = int(22 * scale)
            draw.rectangle([pad + int(6 * scale), dim - pad - h1, pad + int(6 * scale) + b_w, dim - pad], fill=color)
            draw.rectangle([pad + int(16 * scale), dim - pad - h2, pad + int(16 * scale) + b_w, dim - pad], fill=color)
            draw.rectangle([pad + int(26 * scale), dim - pad - h3, pad + int(26 * scale) + b_w, dim - pad], fill=color)

        elif name == "settings":
            # Modern gear cog
            r_out = int(22 * scale)
            r_in = int(10 * scale)
            draw.ellipse([c[0] - r_in, c[1] - r_in, c[0] + r_in, c[1] + r_in], outline=color, width=w)
            for i in range(6):
                ang = i * (math.pi / 3)
                x1 = c[0] + int((r_in + int(2 * scale)) * math.cos(ang))
                y1 = c[1] + int((r_in + int(2 * scale)) * math.sin(ang))
                x2 = c[0] + int(r_out * math.cos(ang))
                y2 = c[1] + int(r_out * math.sin(ang))
                draw.line([(x1, y1), (x2, y2)], fill=color, width=w + int(2 * scale))

        elif name == "search":
            # Magnifying glass
            r = int(14 * scale)
            ox = int(26 * scale)
            oy = int(26 * scale)
            draw.ellipse([ox - r, oy - r, ox + r, oy + r], outline=color, width=w)
            draw.line([(ox + int(10 * scale), oy + int(10 * scale)), (dim - int(16 * scale), dim - int(16 * scale))], fill=color, width=w + int(2 * scale))

        elif name == "plus":
            # Add icon
            pad = int(18 * scale)
            draw.line([(c[0], pad), (c[0], dim - pad)], fill=color, width=w)
            draw.line([(pad, c[1]), (dim - pad, c[1])], fill=color, width=w)

        elif name == "edit":
            # Pencil / edit
            draw.line([(int(18 * scale), dim - int(18 * scale)), (dim - int(22 * scale), int(22 * scale))], fill=color, width=w + int(1 * scale))
            draw.line([(dim - int(22 * scale), int(22 * scale)), (dim - int(16 * scale), int(28 * scale))], fill=color, width=w)
            draw.line([(int(18 * scale), dim - int(18 * scale)), (int(16 * scale), dim - int(24 * scale))], fill=color, width=w)

        elif name == "trash":
            # Trash bin
            pad_x = int(18 * scale)
            # Lid
            draw.line([(pad_x - int(4 * scale), int(20 * scale)), (dim - pad_x + int(4 * scale), int(20 * scale))], fill=color, width=w)
            draw.rectangle([c[0] - int(6 * scale), int(15 * scale), c[0] + int(6 * scale), int(20 * scale)], outline=color, width=w)
            # Can
            draw.rounded_rectangle([pad_x, int(22 * scale), dim - pad_x, dim - int(16 * scale)], radius=int(3 * scale), outline=color, width=w)
            # Slits
            draw.line([(c[0] - int(5 * scale), int(28 * scale)), (c[0] - int(5 * scale), dim - int(22 * scale))], fill=color, width=w)
            draw.line([(c[0] + int(5 * scale), int(28 * scale)), (c[0] + int(5 * scale), dim - int(22 * scale))], fill=color, width=w)

        elif name == "check":
            # Checkmark
            pts = [(int(18 * scale), c[1]), (int(26 * scale), c[1] + int(9 * scale)), (dim - int(18 * scale), c[1] - int(11 * scale))]
            draw.line(pts, fill=color, width=w + int(1 * scale), joint="curve")

        elif name == "alert":
            # Warning triangle
            pts = [(c[0], int(15 * scale)), (dim - int(14 * scale), dim - int(16 * scale)), (int(14 * scale), dim - int(16 * scale))]
            draw.polygon(pts, outline=color, width=w)
            draw.line([(c[0], int(26 * scale)), (c[0], int(36 * scale))], fill=color, width=w)
            draw.point([(c[0], int(41 * scale))], fill=color)

        elif name == "logout":
            # Door & exit arrow
            pad = int(16 * scale)
            draw.line([(pad + int(8 * scale), pad), (pad, pad), (pad, dim - pad), (pad + int(8 * scale), dim - pad)], fill=color, width=w)
            draw.line([(c[0], c[1]), (dim - pad, c[1])], fill=color, width=w)
            draw.polygon([(dim - pad - int(4 * scale), c[1] - int(5 * scale)), (dim - pad + int(4 * scale), c[1]), (dim - pad - int(4 * scale), c[1] + int(5 * scale))], fill=color)

        elif name == "download":
            # Download arrow
            pad = int(18 * scale)
            draw.line([(c[0], pad), (c[0], dim - pad - int(6 * scale))], fill=color, width=w)
            draw.polygon([(c[0] - int(7 * scale), dim - pad - int(8 * scale)), (c[0] + int(7 * scale), dim - pad - int(8 * scale)), (c[0], dim - pad + int(1 * scale))], fill=color)
            draw.line([(pad, dim - pad + int(4 * scale)), (dim - pad, dim - pad + int(4 * scale))], fill=color, width=w)

        elif name == "lock":
            # Padlock
            pad = int(18 * scale)
            draw.rounded_rectangle([pad, c[1] - int(4 * scale), dim - pad, dim - pad], radius=int(4 * scale), outline=color, width=w)
            draw.arc([c[0] - int(10 * scale), int(14 * scale), c[0] + int(10 * scale), c[1] + int(6 * scale)], start=180, end=360, fill=color, width=w)
            draw.ellipse([c[0] - int(3 * scale), c[1] + int(5 * scale), c[0] + int(3 * scale), c[1] + int(11 * scale)], fill=color)

        else:
            # Generic circle fallback
            draw.ellipse([int(18 * scale), int(18 * scale), dim - int(18 * scale), dim - int(18 * scale)], outline=color, width=w)

        # Downsample cleanly to canvas_size
        return img.resize((canvas_size, canvas_size), Image.Resampling.LANCZOS)
