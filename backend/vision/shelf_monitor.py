# vision/shelf_monitor.py - shelf regions (ROI), occupancy and drawing

import cv2
import numpy as np


def roi_to_pixels(shelf, frame_width, frame_height):
    """Shelf ROI is saved as percent. Convert it to pixels: (x1, y1, x2, y2)."""
    x1 = int(shelf["roi_x"] / 100 * frame_width)
    y1 = int(shelf["roi_y"] / 100 * frame_height)
    x2 = int((shelf["roi_x"] + shelf["roi_w"]) / 100 * frame_width)
    y2 = int((shelf["roi_y"] + shelf["roi_h"]) / 100 * frame_height)
    return x1, y1, x2, y2


def center_inside(box, roi):
    """Is the centre of a bounding box inside the ROI?"""
    cx = (box[0] + box[2]) // 2
    cy = (box[1] + box[3]) // 2
    return roi[0] <= cx <= roi[2] and roi[1] <= cy <= roi[3]


def occupancy_percent(roi, boxes):
    """How much of the ROI area is covered by detected objects (0-100).
    We make a small black image of the ROI and paint each box white."""
    width = roi[2] - roi[0]
    height = roi[3] - roi[1]
    if width <= 0 or height <= 0:
        return 0

    mask = np.zeros((height, width), dtype=np.uint8)

    for (x1, y1, x2, y2) in boxes:
        # move the box to ROI coordinates and cut the part outside
        bx1 = max(x1 - roi[0], 0)
        by1 = max(y1 - roi[1], 0)
        bx2 = min(x2 - roi[0], width)
        by2 = min(y2 - roi[1], height)
        if bx2 > bx1 and by2 > by1:
            mask[by1:by2, bx1:bx2] = 1

    return int(round(mask.mean() * 100))


def draw_overlay(frame, shelf_rois, detections):
    """Draw shelf regions and detection boxes on the frame."""
    # shelf regions
    for item in shelf_rois:
        x1, y1, x2, y2 = item["roi"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (224, 165, 38), 2)
        text = item["name"] + "  " + str(item["occupancy"]) + "%"
        cv2.putText(frame, text, (x1 + 4, y1 + 18), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (224, 165, 38), 2)

    # detected objects
    for det in detections:
        x1, y1, x2, y2 = det["box"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (237, 111, 47), 2)
        text = det["label"] + " #" + str(det["id"]) + " " + format(det["conf"], ".2f")
        cv2.putText(frame, text, (x1, max(y1 - 6, 12)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (237, 111, 47), 2)
    return frame
