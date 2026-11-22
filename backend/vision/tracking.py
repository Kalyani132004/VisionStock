# vision/tracking.py - remember which tracked objects were seen recently


class TrackHistory:
    def __init__(self, window=30):
        self.window = window      # how many frames we remember
        self.last_seen = {}       # key -> {track_id: frame_number}

    def mark(self, key, track_id, frame_number):
        if key not in self.last_seen:
            self.last_seen[key] = {}
        self.last_seen[key][track_id] = frame_number

    def count(self, key, frame_number):
        ids = self.last_seen.get(key, {})

        # forget objects that disappeared
        for track_id in list(ids.keys()):
            if frame_number - ids[track_id] > self.window:
                del ids[track_id]

        return len(ids)
