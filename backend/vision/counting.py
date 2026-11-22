# vision/counting.py - count unique products inside each shelf region

from .shelf_monitor import center_inside


def count_by_shelf(detections, shelf_rois, history, frame_number):
    """Returns {shelf_id: {"bottle": 4, "box": 2}}.

    Steps:
      1. For every detection, find the shelf whose region contains it.
      2. Remember its tracker ID for that shelf.
      3. Count the unique IDs seen recently (see tracking.py).
    """
    seen_keys = []

    for det in detections:
        if det["id"] == -1:
            continue                         # the tracker has not given an ID yet

        for item in shelf_rois:
            if center_inside(det["box"], item["roi"]):
                key = (item["shelf_id"], det["label"])
                history.mark(key, det["id"], frame_number)
                if key not in seen_keys:
                    seen_keys.append(key)

    # include old keys too, so a product that disappeared goes down to 0
    for key in list(history.last_seen.keys()):
        if key not in seen_keys:
            seen_keys.append(key)

    counts = {}
    for (shelf_id, label) in seen_keys:
        number = history.count((shelf_id, label), frame_number)
        if shelf_id not in counts:
            counts[shelf_id] = {}
        counts[shelf_id][label] = number
    return counts
