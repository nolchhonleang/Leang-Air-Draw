Leang-Air-Draw
Leang-Air-Draw is a hand-tracking drawing application that lets you draw, move, and erase on a digital canvas using finger gestures, powered by MediaPipe and OpenCV. This project features a sleek, neon-themed UI and supports multiple hands for collaborative drawing.
Author: Nol ChhonleangProject: Leang-Air-DrawDate: August 2025
Features

Draw: Use a thumb-index pinch or pointer gesture to draw lines in multiple colors.
Move: Use a thumb-middle pinch to move the entire drawing.
Erase: Toggle eraser mode to remove parts of the drawing.
Customize: Adjust brush size, opacity, and color via a settings panel.
Undo/Clear: Undo up to 10 actions or clear the canvas.
Save: Save your artwork as a PNG file.
Multi-Hand Support: Up to four hands can draw or move independently.

Prerequisites

Python 3.7+
A webcam for hand tracking
Dependencies:
opencv-python
numpy
mediapipe
pillow



Installation

Clone the repository:git clone https://github.com/nolchhonleang/Leang-Air-Draw.git
cd Leang-Air-Draw


Install dependencies:pip install opencv-python numpy mediapipe pillow


Ensure your webcam is connected and functional.

Usage

Run the application:
python leang_air_draw.py


The interface consists of:

Left Panel: Displays the camera feed and your drawings.
Right Panel: Settings for modes, brush, and colors.


Drawing:

Ensure "Draw: ON" in the "Modes" section (default).
Pinch Mode: Pinch your thumb and index finger to draw.
Pointer Mode: Extend your index finger while keeping other fingers down.
Adjust brush size (5-60px) and opacity (0.1-1.0) in the "Brush" section.
Select a color from the palette or click "Pick Color" in the "Colors" section.


Moving:

Click "Move: OFF" to turn it ON (this sets "Draw: OFF").
Pinch your thumb and middle finger, then move your hand to shift the drawing.
Click "Move: ON" to turn it OFF (this sets "Draw: ON").


Erasing:

Click "Eraser: OFF" to turn it ON in the "Modes" section.
Draw over lines to erase them (same gesture as drawing).


Other Actions:

Undo: Revert the last draw or move action (up to 10).
Clear: Reset the canvas (undoable).
Save: Save the canvas as a PNG file (e.g., drawing_20250822_141500.png).
Reset Colors: Revert to default colors in the "Colors" section.



Notes

Ensure good lighting and a clear camera view for accurate hand tracking.
The application supports up to four hands, each assigned a different color.
Saved images combine the camera feed and drawings with 0.6/0.4 transparency.
The UI features a dark, neon theme for a modern look.

Example

Run python leang_air_draw.py.
Draw a red line using a thumb-index pinch.
Click "Move: OFF" to ON, then use a thumb-middle pinch to move the line.
Click "Eraser: ON" to erase parts of the line.
Click "Save" to export your artwork.

Social Media Sharing
Share your project with pride! Here’s a suggested post:

🎨 Excited to share my project, Leang-Air-Draw! Draw and move artwork in the air using hand gestures, powered by MediaPipe and OpenCV. Check it out on GitHub: (https://github.com/nolchhonleang). Created by Nol Chhonleang. #Python #ComputerVision #CreativeCoding

License
This project is open-source and available for non-commercial use. Please credit Nol Chhonleang when sharing or modifying.

Created by Nol Chhonleang

<img width="1280" height="787" alt="image" src="https://github.com/user-attachments/assets/c7b39be7-9de1-410a-b6ea-2da55da45ffa" />
<img width="1280" height="800" alt="image" src="https://github.com/user-attachments/assets/d9221e70-b66e-4afc-8e42-c0030a2bd279" />

