"""
Cadre photo ICAO (modèle 35×45 mm, ratio 7:9).

- Tête + haut des épaules visibles
- Hauteur visage (sommet du crâne → menton) = 70–80 % de la hauteur du cadre (cible 75 %)
- Marges : léger espace au-dessus des cheveux, épaules en bas (comme photo de référence)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ICAO_RATIO_W = 7
ICAO_RATIO_H = 9

# Norme : visage occupe 70–80 % de la hauteur de la photo
FACE_HEIGHT_TARGET = 0.75
FACE_HEIGHT_MIN = 0.70
FACE_HEIGHT_MAX = 0.80

# Sommet du crâne au-dessus du landmark front (MediaPipe)
# Ajusté pour une marge haute cheveux plus visible.
CROWN_ABOVE_FOREHEAD = 0.18

# Répartition de la marge hors-visage (haut : cheveux + air ; bas : épaules)
# On augmente légèrement la part haute sans dégrader les épaules.
MARGIN_TOP_SHARE = 0.44
MARGIN_BOTTOM_SHARE = 0.56

_LEFT_EYE_IDX = 33
_RIGHT_EYE_IDX = 263
_FOREHEAD_IDX = 10
_CHIN_IDX = 152


@dataclass(frozen=True)
class IcaoFramingBox:
    """Cadre en coordonnées normalisées 0–1 (x, y)."""

    x: float
    y: float
    width: float
    height: float
    crown_y: float
    chin_y: float
    face_height: float
    face_height_ratio: float

    def as_crop_dict(self) -> dict[str, float | str]:
        return {
            "x": round(self.x, 4),
            "y": round(self.y, 4),
            "width": round(self.width, 4),
            "height": round(self.height, 4),
            "ratio": f"{ICAO_RATIO_W}:{ICAO_RATIO_H}",
            "faceHeightPercent": round(self.face_height_ratio * 100, 1),
            "faceHeightTargetMin": int(FACE_HEIGHT_MIN * 100),
            "faceHeightTargetMax": int(FACE_HEIGHT_MAX * 100),
        }


def _clamp_crop_horizontal(
    cx: float, crop_w: float
) -> tuple[float, float]:
    cx_left = max(0.0, cx - crop_w / 2)
    cx_right = cx_left + crop_w
    if cx_right > 1.0:
        cx_right = 1.0
        cx_left = max(0.0, cx_right - crop_w)
    return cx_left, cx_right


def compute_icao_framing(lm) -> IcaoFramingBox:
    """Calcule le cadre ICAO 7:9 et le ratio visage / hauteur photo."""
    le = lm[_LEFT_EYE_IDX]
    re = lm[_RIGHT_EYE_IDX]
    forehead = lm[_FOREHEAD_IDX]
    chin = lm[_CHIN_IDX]

    face_core = max(float(chin.y) - float(forehead.y), 0.12)
    crown_y = float(forehead.y) - CROWN_ABOVE_FOREHEAD * face_core
    chin_y = float(chin.y)
    face_h = max(chin_y - crown_y, face_core)

    crop_h = face_h / FACE_HEIGHT_TARGET
    extra = crop_h - face_h
    margin_top = MARGIN_TOP_SHARE * extra
    margin_bottom = MARGIN_BOTTOM_SHARE * extra

    cy_top = max(0.0, crown_y - margin_top)
    cy_bottom = min(1.0, chin_y + margin_bottom)
    crop_h = cy_bottom - cy_top
    crop_w = crop_h * (ICAO_RATIO_W / ICAO_RATIO_H)

    cx = (float(le.x) + float(re.x)) / 2
    cx_left, cx_right = _clamp_crop_horizontal(cx, crop_w)

    face_height_ratio = face_h / crop_h if crop_h > 1e-6 else 0.0

    return IcaoFramingBox(
        x=cx_left,
        y=cy_top,
        width=cx_right - cx_left,
        height=crop_h,
        crown_y=crown_y,
        chin_y=chin_y,
        face_height=face_h,
        face_height_ratio=face_height_ratio,
    )


def compute_icao_framing_pixels(lm, w: int, h: int) -> tuple[int, int, int, int, IcaoFramingBox]:
    """Retourne x0, y0, x1, y1 (pixels) + métadonnées."""
    box = compute_icao_framing(lm)
    x0 = int(max(0, box.x * w))
    y0 = int(max(0, box.y * h))
    x1 = int(min(w, (box.x + box.width) * w))
    y1 = int(min(h, (box.y + box.height) * h))
    return x0, y0, x1, y1, box


def framing_distance_ok(box: IcaoFramingBox) -> bool:
    """Distance webcam : le cadre ICAO doit occuper une bonne part du flux."""
    return 0.56 <= box.height <= 0.90 and 0.42 <= box.width <= 0.95


def framing_face_ratio_ok(box: IcaoFramingBox) -> bool:
    return FACE_HEIGHT_MIN <= box.face_height_ratio <= FACE_HEIGHT_MAX


def framing_meta(box: IcaoFramingBox) -> dict[str, Any]:
    return {
        "faceHeightRatio": round(box.face_height_ratio, 4),
        "faceHeightPercent": round(box.face_height_ratio * 100, 1),
        "icaoFaceHeightBand": f"{int(FACE_HEIGHT_MIN * 100)}-{int(FACE_HEIGHT_MAX * 100)}",
    }
