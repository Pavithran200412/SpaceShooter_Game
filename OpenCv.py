import cv2
import numpy as np
import tkinter as tk
from tkinter import simpledialog, messagebox

# --- Global Variables ---
angle_x, angle_y = 0, 0
zoom_factor = 1.0
shift_x, shift_y = 0, 0
drawing = False
last_mouse_x, last_mouse_y = 0, 0
shape = "cube"
current_shape = None

# --- 3D Projection ---
def project(points):
    projected_points = []
    for p in points:
        x, y, z = p
        x = x * zoom_factor + shift_x
        y = y * zoom_factor + shift_y
        z = z * zoom_factor
        f = 500 / (500 + z)
        px = int(300 + x * f)
        py = int(300 - y * f)
        projected_points.append((px, py))
    return projected_points

# --- Drawing the 3D shape ---
def draw(img, points):
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    # Connect all points (front & back)
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            cv2.line(img, points[i], points[j], (255, 255, 255), 2)

# --- Rotation ---
def rotate(points, ax, ay):
    ax = np.radians(ax)
    ay = np.radians(ay)
    rx = np.array([
        [1, 0, 0],
        [0, np.cos(ax), -np.sin(ax)],
        [0, np.sin(ax), np.cos(ax)]
    ])
    ry = np.array([
        [np.cos(ay), 0, np.sin(ay)],
        [0, 1, 0],
        [-np.sin(ay), 0, np.cos(ay)]
    ])
    rotated = np.dot(points, rx)
    rotated = np.dot(rotated, ry)
    return rotated

# --- Reset View ---
def reset_view():
    global angle_x, angle_y, zoom_factor, shift_x, shift_y
    angle_x, angle_y = 0, 0
    zoom_factor = 1.0
    shift_x, shift_y = 0, 0

# --- Mouse Events ---
def mouse_callback(event, x, y, flags, param):
    global angle_x, angle_y, last_mouse_x, last_mouse_y, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        last_mouse_x, last_mouse_y = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            angle_y += (x - last_mouse_x) * 0.5
            angle_x += (y - last_mouse_y) * 0.5
            last_mouse_x, last_mouse_y = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

# --- Main 3D Shape Viewer ---
def shape_viewer():
    global current_shape
    cv2.namedWindow("3D Shape Viewer")
    cv2.setMouseCallback("3D Shape Viewer", mouse_callback)

    while True:
        img = np.zeros((600, 600, 3), dtype=np.uint8)

        rotated_shape = rotate(current_shape, angle_x, angle_y)
        projected = project(rotated_shape)
        draw(img, projected)

        cv2.putText(img, "Drag Mouse: Rotate | Arrows: Move | +/- Zoom | r: Reset | Esc: Exit",
                    (10, 590), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        cv2.imshow("3D Shape Viewer", img)

        key = cv2.waitKey(10) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('r'):
            reset_view()
        elif key == ord('+') or key == ord('='):
            zoom_in()
        elif key == ord('-') or key == ord('_'):
            zoom_out()
        elif key == 81:  # Left
            move_left()
        elif key == 82:  # Up
            move_up()
        elif key == 83:  # Right
            move_right()
        elif key == 84:  # Down
            move_down()

    cv2.destroyAllWindows()

# --- Zoom Functions ---
def zoom_in():
    global zoom_factor
    zoom_factor *= 1.1

def zoom_out():
    global zoom_factor
    zoom_factor /= 1.1

# --- Move Functions ---
def move_left():
    global shift_x
    shift_x -= 10

def move_right():
    global shift_x
    shift_x += 10

def move_up():
    global shift_y
    shift_y -= 10

def move_down():
    global shift_y
    shift_y += 10

# --- Create Shapes ---
def create_shape():
    global current_shape
    shape_type = simpledialog.askstring("Input", "Enter shape (cube/cuboid/pyramid/cylinder/sphere):")
    if not shape_type:
        return

    if shape_type.lower() == "cube":
        l = float(simpledialog.askstring("Input", "Enter cube side length (e.g., 3):"))
        w, h, d = l, l, l
        current_shape = np.float32([
            [-w, -h, -d], [ w, -h, -d], [ w,  h, -d], [-w,  h, -d],
            [-w, -h,  d], [ w, -h,  d], [ w,  h,  d], [-w,  h,  d]
        ])

    elif shape_type.lower() == "cuboid":
        w = float(simpledialog.askstring("Input", "Enter cuboid width (X length):"))
        h = float(simpledialog.askstring("Input", "Enter cuboid height (Y length):"))
        d = float(simpledialog.askstring("Input", "Enter cuboid depth (Z length):"))
        current_shape = np.float32([
            [-w, -h, -d], [ w, -h, -d], [ w,  h, -d], [-w,  h, -d],
            [-w, -h,  d], [ w, -h,  d], [ w,  h,  d], [-w,  h,  d]
        ])

    elif shape_type.lower() == "pyramid":
        base_size = float(simpledialog.askstring("Input", "Enter pyramid base size (side length):"))
        height = float(simpledialog.askstring("Input", "Enter pyramid height:"))
        current_shape = np.float32([
            [-base_size, -base_size, 0], [ base_size, -base_size, 0], 
            [ base_size,  base_size, 0], [-base_size,  base_size, 0], 
            [0, 0, height]
        ])

    elif shape_type.lower() == "cylinder":
        radius = float(simpledialog.askstring("Input", "Enter cylinder radius:"))
        height = float(simpledialog.askstring("Input", "Enter cylinder height:"))
        theta = np.linspace(0, 2*np.pi, 30)
        circle = np.array([[radius * np.cos(t), radius * np.sin(t), 0] for t in theta])
        top_circle = circle + [0, 0, height]
        current_shape = np.vstack([circle, top_circle])

    elif shape_type.lower() == "sphere":
        radius = float(simpledialog.askstring("Input", "Enter sphere radius:"))
        phi = np.linspace(0, np.pi, 15)
        theta = np.linspace(0, 2*np.pi, 30)
        points = [
            [radius * np.sin(p) * np.cos(t), radius * np.sin(p) * np.sin(t), radius * np.cos(p)]
            for p in phi for t in theta
        ]
        current_shape = np.array(points)

    else:
        messagebox.showerror("Error", "Invalid shape type entered!")
        return

    reset_view()
    shape_viewer()

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("3D Shape Creator GUI")

tk.Label(root, text="3D Shape Creator", font=("Arial", 20)).pack(pady=10)

btn_create = tk.Button(root, text="Create Shape", command=create_shape, width=30)
btn_create.pack(pady=5)

btn_zoom_in = tk.Button(root, text="Zoom In", command=zoom_in, width=30)
btn_zoom_in.pack(pady=5)

btn_zoom_out = tk.Button(root, text="Zoom Out", command=zoom_out, width=30)
btn_zoom_out.pack(pady=5)

btn_reset = tk.Button(root, text="Reset View", command=reset_view, width=30)
btn_reset.pack(pady=5)

btn_exit = tk.Button(root, text="Exit", command=root.destroy, width=30)
btn_exit.pack(pady=5)

root.mainloop()
