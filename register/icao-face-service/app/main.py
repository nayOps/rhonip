"""ONIP ICAO Face Capture & Quality Control Service."""

from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.analyzer import (
    build_final_response,
    build_realtime_response,
    decode_data_url,
    decode_image,
    final_status,
)
from app.config import (
    AUTO_CAPTURE_STABLE_FRAMES,
    HOST,
    PORT,
    REALTIME_READY_SCORE,
    SCORE_ACCEPTED,
    SCORE_REVIEW,
)
from app.crop_engine import crop_icao_from_bgr, encode_jpeg_bgr
from app.models import (
    CaptureInfo,
    CropInfo,
    FinalResponse,
    LiveOverlayFlags,
    ProcessCaptureResponse,
    RealtimeResponse,
    WsFrameIn,
)

app = FastAPI(
    title="ONIP ICAO Face Quality Assistant",
    version="1.0.0",
    description="Guidage temps réel et validation finale photo d'identité (webcam).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
    ],
    # Guichet LAN (ex. http://192.168.x.x:3000) + localhost
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "icao-face-assistant",
        "port": PORT,
        "thresholds": {
            "scoreAccepted": SCORE_ACCEPTED,
            "scoreReview": SCORE_REVIEW,
            "realtimeReadyScore": REALTIME_READY_SCORE,
            "autoCaptureStableFrames": AUTO_CAPTURE_STABLE_FRAMES,
        },
    }


@app.get("/face/stream/status")
def stream_status_hint() -> dict:
    """Indique d'utiliser le WebSocket pour le flux temps réel."""
    return {
        "message": f"Utilisez WebSocket ws://{HOST}:{PORT}/face/ws avec des frames JPEG base64.",
        "websocket": f"ws://{HOST}:{PORT}/face/ws",
    }


@app.websocket("/face/ws")
async def face_stream_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = WsFrameIn.model_validate_json(raw)
                data = decode_data_url(payload.image)
                bgr = decode_image(data)
                response: RealtimeResponse = build_realtime_response(bgr)
                await websocket.send_text(response.model_dump_json())
            except Exception as exc:
                err = RealtimeResponse(
                    status="NOT_READY",
                    message=f"Frame invalide : {exc}",
                    qualityScore=0,
                )
                await websocket.send_text(err.model_dump_json())
    except WebSocketDisconnect:
        return


@app.post("/face/quality-check", response_model=FinalResponse)
async def quality_check(
    image: UploadFile = File(...),
    enrollmentId: Optional[str] = Form(None),
    deviceId: Optional[str] = Form(None),
    operatorId: Optional[str] = Form(None),
    camera: Optional[str] = Form("Webcam"),
) -> FinalResponse:
    raw = await image.read()
    bgr = decode_image(raw)
    detail, score, errors, recommendation = build_final_response(
        bgr,
        enrollment_id=enrollmentId,
        device_id=deviceId,
        operator_id=operatorId,
        camera=camera,
    )
    status = final_status(score)
    return FinalResponse(
        status=status,
        icaoCompliant=status == "ACCEPTED",
        isoCompliant=status == "ACCEPTED",
        qualityScore=score,
        checks=detail,
        metadata={
            "camera": camera or "Webcam",
            "deviceId": deviceId or "",
            "operatorId": operatorId or "",
            "enrollmentId": enrollmentId or "",
            "captureTimestamp": datetime.now(timezone.utc).isoformat(),
        },
        recommendation=recommendation,
        errors=errors,
    )


@app.post("/face/process-capture", response_model=ProcessCaptureResponse)
async def process_capture(
    image: UploadFile = File(...),
    enrollmentId: Optional[str] = Form(None),
    deviceId: Optional[str] = Form(None),
    operatorId: Optional[str] = Form(None),
    camera: Optional[str] = Form("Webcam"),
) -> ProcessCaptureResponse:
    """Photo brute → recadrage ICAO 7:9 → contrôle qualité + empreintes audit."""
    raw_bytes = await image.read()
    bgr = decode_image(raw_bytes)
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    raw_b64 = base64.b64encode(raw_bytes).decode("ascii")

    icao_bgr, crop_meta = crop_icao_from_bgr(bgr)
    crop_info = CropInfo.model_validate(crop_meta)

    if icao_bgr is None:
        detail, score, errors, recommendation = build_final_response(
            bgr,
            enrollment_id=enrollmentId,
            device_id=deviceId,
            operator_id=operatorId,
            camera=camera,
        )
        status = final_status(score)
        quality = FinalResponse(
            status=status,
            icaoCompliant=False,
            isoCompliant=False,
            qualityScore=score,
            checks=detail,
            metadata={
                "camera": camera or "Webcam",
                "deviceId": deviceId or "KIT-ONIP-WEBCAM",
                "operatorId": operatorId or "",
                "enrollmentId": enrollmentId or "",
                "captureTimestamp": datetime.now(timezone.utc).isoformat(),
            },
            recommendation=recommendation or "Recadrage ICAO impossible",
            errors=[*errors, *( [crop_meta["error"]] if crop_meta.get("error") else [] )],
        )
        return ProcessCaptureResponse(
            capture=CaptureInfo(
                rawImageSaved=True,
                icaoImageSaved=False,
                rawSha256=raw_sha,
                icaoSha256="",
                rawImageBase64=raw_b64,
                icaoImageBase64="",
            ),
            liveOverlay=LiveOverlayFlags(),
            crop=crop_info,
            quality=quality,
            recommendation=quality.recommendation,
        )

    icao_bytes = encode_jpeg_bgr(icao_bgr)
    icao_sha = hashlib.sha256(icao_bytes).hexdigest()
    icao_b64 = base64.b64encode(icao_bytes).decode("ascii")

    detail, score, errors, recommendation = build_final_response(
        icao_bgr,
        enrollment_id=enrollmentId,
        device_id=deviceId,
        operator_id=operatorId,
        camera=camera,
    )
    status = final_status(score)
    ts = datetime.now(timezone.utc).isoformat()
    quality = FinalResponse(
        status=status,
        icaoCompliant=status == "ACCEPTED",
        isoCompliant=status == "ACCEPTED",
        qualityScore=score,
        checks=detail,
        metadata={
            "camera": camera or "Webcam",
            "deviceId": deviceId or "KIT-ONIP-WEBCAM",
            "operatorId": operatorId or "",
            "enrollmentId": enrollmentId or "",
            "captureTimestamp": ts,
            "rawSha256": raw_sha,
            "icaoSha256": icao_sha,
        },
        recommendation=recommendation,
        errors=errors,
    )
    rec = (
        "Photo ICAO normalisée générée avec succès."
        if status == "ACCEPTED"
        else recommendation
    )
    return ProcessCaptureResponse(
        capture=CaptureInfo(
            rawImageSaved=True,
            icaoImageSaved=True,
            rawSha256=raw_sha,
            icaoSha256=icao_sha,
            rawImageBase64=raw_b64,
            icaoImageBase64=icao_b64,
        ),
        liveOverlay=LiveOverlayFlags(),
        crop=crop_info,
        quality=quality,
        recommendation=rec,
    )


def run() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)


if __name__ == "__main__":
    run()
