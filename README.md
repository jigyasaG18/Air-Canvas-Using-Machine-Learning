# ✋🎨 Air Canvas using Machine Learning

Welcome to **Air Canvas**, a computer vision-based virtual painting application that allows users to draw in the air using hand gestures. Powered by **MediaPipe** for hand tracking and **OpenCV** for image processing, this interactive project offers a touchless, intuitive digital drawing experience — perfect for education, entertainment, and creative prototyping.

---

## 📌 Table of Contents

* [📖 Overview](#-overview)
* [💡 Features](#-features)
* [🧠 How It Works](#-how-it-works)
* [🔧 Dependencies](#-dependencies)
* [📁 Project Structure](#-project-structure)
* [🖼️ User Interface Overview](#-user-interface-overview)
* [🖐️ Gesture Mechanics](#-gesture-mechanics)
* [🎯 Use Cases](#-use-cases)
* [⚠️ Limitations](#-limitations)
* [🚀 Future Improvements](#-future-improvements)

---

## 📖 Overview

**Air Canvas** is an AI-driven virtual canvas that enables users to draw on screen by waving their fingers in the air, without any physical contact or touch screen. This is achieved through real-time hand tracking and gesture recognition using **MediaPipe** — a powerful ML solution by Google.

The system detects the movement of your index finger and tracks it to draw colored strokes on a canvas. You can also change colors or clear the canvas using gesture-based buttons displayed at the top of the screen.

This project is especially useful in the domains of **gesture-based HCI (Human-Computer Interaction)**, **AI-enabled art tools**, and **contactless design interfaces**.

---

## 💡 Features

* 👆 **Finger-based Air Drawing**
  Uses your index finger as a pen to draw freely in the air.

* 🎨 **Color Selection Panel**
  Switch between multiple colors using virtual buttons on-screen.

* ❌ **Clear Canvas Button**
  A touchless "CLEAR" option to erase all drawings with a single gesture.

* 🤏 **Gesture-based Stroke Separation**
  Pinch gesture (thumb + index finger) is recognized as "pen lift" to start a new stroke.

* 🧠 **Real-time Hand Tracking**
  Uses MediaPipe’s ML-based hand detection for accurate tracking.

* 📷 **Live Camera Feed Overlay**
  The user sees both the canvas and their live feed with drawn landmarks.

---

## 🧠 How It Works

### 🔍 1. **Hand Detection and Landmark Recognition**

The system uses **MediaPipe Hands**, which detects and tracks 21 hand landmarks in real-time. Once a hand is detected, the coordinates of the **index finger tip** and **thumb tip** are extracted.

### 🎯 2. **Gesture Interpretation**

* **Index Finger Tip Movement** → used to paint.
* **Index & Thumb Proximity** → interpreted as "pen lift".
* **Finger at Top Edge** → interpreted as interaction with color selection buttons.

### 🖼️ 3. **Drawing Mechanism**

A `deque` (double-ended queue) buffer stores the coordinates of the drawing strokes, and lines are drawn between consecutive points. Separate buffers are maintained for each color to manage undo-like behavior without merging all data.

### 🧰 4. **UI Elements**

Color and CLEAR buttons are drawn at the top of the screen and replicated both on the live feed and the actual drawing canvas (`paintWindow`). These virtual buttons respond to the X-Y position of the index finger if it hovers over them.

---

## 🔧 Dependencies

This project requires the following Python libraries:

* **OpenCV (cv2)** – For image processing and GUI
* **MediaPipe** – For hand tracking and landmark recognition
* **NumPy** – For matrix and image data handling
* **collections.deque** – Efficient drawing history management

Installation can be done using:

```bash
pip install opencv-python mediapipe numpy
```

---

## 📁 Project Structure

```
air-canvas/
│
├── air_canvas.py         # Main script with drawing logic and MediaPipe hand tracking
├── README.md             # Project documentation
└── requirements.txt      # Dependency list
```

---

## 🖼️ User Interface Overview

The UI is divided into two main components:

### 🎥 1. **Live Video Feed ("Output")**

* Shows the user’s webcam feed.
* Hand landmarks and drawing strokes are overlaid.
* Button panel appears at the top (CLEAR, BLUE, GREEN, RED, YELLOW).

### 🖌️ 2. **Paint Window**

* A separate window that displays the strokes without the webcam feed.
* Ideal for saving as an artwork or exporting.

---

## 🖐️ Gesture Mechanics

| Gesture               | Action                      |
| --------------------- | --------------------------- |
| Index Finger Movement | Draw on canvas              |
| Index + Thumb Pinch   | Lift pen (start new stroke) |
| Index at Top Buttons  | Select color / clear canvas |
| 'Q' Key Press         | Exit the application        |

---

## 🎯 Use Cases

* **Educational Tools**: Teaching drawing, handwriting, or STEM without whiteboards or physical markers.
* **Gesture-based Interfaces**: Prototyping HCI systems that rely on touchless controls.
* **Creative Expression**: Artists can draw or doodle using only hand gestures.
* **Therapy & Accessibility**: Alternative input methods for users with physical limitations.

---

## ⚠️ Limitations

* **Lighting Dependency**: Poor lighting may affect hand detection accuracy.
* **Single-Hand Operation**: Currently supports only one hand for interaction.
* **Lack of Undo Feature**: No built-in undo; you can only clear or continue drawing.
* **No Saving Option**: Canvas output must be saved manually (via screenshot or code extension).

---

## 🚀 Future Improvements

* ✅ Add multi-hand support for dual tool interaction.
* 💾 Implement image saving and loading features.
* 🔄 Add undo/redo buffer for better control.
* ✨ Improve gesture variety (e.g., two-finger zoom, erase).
* 📱 Port to mobile devices or integrate with AR frameworks.

---
