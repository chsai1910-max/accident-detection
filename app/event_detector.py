
# import math
# from collections import defaultdict

# class EventDetector:

#     def __init__(self):

#         self.stationary_count = defaultdict(int)

#     def evaluate(self, frame_number, objects):

#         events = []

#         for obj in objects:

#             speed = obj["speed"]
#             object_id = obj["id"]

#             if speed < 1.5:
#                 self.stationary_count[object_id] += 1
#             else:
#                 self.stationary_count[object_id] = 0

#             score = 0

#             if speed < 1:
#                 score += 2

#             if self.stationary_count[object_id] > 40:
#                 score += 3

#             for other in objects:

#                 if other["id"] == object_id:
#                     continue

#                 d = self.distance(
#                     obj["position"],
#                     other["position"]
#                 )

#                 if d < 80:
#                     score += 2

#             if score >= 5:
#                 events.append({
#                     "frame": frame_number,
#                     "event": "possible_accident",
#                     "severity": score,
#                     "object_id": object_id
#                 })

#         return events

#     def distance(self, p1, p2):

#         return math.sqrt(
#             (p1[0]-p2[0])**2 +
#             (p1[1]-p2[1])**2
#         )




# from collections import defaultdict
# from math import sqrt


# class EventDetector:

#     def __init__(self):

#         self.IOU_THRESHOLD = 0.40

#         self.MIN_PERSISTENCE = 25

#         self.MAX_MOVEMENT_AFTER_COLLISION = 12

#         self.COOLDOWN = 150

#         self.collision_frames = defaultdict(int)

#         self.last_positions = {}

#         self.triggered = {}

#     def evaluate(
#         self,
#         frame_num,
#         objects
#     ):

#         events = []

#         current_positions = {}

#         for obj in objects:

#             x1, y1, x2, y2 = obj["bbox"]

#             cx = (x1 + x2) / 2
#             cy = (y1 + y2) / 2

#             current_positions[obj["id"]] = (
#                 cx,
#                 cy
#             )

#         for i in range(len(objects)):

#             for j in range(i + 1, len(objects)):

#                 obj1 = objects[i]
#                 obj2 = objects[j]

#                 if obj1["class"] not in [
#                     "Car",
#                     "Truck",
#                     "Bus"
#                 ]:
#                     continue

#                 if obj2["class"] not in [
#                     "Car",
#                     "Truck",
#                     "Bus"
#                 ]:
#                     continue

#                 pair = tuple(
#                     sorted([
#                         obj1["id"],
#                         obj2["id"]
#                     ])
#                 )

#                 iou = self.calculate_iou(
#                     obj1["bbox"],
#                     obj2["bbox"]
#                 )

#                 # VERY STRICT OVERLAP
#                 if iou < 0.45:

#                     self.collision_frames[pair] = 0
#                     continue

#                 movement1 = self.compute_movement(
#                     obj1["id"],
#                     current_positions
#                 )

#                 movement2 = self.compute_movement(
#                     obj2["id"],
#                     current_positions
#                 )

#                 # BOTH MUST ALMOST STOP
#                 if movement1 > 4:
#                     continue

#                 if movement2 > 4:
#                     continue

#                 self.collision_frames[pair] += 1

#                 # MUST REMAIN STUCK
#                 if self.collision_frames[pair] < 30:
#                     continue

#                 # cooldown
#                 if pair in self.triggered:

#                     if (
#                         frame_num -
#                         self.triggered[pair]
#                     ) < 300:
#                         continue

#                 severity = min(
#                     10,
#                     int(iou * 20)
#                 )

#                 events.append({

#                     "frame": frame_num,

#                     "event": "ACCIDENT_DETECTED",

#                     "severity": severity,

#                     "vehicles": [
#                         obj1["id"],
#                         obj2["id"]
#                     ]
#                 })

#                 self.triggered[pair] = frame_num

#         self.last_positions = current_positions

#         return events

#     # def evaluate(
#     #     self,
#     #     frame_num,
#     #     objects
#     # ):

#     #     events = []

#     #     current_positions = {}

#     #     for obj in objects:

#     #         x1, y1, x2, y2 = obj["bbox"]

#     #         cx = (x1 + x2) / 2
#     #         cy = (y1 + y2) / 2

#     #         current_positions[obj["id"]] = (
#     #             cx,
#     #             cy
#     #         )

#     #     for i in range(len(objects)):

#     #         for j in range(i + 1, len(objects)):

#     #             obj1 = objects[i]
#     #             obj2 = objects[j]

#     #             if obj1["class"] not in [
#     #                 "Car",
#     #                 "Truck",
#     #                 "Bus"
#     #             ]:
#     #                 continue

#     #             if obj2["class"] not in [
#     #                 "Car",
#     #                 "Truck",
#     #                 "Bus"
#     #             ]:
#     #                 continue

#     #             pair = tuple(
#     #                 sorted([
#     #                     obj1["id"],
#     #                     obj2["id"]
#     #                 ])
#     #             )

#     #             iou = self.calculate_iou(
#     #                 obj1["bbox"],
#     #                 obj2["bbox"]
#     #             )

#     #             if iou < self.IOU_THRESHOLD:

#     #                 self.collision_frames[pair] = 0
#     #                 continue

#     #             self.collision_frames[pair] += 1

#     #             if (
#     #                 self.collision_frames[pair]
#     #                 < self.MIN_PERSISTENCE
#     #             ):
#     #                 continue

#     #             # cooldown
#     #             if pair in self.triggered:

#     #                 if (
#     #                     frame_num -
#     #                     self.triggered[pair]
#     #                 ) < self.COOLDOWN:
#     #                     continue

#     #             movement1 = self.compute_movement(
#     #                 obj1["id"],
#     #                 current_positions
#     #             )

#     #             movement2 = self.compute_movement(
#     #                 obj2["id"],
#     #                 current_positions
#     #             )

#     #             # BOTH vehicles nearly stationary
#     #             if (
#     #                 movement1 >
#     #                 self.MAX_MOVEMENT_AFTER_COLLISION
#     #             ):
#     #                 continue

#     #             if (
#     #                 movement2 >
#     #                 self.MAX_MOVEMENT_AFTER_COLLISION
#     #             ):
#     #                 continue

#     #             severity = min(
#     #                 10,
#     #                 int(iou * 20)
#     #             )

#     #             events.append({

#     #                 "frame": frame_num,

#     #                 "event": "ACCIDENT_DETECTED",

#     #                 "severity": severity,

#     #                 "vehicles": [
#     #                     obj1["id"],
#     #                     obj2["id"]
#     #                 ]
#     #             })

#     #             self.triggered[pair] = frame_num

#     #     self.last_positions = current_positions

#     #     return events

#     def compute_movement(
#         self,
#         object_id,
#         current_positions
#     ):

#         if object_id not in self.last_positions:
#             return 9999

#         if object_id not in current_positions:
#             return 9999

#         x1, y1 = self.last_positions[
#             object_id
#         ]

#         x2, y2 = current_positions[
#             object_id
#         ]

#         return sqrt(
#             ((x2 - x1) ** 2) +
#             ((y2 - y1) ** 2)
#         )

#     def calculate_iou(
#         self,
#         boxA,
#         boxB
#     ):

#         xA = max(boxA[0], boxB[0])
#         yA = max(boxA[1], boxB[1])
#         xB = min(boxA[2], boxB[2])
#         yB = min(boxA[3], boxB[3])

#         inter_w = max(0, xB - xA)
#         inter_h = max(0, yB - yA)

#         inter_area = inter_w * inter_h

#         if inter_area <= 0:
#             return 0

#         areaA = (
#             (boxA[2] - boxA[0]) *
#             (boxA[3] - boxA[1])
#         )

#         areaB = (
#             (boxB[2] - boxB[0]) *
#             (boxB[3] - boxB[1])
#         )

#         union = (
#             areaA +
#             areaB -
#             inter_area
#         )

#         if union <= 0:
#             return 0

#         return inter_area / union





from collections import defaultdict
from math import sqrt, atan2, degrees


class EventDetector:

    def __init__(self):

        self.history = defaultdict(list)

        self.collision_frames = defaultdict(int)

        self.triggered = {}

        self.COOLDOWN = 300

    def evaluate(
        self,
        frame_num,
        objects
    ):

        events = []

        current = {}

        for obj in objects:

            x1, y1, x2, y2 = obj["bbox"]

            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            current[obj["id"]] = (
                cx,
                cy
            )

            self.history[obj["id"]].append(
                (cx, cy)
            )

            if len(self.history[obj["id"]]) > 10:
                self.history[obj["id"]].pop(0)

        for i in range(len(objects)):

            for j in range(i + 1, len(objects)):

                obj1 = objects[i]
                obj2 = objects[j]

                if obj1["class"] not in [
                    "Car",
                    "Truck",
                    "Bus"
                ]:
                    continue

                if obj2["class"] not in [
                    "Car",
                    "Truck",
                    "Bus"
                ]:
                    continue

                pair = tuple(
                    sorted([
                        obj1["id"],
                        obj2["id"]
                    ])
                )

                iou = self.calculate_iou(
                    obj1["bbox"],
                    obj2["bbox"]
                )

                if iou < 0.45:

                    self.collision_frames[pair] = 0
                    continue

                speed1 = self.compute_speed(
                    obj1["id"]
                )

                speed2 = self.compute_speed(
                    obj2["id"]
                )

                angle_change1 = self.compute_direction_change(
                    obj1["id"]
                )

                angle_change2 = self.compute_direction_change(
                    obj2["id"]
                )

                # both almost stopped
                if speed1 > 4:
                    continue

                if speed2 > 4:
                    continue

                # at least one abrupt direction change
                if (
                    angle_change1 < 35 and
                    angle_change2 < 35
                ):
                    continue

                self.collision_frames[pair] += 1

                if self.collision_frames[pair] < 30:
                    continue

                if pair in self.triggered:

                    if (
                        frame_num -
                        self.triggered[pair]
                    ) < self.COOLDOWN:
                        continue

                confidence = min(
                    0.99,
                    (
                        (iou * 0.5) +
                        (max(
                            angle_change1,
                            angle_change2
                        ) / 180)
                    )
                )

                events.append({

                    "frame": frame_num,

                    "event": "ACCIDENT_DETECTED",

                    "confidence": round(
                        confidence,
                        2
                    ),

                    "vehicles": [
                        obj1["id"],
                        obj2["id"]
                    ]
                })

                self.triggered[pair] = frame_num

        return events

    def compute_speed(
        self,
        object_id
    ):

        pts = self.history[object_id]

        if len(pts) < 2:
            return 999

        x1, y1 = pts[-2]
        x2, y2 = pts[-1]

        return sqrt(
            ((x2 - x1) ** 2) +
            ((y2 - y1) ** 2)
        )

    def compute_direction_change(
        self,
        object_id
    ):

        pts = self.history[object_id]

        if len(pts) < 4:
            return 0

        x1, y1 = pts[-4]
        x2, y2 = pts[-3]
        x3, y3 = pts[-2]
        x4, y4 = pts[-1]

        angle1 = degrees(
            atan2(
                y2 - y1,
                x2 - x1
            )
        )

        angle2 = degrees(
            atan2(
                y4 - y3,
                x4 - x3
            )
        )

        return abs(
            angle2 - angle1
        )

    def calculate_iou(
        self,
        boxA,
        boxB
    ):

        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        inter_w = max(0, xB - xA)
        inter_h = max(0, yB - yA)

        inter_area = inter_w * inter_h

        if inter_area <= 0:
            return 0

        areaA = (
            (boxA[2] - boxA[0]) *
            (boxA[3] - boxA[1])
        )

        areaB = (
            (boxB[2] - boxB[0]) *
            (boxB[3] - boxB[1])
        )

        union = (
            areaA +
            areaB -
            inter_area
        )

        if union <= 0:
            return 0

        return inter_area / union