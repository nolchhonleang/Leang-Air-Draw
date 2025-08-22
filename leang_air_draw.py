"""
Leang-Air-Draw
A hand-tracking drawing application using MediaPipe and OpenCV.
Author: Nol Chhonleang
Project: Leang-Air-Draw
Date: August 2025
"""

import cv2
import numpy as np
import mediapipe as mp
import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk
from datetime import datetime
import math

# --- Hand Tracking ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=4, min_detection_confidence=0.7)

# --- Variables ---
user_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
brush_thickness = 15
brush_opacity = 0.8
prev_points = {}           # {hand_id: (x,y) or None}
drawing_layer = None       # numpy array (H, W, 3) BGR
pinch_threshold = 0.04
use_pinch_mode = True
undo_stack = []
is_eraser = False
is_drawing_enabled = True
is_move_mode = False       # Move mode toggle
max_undo = 10
last_combined = None       # store last combined frame (BGR) for saving
last_frame = None
prev_move_points = {}      # {hand_id: (x,y) or None} for moving

# --- Tkinter GUI ---
root = tk.Tk()
root.title("Leang-Air-Draw")
root.geometry("1200x800")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=('Helvetica', 10, 'bold'), foreground='white', background='#3a3a3a', padding=6, borderwidth=0)
style.map('TButton', background=[('active', '#5a5a5a')], foreground=[('active', 'white')], relief=[('active', 'flat')])
style.configure('TScale', background='#1e1e1e', troughcolor='#4a4a4a', sliderlength=15, borderwidth=0)
style.configure('TLabel', background='#1e1e1e', foreground='white', font=('Helvetica', 10))
style.configure('TFrame', background='#2a2a2a')

main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Left Frame: Camera + Canvas
camera_frame = tk.Frame(main_frame, bg="#1e1e1e", highlightthickness=2, highlightbackground="#4a4a4a")
camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

canvas = tk.Canvas(camera_frame, width=800, height=600, bg="#111111", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

canvas.update_idletasks()
canvas_width = canvas.winfo_width()
canvas_height = canvas.winfo_height()

# Right Frame: Settings
settings_frame = tk.Frame(main_frame, bg="#2a2a2a", width=250, relief=tk.RAISED, borderwidth=2)
settings_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 8))
settings_frame.pack_propagate(False)

title_label = ttk.Label(settings_frame, text="Leang-Air-Draw by Nol Chhonleang", font=("Helvetica", 14, "bold"))
title_label.pack(pady=5)

# Brush preview
preview_canvas = tk.Canvas(settings_frame, width=60, height=60, bg="#2a2a2a", highlightthickness=1, highlightbackground="#4a4a4a")
preview_canvas.pack(pady=5)

def update_brush_preview():
    preview_canvas.delete("all")
    size = int(thickness_slider.get())
    base_color = user_colors[0]
    hex_color = '#%02x%02x%02x' % base_color
    r = 30
    preview_canvas.create_oval(r - size/2, r - size/2, r + size/2, r + size/2, fill=hex_color, outline="")

def clear_canvas():
    global drawing_layer, undo_stack
    if drawing_layer is None:
        return
    undo_stack.append(drawing_layer.copy())
    if len(undo_stack) > max_undo:
        undo_stack.pop(0)
    drawing_layer[:, :, :] = 0
    canvas.delete("all")
    update_status("Canvas cleared")

def undo_last():
    global drawing_layer
    if undo_stack:
        drawing_layer = undo_stack.pop()
        update_status("Undo performed")
    else:
        update_status("Nothing to undo")

def choose_color():
    global user_colors
    color_code = colorchooser.askcolor(title="Pick Color")
    if color_code and color_code[0]:
        rgb = tuple(int(c) for c in color_code[0])
        user_colors[0] = rgb
        update_brush_preview()
        update_status("Color updated")

def reset_colors():
    global user_colors
    user_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    update_brush_preview()
    update_status("Colors reset to default")

def save_canvas():
    global last_combined
    if last_combined is None:
        update_status("Nothing to save")
        return
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"drawing_{now}.png"
    cv2.imwrite(filename, last_combined)
    update_status(f"Saved: {filename}")

def toggle_mode():
    global use_pinch_mode
    use_pinch_mode = not use_pinch_mode
    mode_button.config(text="Pinch" if use_pinch_mode else "Pointer")
    update_status(f"Mode: {'Pinch' if use_pinch_mode else 'Pointer'}")

def toggle_eraser():
    global is_eraser
    is_eraser = not is_eraser
    eraser_button.config(text="Eraser: ON" if is_eraser else "Eraser: OFF")
    update_status(f"Eraser: {'ON' if is_eraser else 'OFF'}")
    update_brush_preview()

def toggle_drawing():
    global is_drawing_enabled, is_move_mode
    is_drawing_enabled = not is_drawing_enabled
    drawing_button.config(text="Draw: ON" if is_drawing_enabled else "Draw: OFF")
    is_move_mode = not is_drawing_enabled
    move_button.config(text="Move: ON" if is_move_mode else "Move: OFF")
    update_status(f"Draw: {'ON' if is_drawing_enabled else 'OFF'}, Move: {'ON' if is_move_mode else 'OFF'}")

def toggle_move_mode():
    global is_move_mode, is_drawing_enabled
    is_move_mode = not is_move_mode
    move_button.config(text="Move: ON" if is_move_mode else "Move: OFF")
    is_drawing_enabled = not is_move_mode
    drawing_button.config(text="Draw: ON" if is_drawing_enabled else "Draw: OFF")
    update_status(f"Move: {'ON' if is_move_mode else 'OFF'}, Draw: {'ON' if is_drawing_enabled else 'OFF'}")

def create_color_palette():
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (0, 255, 255), (255, 0, 255)
    ]
    palette_frame = tk.Frame(settings_frame, bg="#2a2a2a")
    palette_frame.pack(pady=5, fill=tk.X)
    def make_cmd(c):
        return lambda: (set_color(c), update_brush_preview(), update_status("Color changed"))
    for i, color in enumerate(colors):
        hexc = '#%02x%02x%02x' % color
        btn = tk.Button(palette_frame, bg=hexc, width=2, height=1, command=make_cmd(color), relief="flat", bd=1, highlightthickness=1, highlightbackground="#4a4a4a")
        btn.grid(row=i//3, column=i%3, padx=3, pady=3, sticky="ew")
    palette_frame.grid_columnconfigure((0,1,2), weight=1)

def set_color(color):
    global user_colors
    user_colors[0] = color

# Attribution label
attribution_label = ttk.Label(settings_frame, text="Created by Nol Chhonleang", font=('Helvetica', 9), foreground="#cccccc")
attribution_label.pack(side=tk.BOTTOM, pady=(5, 0))

status_label = ttk.Label(settings_frame, text="Ready", font=('Helvetica', 9), foreground="#cccccc")
status_label.pack(side=tk.BOTTOM, pady=(5, 5), fill=tk.X)

def update_status(msg):
    status_label.config(text=msg)

# Controls
controls_frame = tk.Frame(settings_frame, bg="#2a2a2a")
controls_frame.pack(fill=tk.X, pady=5)
ttk.Label(controls_frame, text="Drawing", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
ttk.Button(controls_frame, text="Clear", command=clear_canvas).pack(pady=3, fill=tk.X)
ttk.Button(controls_frame, text="Undo", command=undo_last).pack(pady=3, fill=tk.X)
ttk.Button(controls_frame, text="Save", command=save_canvas).pack(pady=3, fill=tk.X)

mode_frame = tk.Frame(settings_frame, bg="#2a2a2a")
mode_frame.pack(fill=tk.X, pady=5)
ttk.Label(mode_frame, text="Modes", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
mode_button = ttk.Button(mode_frame, text="Pinch", command=toggle_mode)
mode_button.pack(pady=3, fill=tk.X)
eraser_button = ttk.Button(mode_frame, text="Eraser: OFF", command=toggle_eraser)
eraser_button.pack(pady=3, fill=tk.X)
drawing_button = ttk.Button(mode_frame, text="Draw: ON", command=toggle_drawing)
drawing_button.pack(pady=3, fill=tk.X)
move_button = ttk.Button(mode_frame, text="Move: OFF", command=toggle_move_mode)
move_button.pack(pady=3, fill=tk.X)

brush_frame = tk.Frame(settings_frame, bg="#2a2a2a")
brush_frame.pack(fill=tk.X, pady=5)
ttk.Label(brush_frame, text="Brush", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
ttk.Label(brush_frame, text="Size").pack(pady=(0, 3))
thickness_slider = ttk.Scale(brush_frame, from_=5, to=60, orient=tk.HORIZONTAL, command=lambda e: update_brush_preview())
thickness_slider.set(brush_thickness)
thickness_slider.pack(fill=tk.X, padx=5)
ttk.Label(brush_frame, text="Opacity").pack(pady=(3, 3))
opacity_slider = ttk.Scale(brush_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, command=lambda e: update_brush_preview())
opacity_slider.set(brush_opacity)
opacity_slider.pack(fill=tk.X, padx=5)

color_frame = tk.Frame(settings_frame, bg="#2a2a2a")
color_frame.pack(fill=tk.X, pady=5)
ttk.Label(color_frame, text="Colors", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
ttk.Button(color_frame, text="Pick Color", command=choose_color).pack(pady=3, fill=tk.X)
ttk.Button(color_frame, text="Reset Colors", command=reset_colors).pack(pady=3, fill=tk.X)
create_color_palette()

# --- Camera Setup ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    update_status("Cannot open camera")
    print("ERROR: Cannot open camera.")

camera_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
camera_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)

# Initialize drawing_layer
canvas.update_idletasks()
canvas_width = canvas.winfo_width()
canvas_height = canvas.winfo_height()
drawing_layer = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

update_brush_preview()

def distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def resize_and_center_frame(frame, target_w, target_h):
    fh, fw = frame.shape[:2]
    scale = min(target_w / fw, target_h / fh)
    nw = int(fw * scale)
    nh = int(fh * scale)
    resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_AREA)
    centered = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    x_off = (target_w - nw) // 2
    y_off = (target_h - nh) // 2
    centered[y_off:y_off+nh, x_off:x_off+nw] = resized
    return centered

def ensure_drawing_layer_size(w, h):
    global drawing_layer
    if drawing_layer is None:
        drawing_layer = np.zeros((h, w, 3), dtype=np.uint8)
        return
    if drawing_layer.shape[0] != h or drawing_layer.shape[1] != w:
        drawing_layer = cv2.resize(drawing_layer, (w, h), interpolation=cv2.INTER_LINEAR)

def move_drawing_layer(dx, dy):
    global drawing_layer, undo_stack
    if drawing_layer is None:
        return
    undo_stack.append(drawing_layer.copy())
    if len(undo_stack) > max_undo:
        undo_stack.pop(0)
    h, w = drawing_layer.shape[:2]
    translation_matrix = np.float32([[1, 0, dx], [0, 1, dy]])
    drawing_layer = cv2.warpAffine(drawing_layer, translation_matrix, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    update_status("Drawing moved")

def update_frame():
    global prev_points, prev_move_points, drawing_layer, brush_thickness, brush_opacity
    global canvas_width, canvas_height, last_combined, last_frame
    try:
        brush_thickness = int(thickness_slider.get())
        brush_opacity = float(opacity_slider.get())

        canvas.update_idletasks()
        new_w = canvas.winfo_width()
        new_h = canvas.winfo_height()
        if new_w != canvas_width or new_h != canvas_height:
            canvas_width, canvas_height = new_w, new_h
            ensure_drawing_layer_size(canvas_width, canvas_height)

        ret, frame = cap.read()
        if not ret:
            update_status("Camera read error")
            root.after(30, update_frame)
            return

        frame = cv2.flip(frame, 1)
        frame_for_processing = resize_and_center_frame(frame, canvas_width, canvas_height)
        last_frame = frame_for_processing.copy()

        rgb = cv2.cvtColor(frame_for_processing, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks and (is_drawing_enabled or is_move_mode):
            update_status(f"{len(results.multi_hand_landmarks)} hand(s) detected")
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                index_tip = hand_landmarks.landmark[8]
                thumb_tip = hand_landmarks.landmark[4]
                middle_tip = hand_landmarks.landmark[12]
                x = int(index_tip.x * canvas_width)
                y = int(index_tip.y * canvas_height)
                x = max(0, min(x, canvas_width-1))
                y = max(0, min(y, canvas_height-1))
                hand_id = idx

                user_color_rgb = user_colors[idx % len(user_colors)]
                user_color_bgr = tuple(reversed(user_color_rgb))

                if is_move_mode:
                    # Check for thumb-middle pinch for moving
                    is_moving = distance(thumb_tip, middle_tip) < pinch_threshold
                    if is_moving:
                        if prev_move_points.get(hand_id) is None:
                            prev_move_points[hand_id] = (x, y)
                        else:
                            x0, y0 = prev_move_points[hand_id]
                            dx = x - x0
                            dy = y - y0
                            if dx != 0 or dy != 0:
                                move_drawing_layer(dx, dy)
                            prev_move_points[hand_id] = (x, y)
                    else:
                        prev_move_points[hand_id] = None
                elif is_drawing_enabled:
                    # Drawing logic
                    if use_pinch_mode:
                        is_drawing = distance(thumb_tip, index_tip) < pinch_threshold
                    else:
                        ring_tip = hand_landmarks.landmark[16]
                        pinky_tip = hand_landmarks.landmark[20]
                        wrist = hand_landmarks.landmark[0]
                        is_drawing = (
                            distance(index_tip, wrist) > distance(middle_tip, wrist) and
                            distance(index_tip, wrist) > distance(ring_tip, wrist) and
                            distance(index_tip, wrist) > distance(pinky_tip, wrist)
                        )

                    if is_drawing:
                        if prev_points.get(hand_id) is None:
                            undo_stack.append(drawing_layer.copy())
                            if len(undo_stack) > max_undo:
                                undo_stack.pop(0)
                            prev_points[hand_id] = (x, y)
                        else:
                            x0, y0 = prev_points[hand_id]
                            overlay = drawing_layer.copy()
                            color = (0, 0, 0) if is_eraser else user_color_bgr
                            cv2.line(overlay, (x0, y0), (x, y), color, brush_thickness, lineType=cv2.LINE_AA)
                            drawing_layer = cv2.addWeighted(overlay, brush_opacity, drawing_layer, 1 - brush_opacity, 0)
                            prev_points[hand_id] = (x, y)
                    else:
                        prev_points[hand_id] = None

                mp_drawing.draw_landmarks(frame_for_processing, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            if not results.multi_hand_landmarks:
                prev_points.clear()
                prev_move_points.clear()
            update_status("No hand detected" if not results.multi_hand_landmarks else "Hands detected, drawing/move disabled")

        combined = cv2.addWeighted(frame_for_processing, 0.6, drawing_layer, 0.4, 0)
        last_combined = combined.copy()
        img_rgb = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)

        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        canvas.imgtk = imgtk

    except Exception as e:
        print("Error in update_frame:", e)
        update_status(f"Error: {e}")

    root.after(15, update_frame)

def on_close():
    try:
        cap.release()
    except Exception:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

update_frame()
root.mainloop()