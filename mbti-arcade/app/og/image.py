from __future__ import annotations

import zlib
from typing import Iterable, Sequence, Tuple

from .font import FONT_5X7

Color = Tuple[int, int, int, int]


class Canvas:
    def __init__(
        self,
        width: int,
        height: int,
        bg: Color | None = None,
        *,
        rows: Sequence[bytes] | None = None,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Canvas dimensions must be positive")
        self.width = width
        self.height = height
        if rows is not None:
            if len(rows) != height:
                raise ValueError("Row template height mismatch")
            self.rows = [bytearray(row) for row in rows]
        else:
            if bg is None:
                raise ValueError("Background color required when rows not provided")
            self.rows = [bytearray(bg * width) for _ in range(height)]

    def set_pixel(self, x: int, y: int, color: Color) -> None:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        row = self.rows[y]
        idx = x * 4
        row[idx : idx + 4] = bytes(color)

    def fill_rect(self, x: int, y: int, w: int, h: int, color: Color) -> None:
        for yy in range(y, y + h):
            if yy < 0 or yy >= self.height:
                continue
            row = self.rows[yy]
            start = max(x, 0)
            end = min(x + w, self.width)
            for xx in range(start, end):
                idx = xx * 4
                row[idx : idx + 4] = bytes(color)

    def draw_text(self, x: int, y: int, text: str, color: Color, scale: int = 2, spacing: int = 1) -> None:
        cursor_x = x
        upper_text = text.upper()
        for char in upper_text:
            glyph = FONT_5X7.get(char)
            if glyph is None:
                cursor_x += (5 * scale) + spacing * scale
                continue
            self._draw_glyph(cursor_x, y, glyph, color, scale)
            cursor_x += (len(glyph[0]) * scale) + spacing * scale

    def _draw_glyph(self, x: int, y: int, glyph: Iterable[str], color: Color, scale: int) -> None:
        for gy, line in enumerate(glyph):
            for gx, ch in enumerate(line):
                if ch != "#":
                    continue
                for sy in range(scale):
                    for sx in range(scale):
                        self.set_pixel(x + gx * scale + sx, y + gy * scale + sy, color)

    def to_png(self) -> bytes:
        raw = b"".join(b"\x00" + bytes(row) for row in self.rows)
        compressor = zlib.compressobj()
        compressed = compressor.compress(raw) + compressor.flush()

        def chunk(chunk_type: bytes, data: bytes) -> bytes:
            length = len(data).to_bytes(4, "big")
            crc = zlib.crc32(chunk_type + data).to_bytes(4, "big")
            return length + chunk_type + data + crc

        ihdr = (
            self.width.to_bytes(4, "big")
            + self.height.to_bytes(4, "big")
            + bytes([8, 6, 0, 0, 0])
        )
        png = [b"\x89PNG\r\n\x1a\n", chunk(b"IHDR", ihdr), chunk(b"IDAT", compressed), chunk(b"IEND", b"")]
        return b"".join(png)

    def clone(self) -> "Canvas":
        return Canvas(self.width, self.height, rows=self.rows)
