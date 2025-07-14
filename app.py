import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import math
import streamlit as st
import time

# Helper distance function to calculate Euclidean distance between two points
def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])

# Initialize stroke buffers for each color as lists of deques (strokes)
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]

# Index trackers for the current stroke in each color buffer
blue_index = green_index = red_index = yellow_index = 0

# Define colors in BGR format for OpenCV
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]

# Current color index (0=Blue,1=Green,2=Red,3=Yellow)
colorIndex = 0

# Initialize white canvas (paint window)
paintWindow = np.ones((480, 640, 3), dtype=np.uint8) * 255

# MediaPipe hands model setup
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Button regions for UI (x1, y1, x2) along top of screen
button_regions = [(40, 1, 140), (160, 1, 255), (275, 1, 370), (390, 1, 485), (505, 1, 600)]
button_labels = ["CLEAR", "BLUE", "GREEN", "RED", "YELLOW"]
button_colors = [(200, 200, 200)] + colors  # Gray for CLEAR + colors

def draw_buttons(frame, paintWindow, highlight=None):
    """
    Draws buttons on both the camera frame and paint window.
    Highlights the selected button.
    """
    for idx, ((x1, y1, x2), clr, lbl) in enumerate(zip(button_regions, button_colors, button_labels)):
        filled = (highlight == idx)
        # Draw filled rectangle on camera frame
        cv2.rectangle(frame, (x1, y1), (x2, 65), clr, -1)
        # Draw border rectangle (thicker if highlighted)
        thickness = 3 if filled else 2
        cv2.rectangle(frame, (x1, y1), (x2, 65), (0, 0, 0), thickness)
        # Text color black for CLEAR, white for others
        txt_color = (0, 0, 0) if idx == 0 else (255, 255, 255)
        cv2.putText(frame, lbl, (x1 + 10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, txt_color, 2)

        # Draw same buttons on paintWindow without highlight
        cv2.rectangle(paintWindow, (x1, y1), (x2, 65), clr, -1)
        cv2.rectangle(paintWindow, (x1, y1), (x2, 65), (0, 0, 0), 2)
        cv2.putText(paintWindow, lbl, (x1 + 10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, txt_color, 2)

# Streamlit app title
st.title("Hand Gesture Paint Application")

# Run loop - use Streamlit button to control start/stop (optional)
run = st.checkbox("Run Painting", value=True)

while run:
    ret, frame = cap.read()
    if not ret:
        st.warning("Failed to capture from camera.")
        break

    # Flip frame horizontally for natural interaction
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame with MediaPipe hands model
    result = hands.process(rgb)

    highlight = -1  # No button highlighted initially

    if result.multi_hand_landmarks:
        lm = result.multi_hand_landmarks[0]
        # Extract landmark coordinates scaled to image size
        coords = [(int(pt.x * w), int(pt.y * h)) for pt in lm.landmark]
        idx, thumb = coords[8], coords[4]  # Index fingertip and thumb tip

        # Draw hand landmarks on frame
        mpDraw.draw_landmarks(frame, lm, mpHands.HAND_CONNECTIONS)

        # Draw circle cursor at index finger tip
        cv2.circle(frame, idx, 12, colors[colorIndex], -1)
        cv2.circle(frame, idx, 14, (0, 0, 0), 2)

        # Detect pinch gesture (index and thumb close together)
        if dist(idx, thumb) < 40:
            # Lift pen: start new stroke for all colors to avoid connecting lines
            bpoints.append(deque(maxlen=512)); blue_index += 1
            gpoints.append(deque(maxlen=512)); green_index += 1
            rpoints.append(deque(maxlen=512)); red_index += 1
            ypoints.append(deque(maxlen=512)); yellow_index += 1
            st.write("Pen lifted - starting new stroke")

        # Detect if finger is near top UI buttons area
        elif idx[1] < 65:
            x = idx[0]
            # Check which button region the finger is in and update accordingly
            if 40 <= x <= 140:
                # CLEAR button pressed - reset everything
                colorIndex = 0
                bpoints = [deque(maxlen=1024)]
                gpoints = [deque(maxlen=1024)]
                rpoints = [deque(maxlen=1024)]
                ypoints = [deque(maxlen=1024)]
                blue_index = green_index = red_index = yellow_index = 0
                paintWindow[:] = 255
                st.write("Canvas cleared")
                highlight = 0
            elif 160 <= x <= 255:
                colorIndex = 0
                highlight = 1
            elif 275 <= x <= 370:
                colorIndex = 1
                highlight = 2
            elif 390 <= x <= 485:
                colorIndex = 2
                highlight = 3
            elif 505 <= x <= 600:
                colorIndex = 3
                highlight = 4

        else:
            # Add current index finger position to the corresponding color stroke deque
            if colorIndex == 0:
                bpoints[blue_index].appendleft(idx)
            elif colorIndex == 1:
                gpoints[green_index].appendleft(idx)
            elif colorIndex == 2:
                rpoints[red_index].appendleft(idx)
            elif colorIndex == 3:
                ypoints[yellow_index].appendleft(idx)

    else:
        # No hand detected, lift pen (start new strokes)
        bpoints.append(deque(maxlen=512)); blue_index += 1
        gpoints.append(deque(maxlen=512)); green_index += 1
        rpoints.append(deque(maxlen=512)); red_index += 1
        ypoints.append(deque(maxlen=512)); yellow_index += 1

    # Draw buttons on both frame and paintWindow
    draw_buttons(frame, paintWindow, highlight)

    # Draw all strokes from all buffers onto both frame and paintWindow
    for pts, clr in zip([bpoints, gpoints, rpoints, ypoints], colors):
        for stroke in pts:
            for i in range(1, len(stroke)):
                if stroke[i - 1] and stroke[i]:
                    cv2.line(frame, stroke[i - 1], stroke[i], clr, 4)
                    cv2.line(paintWindow, stroke[i - 1], stroke[i], clr, 4)

    # Display the camera frame with hand detection and drawing UI
    st.image(frame, channels="BGR", caption="Output (Camera feed)")

    # Display the paint canvas
    st.image(paintWindow, channels="BGR", caption="Paint Canvas")

    # Small delay to control frame rate (~30 FPS)
    time.sleep(0.03)

# Release camera and cleanup when loop ends
cap.release()
