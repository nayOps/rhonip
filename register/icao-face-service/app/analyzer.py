"""Analyse qualité visage ICAO (heuristiques MediaPipe + OpenCV)."""

from __future__ import annotations

import base64
import math
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

from app.config import REALTIME_READY_SCORE, SCORE_ACCEPTED, SCORE_REVIEW
from app.icao_framing import (
    FACE_HEIGHT_MAX,
    FACE_HEIGHT_MIN,
    compute_icao_framing,
    framing_distance_ok,
    framing_face_ratio_ok,
)
from app.models import ChecksDetail, LiveOverlay, RealtimeChecks, RealtimeResponse
from app.overlay import build_live_overlay

Mode = Literal["realtime", "final"]

MIN_WIDTH = 480
MIN_HEIGHT = 640

# Indices Face Mesh (MediaPipe)
_LEFT_EYE = (33, 160, 158, 133, 153, 144)
_RIGHT_EYE = (362, 385, 387, 263, 373, 380)
_MOUTH = (13, 14, 78, 308)
_NOSE_TIP = 1
_CHIN = 152
_FOREHEAD = 10

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "face_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)

_landmarker: vision.FaceLandmarker | None = None


def ensure_model() -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if not MODEL_PATH.exists():
        print(f"Téléchargement du modèle MediaPipe ({MODEL_PATH.name})…")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    return MODEL_PATH


def get_landmarker() -> vision.FaceLandmarker:
    global _landmarker
    if _landmarker is None:
        ensure_model()
        options = vision.FaceLandmarkerOptions(
            base_options=mp_tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=vision.RunningMode.IMAGE,
            num_faces=2,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        _landmarker = vision.FaceLandmarker.create_from_options(options)
    return _landmarker


def detect_face_landmarks(rgb: np.ndarray) -> list:
    landmarker = get_landmarker()
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = landmarker.detect(mp_image)
    return result.face_landmarks or []


@dataclass
class FaceMetrics:
    face_count: int
    center_x: float
    center_y: float
    face_size: float
    crop_height: float
    face_height_pct: float
    eyes_closed: bool
    mouth_open: bool
    head_tilted: bool
    gaze_off: bool
    brightness_bad: bool
    over_exposed: bool
    under_exposed: bool
    blurry: bool
    background_bad: bool
    resolution_ok: bool
    occlusion: bool


def decode_image(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Image illisible")
    return img


def decode_data_url(data_url: str) -> bytes:
    if "," in data_url:
        _, b64 = data_url.split(",", 1)
    else:
        b64 = data_url
    return base64.b64decode(b64)


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _ear(landmarks, indices: tuple[int, ...], w: int, h: int) -> float:
    pts = [(landmarks[i].x * w, landmarks[i].y * h) for i in indices]
    v1 = _dist(pts[1], pts[5])
    v2 = _dist(pts[2], pts[4])
    horiz = _dist(pts[0], pts[3])
    if horiz < 1e-6:
        return 0.3
    return (v1 + v2) / (2.0 * horiz)


def _laplacian_variance(gray_roi: np.ndarray) -> float:
    if gray_roi.size == 0:
        return 0.0
    return float(cv2.Laplacian(gray_roi, cv2.CV_64F).var())


def _sample_mean_std(bgr: np.ndarray, x0: float, y0: float, x1: float, y1: float) -> tuple[float, float]:
    h, w = bgr.shape[:2]
    xs, xe = int(x0 * w), int(x1 * w)
    ys, ye = int(y0 * h), int(y1 * h)
    roi = bgr[ys:ye, xs:xe]
    if roi.size == 0:
        return 0.0, 0.0
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    return float(gray.mean()), float(gray.std())


def analyze_frame(bgr: np.ndarray, mode: Mode = "realtime") -> tuple[FaceMetrics | None, RealtimeChecks, int, list[str]]:
    h, w = bgr.shape[:2]
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    face_landmarks_list = detect_face_landmarks(rgb)

    errors: list[str] = []
    checks = RealtimeChecks()

    resolution_ok = w >= MIN_WIDTH and h >= MIN_HEIGHT
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    full_mean = float(gray.mean())
    full_std = float(gray.std())
    lap_var = _laplacian_variance(gray[int(h * 0.15) : int(h * 0.85), int(w * 0.2) : int(w * 0.8)])

    relax = mode == "realtime"
    sharp_thresh = 80.0 if relax else 120.0
    blur = lap_var < sharp_thresh

    over = full_mean > 235 or (full_std > 70 and full_mean > 200)
    under = full_mean < 55
    bright_bad = full_mean < 65 or full_mean > 225 or under or over

    border_l_mean, _ = _sample_mean_std(bgr, 0, 0, 0.18, 1)
    border_r_mean, _ = _sample_mean_std(bgr, 0.82, 0, 1, 1)
    border_ok = border_l_mean >= 140 and border_r_mean >= 140

    if not face_landmarks_list:
        checks.sharpness = "FAIL" if blur else "OK"
        checks.lighting = "FAIL" if bright_bad else "OK"
        checks.background = "FAIL" if not border_ok else "OK"
        score = 15 if resolution_ok else 5
        return None, checks, score, ["Visage non détecté"]

    face_count = len(face_landmarks_list)
    lm = face_landmarks_list[0]

    xs = [p.x for p in lm]
    ys = [p.y for p in lm]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    cx = (x_min + x_max) / 2
    cy = (y_min + y_max) / 2
    face_size = (x_max - x_min) * (y_max - y_min)
    frame = compute_icao_framing(lm)
    crop_height = frame.height
    face_height_pct = frame.face_height_ratio * 100.0

    left_ear = _ear(lm, _LEFT_EYE, w, h)
    right_ear = _ear(lm, _RIGHT_EYE, w, h)
    ear = (left_ear + right_ear) / 2
    eyes_closed = ear < (0.19 if relax else 0.21)

    mouth_pts = [(lm[i].x * w, lm[i].y * h) for i in _MOUTH]
    mouth_open = _dist(mouth_pts[0], mouth_pts[1]) > (0.035 * w if relax else 0.03 * w)

    le = (lm[_LEFT_EYE[0]].x * w, lm[_LEFT_EYE[0]].y * h)
    re = (lm[_RIGHT_EYE[0]].x * w, lm[_RIGHT_EYE[0]].y * h)
    roll_deg = abs(math.degrees(math.atan2(re[1] - le[1], re[0] - le[0])))
    head_tilted = roll_deg > (12 if relax else 8)

    nose = (lm[_NOSE_TIP].x, lm[_NOSE_TIP].y)
    gaze_off = abs(nose[0] - cx) > (0.06 if relax else 0.04)

    # Centrage dans le cadre ICAO 7:9 (même géométrie que la photo de référence)
    crop_cx = frame.x + frame.width / 2
    crop_cy = frame.y + frame.height / 2
    cx_tol = 0.11 if relax else 0.08
    cy_tol = 0.12 if relax else 0.09
    centered = (
        abs(nose[0] - crop_cx) <= cx_tol
        and abs(cy - crop_cy) <= cy_tol
    )
    size_ok = framing_distance_ok(frame) and framing_face_ratio_ok(frame)

    face_roi = gray[int(y_min * h) : int(y_max * h), int(x_min * w) : int(x_max * w)]
    face_lap = _laplacian_variance(face_roi) if face_roi.size else lap_var
    blur = face_lap < sharp_thresh

    center_mean, _ = _sample_mean_std(bgr, x_min, y_min, x_max, y_max)
    bg_uniform = border_ok and (border_l_mean - center_mean > 8 or border_r_mean - center_mean > 8)

    # Occlusion grossière : asymétrie forte des joues
    occlusion = False

    metrics = FaceMetrics(
        face_count=face_count,
        center_x=cx,
        center_y=cy,
        face_size=face_size,
        crop_height=crop_height,
        face_height_pct=face_height_pct,
        eyes_closed=eyes_closed,
        mouth_open=mouth_open,
        head_tilted=head_tilted,
        gaze_off=gaze_off,
        brightness_bad=bright_bad,
        over_exposed=over,
        under_exposed=under,
        blurry=blur,
        background_bad=not bg_uniform,
        resolution_ok=resolution_ok,
        occlusion=occlusion,
    )

    checks.faceDetected = True
    checks.singleFace = face_count == 1
    checks.faceCentered = centered and size_ok
    checks.eyesOpen = not eyes_closed
    checks.mouthClosed = not mouth_open
    checks.headPose = "OK" if not head_tilted and not gaze_off else "FAIL"
    checks.lighting = "OK" if not bright_bad else "FAIL"
    checks.background = "OK" if bg_uniform else "FAIL"
    checks.sharpness = "OK" if not blur else "FAIL"

    weights = [
        (checks.faceDetected, 12),
        (checks.singleFace, 10),
        (checks.faceCentered, 18),
        (checks.eyesOpen, 12),
        (checks.mouthClosed, 10),
        (checks.headPose == "OK", 12),
        (checks.lighting == "OK", 10),
        (checks.background == "OK", 8),
        (checks.sharpness == "OK", 8),
    ]
    if resolution_ok:
        weights.append((True, 10))
    score = min(100, sum(w for ok, w in weights if ok))

    if not checks.singleFace:
        errors.append("Plusieurs visages détectés")
    if not centered:
        if nose[0] < crop_cx - cx_tol:
            errors.append("Visage trop à gauche")
        elif nose[0] > crop_cx + cx_tol:
            errors.append("Visage trop à droite")
        if cy < crop_cy - cy_tol:
            errors.append("Visage trop haut")
        elif cy > crop_cy + cy_tol:
            errors.append("Visage trop bas")
    if not size_ok:
        if crop_height < 0.56:
            errors.append("Approchez-vous (visage trop petit dans le cadre)")
        elif crop_height > 0.90:
            errors.append("Reculez légèrement (cadre trop grand)")
        elif face_height_pct < FACE_HEIGHT_MIN * 100:
            errors.append("Remontez légèrement la tête")
        elif face_height_pct > FACE_HEIGHT_MAX * 100:
            errors.append("Baissez légèrement la tête")
    if eyes_closed:
        errors.append("Yeux fermés")
    if mouth_open:
        errors.append("Bouche ouverte")
    if head_tilted:
        errors.append("Tête inclinée")
    if gaze_off:
        errors.append("Regard non centré")
    if bright_bad:
        errors.append("Éclairage incorrect")
    if over:
        errors.append("Surexposition")
    if under:
        errors.append("Sous-exposition")
    if blur:
        errors.append("Image floue")
    if not bg_uniform:
        errors.append("Fond non uniforme")
    if not resolution_ok:
        errors.append("Résolution insuffisante")

    return metrics, checks, score, errors


def pick_realtime_message(metrics: FaceMetrics | None, checks: RealtimeChecks) -> str:
    if metrics is None or not checks.faceDetected:
        return "Placez votre visage devant la caméra"
    if not checks.singleFace:
        return "Une seule personne doit être visible"
    if not checks.faceCentered and metrics:
        if metrics.crop_height < 0.56:
            return "Approchez-vous — le cadre vert doit être plus grand"
        if metrics.crop_height > 0.90:
            return "Reculez — le cadre vert dépasse l'image"
        return "Centrez votre visage dans le cadre vert (tête + épaules)"
    if not checks.eyesOpen:
        return "Ouvrez les yeux"
    if not checks.mouthClosed:
        return "Fermez la bouche"
    if checks.headPose != "OK":
        return "Redressez la tête"
    if checks.lighting != "OK":
        if metrics and metrics.over_exposed:
            return "Réduisez la lumière directe"
        if metrics and metrics.under_exposed:
            return "Ajoutez de la lumière"
        return "Améliorez l'éclairage"
    if checks.sharpness != "OK":
        return "Stabilisez la caméra"
    if checks.background != "OK":
        return "Utilisez un fond clair et uniforme"
    return "Photo conforme — capture possible"


def build_realtime_response(bgr: np.ndarray) -> RealtimeResponse:
    h, w = bgr.shape[:2]
    metrics, checks, score, _ = analyze_frame(bgr, mode="realtime")
    message = pick_realtime_message(metrics, checks)
    ready = (
        checks.faceDetected
        and checks.singleFace
        and checks.faceCentered
        and checks.eyesOpen
        and checks.mouthClosed
        and checks.headPose == "OK"
        and checks.lighting == "OK"
        and checks.sharpness == "OK"
        and score >= REALTIME_READY_SCORE
    )
    if ready:
        message = "Ne bougez plus — vous pouvez capturer"

    overlay: LiveOverlay | None = None
    if checks.faceDetected:
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        faces = detect_face_landmarks(rgb)
        if faces:
            overlay = LiveOverlay.model_validate(build_live_overlay(faces[0], w=w, h=h))

    return RealtimeResponse(
        status="READY" if ready else "NOT_READY",
        message=message,
        qualityScore=score,
        checks=checks,
        overlay=overlay,
    )


def build_final_response(
    bgr: np.ndarray,
    *,
    enrollment_id: str | None = None,
    device_id: str | None = None,
    operator_id: str | None = None,
    camera: str | None = None,
) -> tuple[ChecksDetail, int, list[str], str]:
    metrics, rt_checks, score, errors = analyze_frame(bgr, mode="final")

    detail = ChecksDetail(
        faceDetected=rt_checks.faceDetected,
        singleFace=rt_checks.singleFace,
        faceCentered=rt_checks.faceCentered,
        eyesOpen=rt_checks.eyesOpen,
        gazeToCamera=rt_checks.headPose == "OK",
        mouthClosed=rt_checks.mouthClosed,
        neutralExpression=rt_checks.mouthClosed and rt_checks.eyesOpen,
        headStraight=rt_checks.headPose == "OK",
        yaw="OK" if metrics and not metrics.gaze_off else "FAIL",
        pitch="OK" if metrics and not metrics.head_tilted else "FAIL",
        roll="OK" if metrics and not metrics.head_tilted else "FAIL",
        lighting=rt_checks.lighting,
        overExposure=bool(metrics and metrics.over_exposed),
        underExposure=bool(metrics and metrics.under_exposed),
        sharpness=rt_checks.sharpness,
        backgroundUniform=rt_checks.background == "OK",
        occlusionDetected=bool(metrics and metrics.occlusion),
        resolution=bool(metrics and metrics.resolution_ok) if metrics else False,
    )

    if score >= SCORE_ACCEPTED:
        recommendation = "Photo conforme ICAO"
    elif score >= SCORE_REVIEW:
        recommendation = "Photo acceptable sous réserve — vérification opérateur recommandée"
    else:
        recommendation = "Reprendre la photo : " + (errors[0] if errors else "qualité insuffisante")

    return detail, score, errors, recommendation


def final_status(score: int) -> Literal["ACCEPTED", "REVIEW", "REJECTED"]:
    if score >= SCORE_ACCEPTED:
        return "ACCEPTED"
    if score >= SCORE_REVIEW:
        return "REVIEW"
    return "REJECTED"
