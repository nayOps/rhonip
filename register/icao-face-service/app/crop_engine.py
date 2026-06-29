"""Recadrage ICAO : rotation légère + crop 7:9, sans étirement."""

from __future__ import annotations

import math
from typing import Any

import cv2
import numpy as np

from app.analyzer import _CHIN, _FOREHEAD, _LEFT_EYE, _NOSE_TIP, _RIGHT_EYE, detect_face_landmarks
from app.icao_framing import (
    ICAO_RATIO_H,
    ICAO_RATIO_W,
    compute_icao_framing_pixels,
    framing_meta,
)

OUTPUT_WIDTH = 420
OUTPUT_HEIGHT = int(OUTPUT_WIDTH * ICAO_RATIO_H / ICAO_RATIO_W)


def _lm_xy(lm, idx: int, w: int, h: int) -> tuple[float, float]:
    p = lm[idx]
    return p.x * w, p.y * h


def _rotate_image_and_points(
    bgr: np.ndarray, angle_deg: float, center: tuple[float, float]
) -> tuple[np.ndarray, np.ndarray]:
    h, w = bgr.shape[:2]
    m = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    rotated = cv2.warpAffine(
        bgr, m, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated, m


def _transform_point(px: float, py: float, m: np.ndarray) -> tuple[float, float]:
    x = m[0, 0] * px + m[0, 1] * py + m[0, 2]
    y = m[1, 0] * px + m[1, 1] * py + m[1, 2]
    return x, y


def crop_icao_from_bgr(bgr: np.ndarray) -> tuple[np.ndarray | None, dict[str, Any]]:
    """Image recadrée ICAO — visage 70–80 % hauteur, tête + haut des épaules."""
    h, w = bgr.shape[:2]
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    faces = detect_face_landmarks(rgb)
    meta: dict[str, Any] = {
        "croppingApplied": False,
        "stretchingApplied": False,
        "rotationCorrectionApplied": False,
        "rotationDegrees": 0.0,
        "ratio": f"{ICAO_RATIO_W}:{ICAO_RATIO_H}",
        "faceCentered": False,
        "eyesAligned": False,
        "chinVisible": False,
        "headTopMargin": "FAIL",
        "outputWidth": OUTPUT_WIDTH,
        "outputHeight": OUTPUT_HEIGHT,
    }

    if not faces:
        meta["error"] = "Visage non détecté pour le recadrage"
        return None, meta

    if len(faces) > 1:
        meta["error"] = "Plusieurs visages — recadrage impossible"
        return None, meta

    lm = faces[0]
    le = _lm_xy(lm, _LEFT_EYE[0], w, h)
    re = _lm_xy(lm, _RIGHT_EYE[0], w, h)
    forehead = _lm_xy(lm, _FOREHEAD, w, h)
    chin = _lm_xy(lm, _CHIN, w, h)
    nose = _lm_xy(lm, _NOSE_TIP, w, h)

    eye_mid = ((le[0] + re[0]) / 2, (le[1] + re[1]) / 2)
    angle = math.degrees(math.atan2(re[1] - le[1], re[0] - le[0]))
    rotation_applied = abs(angle) > 0.8

    work = bgr
    m_rot = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float64)
    if rotation_applied:
        work, m_rot = _rotate_image_and_points(work, -angle, eye_mid)
        meta["rotationCorrectionApplied"] = True
        meta["rotationDegrees"] = round(-angle, 2)

    le2 = _transform_point(le[0], le[1], m_rot)
    re2 = _transform_point(re[0], re[1], m_rot)
    forehead2 = _transform_point(forehead[0], forehead[1], m_rot)
    chin2 = _transform_point(chin[0], chin[1], m_rot)
    nose2 = _transform_point(nose[0], nose[1], m_rot)

    wh, ww = work.shape[:2]
    rgb_work = cv2.cvtColor(work, cv2.COLOR_BGR2RGB)
    faces_work = detect_face_landmarks(rgb_work)
    lm_work = faces_work[0] if faces_work else lm

    x0, y0, x1, y1, frame = compute_icao_framing_pixels(lm_work, ww, wh)
    meta.update(framing_meta(frame))

    if y1 <= y0 or x1 <= x0:
        meta["error"] = "Zone de recadrage invalide"
        return None, meta

    cropped = work[y0:y1, x0:x1]
    if cropped.size == 0:
        meta["error"] = "Crop vide"
        return None, meta

    scale = min(OUTPUT_WIDTH / cropped.shape[1], OUTPUT_HEIGHT / cropped.shape[0])
    new_w = max(1, int(cropped.shape[1] * scale))
    new_h = max(1, int(cropped.shape[0] * scale))
    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)

    canvas = np.full((OUTPUT_HEIGHT, OUTPUT_WIDTH, 3), 255, dtype=np.uint8)
    off_x = (OUTPUT_WIDTH - new_w) // 2
    off_y = (OUTPUT_HEIGHT - new_h) // 2
    canvas[off_y : off_y + new_h, off_x : off_x + new_w] = resized

    face_h_px = max(chin2[1] - forehead2[1], wh * 0.08)
    meta["croppingApplied"] = True
    meta["faceCentered"] = abs(nose2[0] - (x0 + x1) / 2) < (x1 - x0) * 0.12
    meta["eyesAligned"] = abs(le2[1] - re2[1]) < max(4.0, face_h_px * 0.04)
    meta["chinVisible"] = chin2[1] <= y1 - 2
    meta["headTopMargin"] = "OK" if y0 <= forehead2[1] - 0.05 * face_h_px else "WARN"
    meta["cropRect"] = {
        "x0": x0,
        "y0": y0,
        "x1": x1,
        "y1": y1,
        "imageWidth": ww,
        "imageHeight": wh,
    }

    return canvas, meta


def encode_jpeg_bgr(bgr: np.ndarray, quality: int = 92) -> bytes:
    ok, buf = cv2.imencode(".jpg", bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        raise ValueError("Encodage JPEG échoué")
    return buf.tobytes()