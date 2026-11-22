# routes/detection.py - start / stop camera processing and the live video stream

import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from ..models import User
from ..schemas import StartIn
from ..security import get_current_user, read_token
from ..vision.camera import list_videos
from ..vision.pipeline import pipeline

router = APIRouter(prefix="/api/detection", tags=["Detection"])


@router.post("/start")
def start_detection(data: StartIn, user: User = Depends(get_current_user)):
    try:
        pipeline.start(data.source.strip())
    except RuntimeError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return pipeline.status


@router.post("/stop")
def stop_detection(user: User = Depends(get_current_user)):
    pipeline.stop()
    return pipeline.status


@router.get("/status")
def detection_status(user: User = Depends(get_current_user)):
    return pipeline.status


@router.get("/videos")
def get_videos(user: User = Depends(get_current_user)):
    return list_videos()


# The <img> tag cannot send a login header, so the token comes in the URL.
@router.get("/stream")
def stream(token: str = ""):
    if read_token(token) is None:
        raise HTTPException(status_code=401, detail="Please login first")

    def frames():
        last = None
        idle = 0
        while idle < 100:                     # stop after about 5 seconds without video
            jpeg = pipeline.latest_jpeg
            if jpeg is not None and jpeg is not last:
                last = jpeg
                idle = 0
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
            else:
                idle += 1
            time.sleep(0.05)

    return StreamingResponse(frames(), media_type="multipart/x-mixed-replace; boundary=frame")
