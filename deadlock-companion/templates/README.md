# Template Images

This directory contains reference template images used for detecting objectives on the minimap.

## How to generate templates

1. Launch Deadlock and start a match
2. Take a high-resolution screenshot when the minimap is fully visible with objectives
3. Run the extraction tool:
   ```bash
   python tools/extract_templates.py path/to/screenshot.png
   ```
4. Click on each objective icon when prompted
5. Templates are saved here automatically

## Required templates

- `t1_camp.png` — T1 neutral camp icon (small, 1 arrow)
- `t2_camp.png` — T2 neutral camp icon (medium, 2 arrows)
- `t3_camp.png` — T3 neutral camp icon (large, 3 arrows)
- `sinner.png` — Sinner's Sacrifice icon
- `bridge_buff.png` — Bridge Buff icon
