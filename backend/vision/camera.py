# vision/camera.py - open a webcam or a recorded video with OpenCV

import os
import cv2

from ..config import VIDEO_FOLDER, FRAME_WIDTH


def list_videos():
    """Names of the video files inside the videos/ folder."""
    if not VIDEO_FOLDER.exists():
        return []
    allowed = (".mp4", ".avi", ".mov", ".mkv")
    return sorted(f for f in os.listdir(VIDEO_FOLDER) if f.lower().endswith(allowed))


def open_source(source: str):
    """source = "0" (webcam number) or a video file name."""
    if source.isdigit():
        cap = cv2.VideoCapture(int(source))
    else:
        # os.path.basename stops people from opening files outside the videos folder
        path = VIDEO_FOLDER / os.path.basename(source)
        cap = cv2.VideoCapture(str(path))

    if not cap.isOpened():
        raise RuntimeError("Could not open video source: " + source)
    return cap


def resize_frame(frame):
    """Make the frame smaller so processing is faster."""
    height, width = frame.shape[:2]
    if width <= FRAME_WIDTH:
        return frame
    new_height = int(height * FRAME_WIDTH / width)
    return cv2.resize(frame, (FRAME_WIDTH, new_height))
