
import cv2

def draw_event(frame, text):

    cv2.rectangle(frame, (20,20), (600,80), (0,0,255), -1)

    cv2.putText(
        frame,
        text,
        (40,60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255,255,255),
        3
    )

def draw_bbox(frame, bbox, label):

    x1, y1, x2, y2 = bbox

    cv2.rectangle(
        frame,
        (x1,y1),
        (x2,y2),
        (0,255,0),
        2
    )

    cv2.putText(
        frame,
        label,
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0,255,0),
        2
    )
