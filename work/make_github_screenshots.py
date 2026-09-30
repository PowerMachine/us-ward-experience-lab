"""Capture the official GitHub screenshots from the real Tk application.

Run this on Windows from any working directory. The capture is deliberately the
minimum supported app size so layout regressions in the sidebar and top bar are
visible in the repository screenshots.
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

from PIL import ImageGrab


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
SCREENSHOTS = ROOT / "screenshots"
CAPTURE_WIDTH = 1180
CAPTURE_HEIGHT = 700
WINDOW_X = 40
WINDOW_Y = 40

if str(WORK) not in sys.path:
    sys.path.insert(0, str(WORK))

from us_ward_simulator import WardSimulatorApp, enable_windows_dpi_awareness  # noqa: E402


def settle(app: WardSimulatorApp) -> None:
    """Let Tk finish layout, redraws, and local image composition."""
    app.update_idletasks()
    app.update()
    time.sleep(0.25)
    app.update_idletasks()
    app.update()


def capture_page(app: WardSimulatorApp, page_key: str, filename: str) -> None:
    app.show_page(page_key)
    app.page.canvas.yview_moveto(0.0)
    settle(app)

    x = app.winfo_rootx()
    y = app.winfo_rooty()
    width = app.winfo_width()
    height = app.winfo_height()
    if (width, height) != (CAPTURE_WIDTH, CAPTURE_HEIGHT):
        raise RuntimeError(
            f"Unexpected Tk client size for {page_key}: {width}x{height}; "
            f"expected {CAPTURE_WIDTH}x{CAPTURE_HEIGHT}."
        )

    screenshot = ImageGrab.grab(
        bbox=(x, y, x + width, y + height),
        include_layered_windows=True,
    ).convert("RGB")
    if screenshot.size != (CAPTURE_WIDTH, CAPTURE_HEIGHT):
        raise RuntimeError(
            f"Unexpected bitmap size for {page_key}: {screenshot.size}; "
            f"expected {(CAPTURE_WIDTH, CAPTURE_HEIGHT)}."
        )
    screenshot.save(SCREENSHOTS / filename, format="PNG", optimize=True)


def main() -> None:
    if sys.platform != "win32":
        raise RuntimeError("Official UI screenshots must be captured on Windows.")

    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    random.seed(7)
    enable_windows_dpi_awareness()
    app = WardSimulatorApp()
    try:
        app.geometry(
            f"{CAPTURE_WIDTH}x{CAPTURE_HEIGHT}+{WINDOW_X}+{WINDOW_Y}"
        )
        try:
            app.attributes("-topmost", True)
        except Exception:
            pass
        app.lift()
        app.focus_force()
        settle(app)

        for page_key, filename in (
            ("dashboard", "main.png"),
            ("first7", "first_7_days.png"),
            ("tour", "ward_tour.png"),
        ):
            capture_page(app, page_key, filename)
    finally:
        app.destroy()

    print("GITHUB_SCREENSHOTS_OK 1180x700")


if __name__ == "__main__":
    main()
