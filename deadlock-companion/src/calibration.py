"""Calibration overlay — tkinter fullscreen region selector for minimap capture."""
import tkinter as tk
from typing import Optional


def select_region() -> Optional[dict]:
    """Show a fullscreen transparent overlay and let user drag a rectangle.
    Returns {"x": int, "y": int, "width": int, "height": int} or None if cancelled.
    """
    result = {"region": None}

    root = tk.Tk()
    root.title("Deadlock Companion — Select Minimap Region")
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.3)
    root.attributes("-topmost", True)
    root.configure(bg="black")

    canvas = tk.Canvas(root, cursor="crosshair", bg="black", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    start_x = 0
    start_y = 0
    rect_id = None

    canvas.create_text(
        root.winfo_screenwidth() // 2,
        50,
        text="Drag a rectangle over your minimap. Press Escape to cancel.",
        fill="white",
        font=("Arial", 24),
    )

    def on_press(event):
        nonlocal start_x, start_y, rect_id
        start_x = event.x
        start_y = event.y
        if rect_id:
            canvas.delete(rect_id)
        rect_id = canvas.create_rectangle(
            start_x, start_y, start_x, start_y,
            outline="lime", width=3,
        )

    def on_drag(event):
        nonlocal rect_id
        if rect_id:
            canvas.coords(rect_id, start_x, start_y, event.x, event.y)

    def on_release(event):
        x1 = min(start_x, event.x)
        y1 = min(start_y, event.y)
        x2 = max(start_x, event.x)
        y2 = max(start_y, event.y)
        width = x2 - x1
        height = y2 - y1
        if width > 10 and height > 10:
            result["region"] = {
                "x": x1,
                "y": y1,
                "width": width,
                "height": height,
            }
        root.destroy()

    def on_escape(event):
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", on_escape)

    root.mainloop()
    return result["region"]
