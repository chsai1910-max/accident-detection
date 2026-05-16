
from collections import defaultdict
import math

class TrackerStateManager:

    def __init__(self):
        self.history = defaultdict(list)
        self.speed_history = defaultdict(list)

    def update_object(self, object_id, bbox):

        x1, y1, x2, y2 = bbox

        cx = int((x1 + x2) / 2)
        cy = int(y2)

        self.history[object_id].append((cx, cy))

        if len(self.history[object_id]) > 30:
            self.history[object_id].pop(0)

        speed = self.compute_speed(object_id)

        self.speed_history[object_id].append(speed)

        return {
            "position": (cx, cy),
            "trajectory": self.history[object_id],
            "speed": speed
        }

    def compute_speed(self, object_id):

        pts = self.history[object_id]

        if len(pts) < 2:
            return 0

        x1, y1 = pts[-2]
        x2, y2 = pts[-1]

        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
