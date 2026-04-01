"""Interactive tool to extract objective icon templates from a minimap screenshot.

Usage:
    python tools/extract_templates.py path/to/screenshot.png

Click on each objective icon center when prompted. Press 'q' to skip.
Extracted templates are saved to the templates/ directory.
"""

import sys
from pathlib import Path
import cv2
import numpy as np


TEMPLATE_SIZE = 40  # Size of the crop around each icon (pixels)

OBJECTIVES_TO_EXTRACT = [
    ("t1_camp.png", "Click on a T1 camp icon (small, 1 arrow)"),
    ("t2_camp.png", "Click on a T2 camp icon (medium, 2 arrows)"),
    ("t3_camp.png", "Click on a T3 camp icon (large, 3 arrows)"),
    ("sinner.png", "Click on a Sinner's Sacrifice icon"),
    ("bridge_buff.png", "Click on a Bridge Buff icon"),
]


def extract_template(image: np.ndarray, center_x: int, center_y: int, size: int) -> np.ndarray:
    half = size // 2
    h, w = image.shape[:2]
    x1 = max(0, center_x - half)
    y1 = max(0, center_y - half)
    x2 = min(w, center_x + half)
    y2 = min(h, center_y + half)
    return image[y1:y2, x1:x2].copy()


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/extract_templates.py path/to/screenshot.png")
        sys.exit(1)

    image_path = sys.argv[1]
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image: {image_path}")
        sys.exit(1)

    templates_dir = Path(__file__).parent.parent / "templates"
    templates_dir.mkdir(exist_ok=True)

    click_pos = {"x": -1, "y": -1}

    def on_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            click_pos["x"] = x
            click_pos["y"] = y

    window_name = "Template Extractor"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, on_click)

    for filename, prompt in OBJECTIVES_TO_EXTRACT:
        print(f"\n{prompt}")
        print("Left-click on the icon center. Press 'q' to skip, wait for save.")

        display = image.copy()
        cv2.putText(display, prompt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow(window_name, display)

        click_pos["x"] = -1
        click_pos["y"] = -1

        while True:
            key = cv2.waitKey(50) & 0xFF
            if key == ord("q"):
                print(f"  Skipped {filename}")
                break
            if click_pos["x"] >= 0:
                template = extract_template(image, click_pos["x"], click_pos["y"], TEMPLATE_SIZE)
                out_path = templates_dir / filename
                cv2.imwrite(str(out_path), template)
                print(f"  Saved {filename} ({template.shape[1]}x{template.shape[0]})")

                preview = image.copy()
                half = TEMPLATE_SIZE // 2
                cv2.rectangle(
                    preview,
                    (click_pos["x"] - half, click_pos["y"] - half),
                    (click_pos["x"] + half, click_pos["y"] + half),
                    (0, 255, 0), 2,
                )
                cv2.imshow(window_name, preview)
                cv2.waitKey(1000)
                break

    cv2.destroyAllWindows()
    print("\nDone! Check templates/ directory.")


if __name__ == "__main__":
    main()
