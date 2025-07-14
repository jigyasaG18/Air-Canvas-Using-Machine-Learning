import cv2, numpy as np
import mediapipe as mp
from collections import deque
import math

# Helper distance function
def dist(p, q): return math.hypot(p[0]-q[0], p[1]-q[1])

# Stroke buffers
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]
blue_index = green_index = red_index = yellow_index = 0
colors = [(255,0,0),(0,255,0),(0,0,255),(0,255,255)]
colorIndex = 0

# Canvas setup
paintWindow = np.ones((480,640,3),dtype=np.uint8)*255
cv2.namedWindow('Paint',cv2.WINDOW_AUTOSIZE)

# MediaPipe setup
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1,min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Camera setup
cap = cv2.VideoCapture(0)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Button regions and labels - for reuse
button_regions = [(40,1,140), (160,1,255), (275,1,370), (390,1,485), (505,1,600)]
button_labels = ["CLEAR","BLUE","GREEN","RED","YELLOW"]
button_colors = [(200,200,200)] + colors  # Gray fill for CLEAR, colors for others

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame,1)
    rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    # UI: filled button highlight
    def draw_buttons(highlight=None):
        for idx, ((x1,y1,x2), clr, lbl) in enumerate(zip(button_regions, button_colors, button_labels)):
            filled = (highlight==idx)
            # Draw filled rect on frame
            cv2.rectangle(frame,(x1,y1),(x2,65),clr,-1)
            # Draw border rect on frame (thickness=3 for highlight else 2)
            thickness = 3 if filled else 2
            cv2.rectangle(frame,(x1,y1),(x2,65),(0,0,0),thickness)
            # Text color: black for CLEAR, white for colors
            txt_color = (0,0,0) if idx==0 else (255,255,255)
            cv2.putText(frame,lbl,(x1+10,40), cv2.FONT_HERSHEY_SIMPLEX,0.6, txt_color,2)

            # Also draw same buttons on paintWindow (no highlight)
            cv2.rectangle(paintWindow,(x1,y1),(x2,65),clr,-1)
            cv2.rectangle(paintWindow,(x1,y1),(x2,65),(0,0,0),2)
            cv2.putText(paintWindow,lbl,(x1+10,40), cv2.FONT_HERSHEY_SIMPLEX,0.6, txt_color,2)

    highlight = -1

    if result.multi_hand_landmarks:
        lm = result.multi_hand_landmarks[0]
        coords = [(int(pt.x*w), int(pt.y*h)) for pt in lm.landmark]
        idx, thumb = coords[8], coords[4]

        mpDraw.draw_landmarks(frame,lm,mpHands.HAND_CONNECTIONS)

        # Draw cursor
        cv2.circle(frame, idx, 12, colors[colorIndex], -1)
        cv2.circle(frame, idx, 14, (0,0,0),2)

        # Pinch = clear buffer
        if dist(idx, thumb)<40:
            bpoints.append(deque(maxlen=512)); blue_index+=1
            gpoints.append(deque(maxlen=512)); green_index+=1
            rpoints.append(deque(maxlen=512)); red_index+=1
            ypoints.append(deque(maxlen=512)); yellow_index+=1
            print("Pen Lifted – starting new stroke")

        # Finger at the top => possible button interaction
        elif idx[1]<65:
            x = idx[0]
            if 40<=x<=140:
                colorIndex=0; bpoints=[deque(maxlen=1024)]; gpoints=[deque(maxlen=1024)]; rpoints=[deque(maxlen=1024)]; ypoints=[deque(maxlen=1024)]
                blue_index = green_index = red_index = yellow_index = 0
                paintWindow[:] = 255
                print("Canvas Cleared")
                highlight=0
            elif 160<=x<=255: colorIndex=0; highlight=1
            elif 275<=x<=370: colorIndex=1; highlight=2
            elif 390<=x<=485: colorIndex=2; highlight=3
            elif 505<=x<=600: colorIndex=3; highlight=4

        # Draw mode
        else:
            if colorIndex==0: bpoints[blue_index].appendleft(idx)
            elif colorIndex==1: gpoints[green_index].appendleft(idx)
            elif colorIndex==2: rpoints[red_index].appendleft(idx)
            elif colorIndex==3: ypoints[yellow_index].appendleft(idx)

    else:
        bpoints.append(deque(maxlen=512)); blue_index+=1
        gpoints.append(deque(maxlen=512)); green_index+=1
        rpoints.append(deque(maxlen=512)); red_index+=1
        ypoints.append(deque(maxlen=512)); yellow_index+=1

    # Redraw button UI with borders on both screens
    draw_buttons(highlight)

    # Draw strokes
    for pts, clr in zip([bpoints,gpoints,rpoints,ypoints], colors):
        for stroke in pts:
            for i in range(1,len(stroke)):
                if stroke[i-1] and stroke[i]:
                    cv2.line(frame,stroke[i-1],stroke[i],clr,4)
                    cv2.line(paintWindow,stroke[i-1],stroke[i],clr,4)

    st.image(frame, channels="BGR", caption="Output")
    st.image(paintWindow, channels="BGR", caption="Paint")

   # Add a short sleep to avoid freezing or overloading UI
   time.sleep(0.03)  # ~30 FPS


cap.release()
cv2.destroyAllWindows()
