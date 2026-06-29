"""Géométrie live : landmarks, lignes, cadre ICAO pour overlay navigateur."""

from __future__ import annotations

from typing import Any

from app.icao_framing import ICAO_RATIO_H, ICAO_RATIO_W, compute_icao_framing

# Contour visage (MediaPipe Face Landmarker — indices courants)
_FACE_OVAL: tuple[int, ...] = (
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378,
    400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54,
    103, 67, 109,
)

_LEFT_EYE_IDX = 33
_RIGHT_EYE_IDX = 263
_NOSE_TIP = 1
_CHIN = 152
_FOREHEAD = 10


def _pt(lm, idx: int) -> dict[str, float]:
    p = lm[idx]
    return {"x": round(float(p.x), 4), "y": round(float(p.y), 4)}


def _oval_connections() -> list[list[int]]:
    pairs: list[list[int]] = []
    oval = list(_FACE_OVAL)
    for i in range(len(oval) - 1):
        pairs.append([oval[i], oval[i + 1]])
    pairs.append([oval[-1], oval[0]])
    pairs.append([_LEFT_EYE_IDX, _RIGHT_EYE_IDX])
    pairs.append([_NOSE_TIP, _CHIN])
    return pairs


def build_live_overlay(lm, *, w: int, h: int) -> dict[str, Any]:
    """Overlay normalisé 0–1 — cadre 7:9, visage 70–80 % hauteur (cible 75 %)."""
    xs = [p.x for p in lm]
    ys = [p.y for p in lm]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    frame = compute_icao_framing(lm)
    landmarks = [{"x": round(float(p.x), 4), "y": round(float(p.y), 4)} for p in lm]

    return {
        "facialLandmarks": landmarks,
        "connections": _oval_connections(),
        "boundingBox": {
            "xMin": round(x_min, 4),
            "yMin": round(y_min, 4),
            "xMax": round(x_max, 4),
            "yMax": round(y_max, 4),
        },
        "eyeLine": {
            "left": _pt(lm, _LEFT_EYE_IDX),
            "right": _pt(lm, _RIGHT_EYE_IDX),
        },
        "faceAxis": {
            "top": {"x": round((x_min + x_max) / 2, 4), "y": round(frame.crown_y, 4)},
            "bottom": _pt(lm, _CHIN),
            "nose": _pt(lm, _NOSE_TIP),
        },
        "cropFrame": frame.as_crop_dict(),
    }

