# vision/tracking.py - remember which tracked objects were seen recently
#
# Counting detections in every frame is wrong, because the same bottle
# appears in many frames. Each object has a tracker ID, so we count
# UNIQUE IDs seen in the last few frames instead.


class TrackHistory:
    def __init__(self, window=30):
        self.window = window      # how many frames we remember
        self.last_seen = {}       # key -> {track_id: frame_number}

    def mark(self, key, track_id, frame_number):
        """Say that object `track_id` was seen in this frame."""
        if key not in self.last_seen:
            self.last_seen[key] = {}
        self.last_seen[key][track_id] = frame_number

    def count(self, key, frame_number):
        """How many unique objects were seen in the last `window` frames."""
        ids = self.last_seen.get(key, {})

        # forget objects that disappeared
        for track_id in list(ids.keys()):
            if frame_number - ids[track_id] > self.window:
                del ids[track_id]

        return len(ids)
