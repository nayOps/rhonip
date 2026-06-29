from typing import Any, Literal

from pydantic import BaseModel, Field

CheckStatus = Literal["OK", "WARN", "FAIL"]


class ChecksDetail(BaseModel):
    faceDetected: bool = False
    singleFace: bool = False
    faceCentered: bool = False
    eyesOpen: bool = False
    gazeToCamera: bool = False
    mouthClosed: bool = False
    neutralExpression: bool = False
    headStraight: bool = False
    yaw: CheckStatus = "FAIL"
    pitch: CheckStatus = "FAIL"
    roll: CheckStatus = "FAIL"
    lighting: CheckStatus = "FAIL"
    overExposure: bool = False
    underExposure: bool = False
    sharpness: CheckStatus = "FAIL"
    backgroundUniform: bool = False
    occlusionDetected: bool = False
    resolution: bool = False


class RealtimeChecks(BaseModel):
    faceDetected: bool = False
    singleFace: bool = False
    faceCentered: bool = False
    eyesOpen: bool = False
    mouthClosed: bool = False
    headPose: CheckStatus = "FAIL"
    lighting: CheckStatus = "FAIL"
    background: CheckStatus = "FAIL"
    sharpness: CheckStatus = "FAIL"


class Point2D(BaseModel):
    x: float
    y: float


class LiveOverlay(BaseModel):
    facialLandmarks: list[Point2D] = Field(default_factory=list)
    connections: list[list[int]] = Field(default_factory=list)
    boundingBox: dict[str, float] | None = None
    eyeLine: dict[str, Point2D] | None = None
    faceAxis: dict[str, Point2D] | None = None
    cropFrame: dict[str, float | str] | None = None


class RealtimeResponse(BaseModel):
    mode: Literal["REAL_TIME"] = "REAL_TIME"
    status: Literal["NOT_READY", "READY"] = "NOT_READY"
    message: str = "Placez votre visage devant la caméra"
    qualityScore: int = 0
    checks: RealtimeChecks = Field(default_factory=RealtimeChecks)
    overlay: LiveOverlay | None = None


class FinalResponse(BaseModel):
    mode: Literal["FINAL_CAPTURE"] = "FINAL_CAPTURE"
    status: Literal["ACCEPTED", "REVIEW", "REJECTED"] = "REJECTED"
    icaoCompliant: bool = False
    isoCompliant: bool = False
    qualityScore: int = 0
    checks: ChecksDetail = Field(default_factory=ChecksDetail)
    metadata: dict[str, Any] = Field(default_factory=dict)
    recommendation: str = ""
    errors: list[str] = Field(default_factory=list)


class CropInfo(BaseModel):
    croppingApplied: bool = False
    stretchingApplied: bool = False
    rotationCorrectionApplied: bool = False
    rotationDegrees: float = 0.0
    ratio: str = "7:9"
    faceCentered: bool = False
    eyesAligned: bool = False
    chinVisible: bool = False
    headTopMargin: str = "FAIL"
    outputWidth: int = 0
    outputHeight: int = 0
    cropRect: dict[str, int] | None = None
    error: str | None = None


class CaptureInfo(BaseModel):
    rawImageSaved: bool = True
    icaoImageSaved: bool = False
    rawSha256: str = ""
    icaoSha256: str = ""
    rawImageBase64: str = ""
    icaoImageBase64: str = ""


class LiveOverlayFlags(BaseModel):
    facialLandmarks: bool = True
    faceMesh: bool = True
    boundingBox: bool = True
    eyeLine: bool = True
    faceAxis: bool = True
    cropFrame: bool = True


class ProcessCaptureResponse(BaseModel):
    capture: CaptureInfo
    liveOverlay: LiveOverlayFlags = Field(default_factory=LiveOverlayFlags)
    crop: CropInfo
    quality: FinalResponse
    recommendation: str = ""


class WsFrameIn(BaseModel):
    image: str
