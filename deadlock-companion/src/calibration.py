"""Calibration overlay — tkinter fullscreen region selector and position calibrator."""
import tkinter as tk
from typing import Optional

import numpy as np

try:
    from PIL import Image, ImageTk
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False


# Objective types to calibrate, in order: (type_key, display_name, dot_color)
OBJECTIVE_TYPES_TO_CALIBRATE = [
    ("t1_camp",    "T1 Neutral Camp (small, 1 arrow)", "lime"),
    ("t2_camp",    "T2 Neutral Camp (medium, 2 arrows)", "cyan"),
    ("t3_camp",    "T3 Neutral Camp (large, 3 arrows)", "yellow"),
    ("sinner",     "Sinner's Sacrifice", "orange"),
    ("bridge_buff", "Bridge Buff", "magenta"),
]


def calibrate_positions(frame: np.ndarray) -> Optional[dict]:
    """Show a click-to-calibrate window for each objective type on the minimap.

    The user clicks on each instance of the current objective type shown on the
    frame (a BGR numpy array).  Right-click removes the last placed dot.  Press
    Enter or click "Done" to advance to the next type; press S or click "Skip"
    to skip the current type; press Escape to cancel the whole calibration.

    Args:
        frame: A BGR numpy array — the minimap screenshot to calibrate on.

    Returns:
        A dict mapping type keys to lists of (x_pct, y_pct) tuples, where each
        percentage is relative to the displayed image dimensions (0.0–1.0).
        Only types with at least one click are included.
        Returns None if the user presses Escape to cancel.
    """
    # ---- Scale frame up so the longer side is at least 500 px --------
    src_h, src_w = frame.shape[:2]
    min_size = 500
    scale = max(1.0, min_size / max(src_w, src_h))
    disp_w = int(src_w * scale)
    disp_h = int(src_h * scale)

    # Convert BGR → RGB PIL image at display size
    if _PIL_AVAILABLE:
        import cv2
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb).resize((disp_w, disp_h), Image.NEAREST)
    else:
        raise RuntimeError("Pillow (PIL) is required for calibrate_positions().")

    # ---- Shared mutable state -----------------------------------------
    state = {
        "cancelled": False,
        "type_index": 0,
        "clicks": [],          # list of (x_pct, y_pct) for current type
        "all_clicks": {},      # type_key -> [(x_pct, y_pct), ...]
        "advance": False,
        "skip": False,
    }

    DOT_RADIUS = 6

    root = tk.Tk()
    root.title("Deadlock Companion — Calibrate Objective Positions")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    # ---- Layout ----------------------------------------------------------
    # Header label
    header_var = tk.StringVar()
    header_lbl = tk.Label(
        root, textvariable=header_var,
        font=("Arial", 16, "bold"), pady=6,
    )
    header_lbl.pack(fill=tk.X)

    # Sub-label with instructions
    instr_lbl = tk.Label(
        root,
        text="Left-click to place a dot. Right-click to remove the last dot.",
        font=("Arial", 10),
    )
    instr_lbl.pack()

    # Canvas for the minimap image
    canvas = tk.Canvas(root, width=disp_w, height=disp_h, cursor="crosshair")
    canvas.pack()

    # Footer bar
    footer = tk.Frame(root)
    footer.pack(fill=tk.X, pady=4)

    count_var = tk.StringVar(value="Clicks: 0")
    count_lbl = tk.Label(footer, textvariable=count_var, font=("Arial", 11))
    count_lbl.pack(side=tk.LEFT, padx=10)

    done_btn = tk.Button(footer, text="Done (Enter)", font=("Arial", 11), width=12)
    done_btn.pack(side=tk.RIGHT, padx=6)

    skip_btn = tk.Button(footer, text="Skip (S)", font=("Arial", 11), width=10)
    skip_btn.pack(side=tk.RIGHT, padx=4)

    # Embed PIL image in canvas
    tk_img = ImageTk.PhotoImage(pil_img)
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

    # ---- Helpers ---------------------------------------------------------
    def _redraw_dots(dot_color: str):
        """Clear existing dot items and redraw all dots for the current type."""
        canvas.delete("dot")
        for xp, yp in state["clicks"]:
            cx = int(xp * disp_w)
            cy = int(yp * disp_h)
            canvas.create_oval(
                cx - DOT_RADIUS, cy - DOT_RADIUS,
                cx + DOT_RADIUS, cy + DOT_RADIUS,
                fill=dot_color, outline="white", width=2, tags="dot",
            )

    def _update_header():
        idx = state["type_index"]
        type_key, display_name, dot_color = OBJECTIVE_TYPES_TO_CALIBRATE[idx]
        header_var.set(
            f"Step {idx + 1}/{len(OBJECTIVE_TYPES_TO_CALIBRATE)}: "
            f"Click all  {display_name}  icons"
        )
        header_lbl.config(fg=dot_color)
        count_var.set(f"Clicks: {len(state['clicks'])}")
        _redraw_dots(dot_color)

    def _advance_to_next():
        """Save current type's clicks and move to the next type (or finish)."""
        idx = state["type_index"]
        type_key, _, _ = OBJECTIVE_TYPES_TO_CALIBRATE[idx]
        if state["clicks"]:
            state["all_clicks"][type_key] = list(state["clicks"])
        state["clicks"] = []
        state["type_index"] += 1
        if state["type_index"] >= len(OBJECTIVE_TYPES_TO_CALIBRATE):
            root.destroy()
        else:
            _update_header()

    def _skip_current():
        """Skip the current type without saving any clicks."""
        state["clicks"] = []
        state["type_index"] += 1
        if state["type_index"] >= len(OBJECTIVE_TYPES_TO_CALIBRATE):
            root.destroy()
        else:
            _update_header()

    # ---- Event bindings --------------------------------------------------
    def on_left_click(event):
        xp = event.x / disp_w
        yp = event.y / disp_h
        state["clicks"].append((xp, yp))
        _, _, dot_color = OBJECTIVE_TYPES_TO_CALIBRATE[state["type_index"]]
        count_var.set(f"Clicks: {len(state['clicks'])}")
        _redraw_dots(dot_color)

    def on_right_click(event):
        if state["clicks"]:
            state["clicks"].pop()
            _, _, dot_color = OBJECTIVE_TYPES_TO_CALIBRATE[state["type_index"]]
            count_var.set(f"Clicks: {len(state['clicks'])}")
            _redraw_dots(dot_color)

    def on_escape(event):
        state["cancelled"] = True
        root.destroy()

    def on_key(event):
        if event.keysym in ("Return", "KP_Enter"):
            _advance_to_next()
        elif event.keysym.lower() == "s":
            _skip_current()
        elif event.keysym == "Escape":
            on_escape(event)

    canvas.bind("<Button-1>", on_left_click)
    canvas.bind("<Button-3>", on_right_click)
    root.bind("<Key>", on_key)
    done_btn.config(command=_advance_to_next)
    skip_btn.config(command=_skip_current)

    # ---- Init first type and run ----------------------------------------
    _update_header()
    root.mainloop()

    if state["cancelled"]:
        return None
    return state["all_clicks"] if state["all_clicks"] else {}


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
