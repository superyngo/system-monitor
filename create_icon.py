#!/usr/bin/env python
"""
Generate a simple icon for the system monitor application
"""

from PIL import Image, ImageDraw
import os


def create_icon():
    """Create a simple system monitor icon"""

    # Create a 256x256 image with transparent background
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a computer monitor shape
    monitor_color = (64, 128, 255, 255)  # Blue
    screen_color = (32, 32, 32, 255)  # Dark gray

    # Monitor outline
    margin = 20
    monitor_rect = [margin, margin, size - margin, size - margin - 40]
    draw.rectangle(monitor_rect, fill=monitor_color, outline=(0, 0, 0, 255), width=4)

    # Screen
    screen_margin = 15
    screen_rect = [
        monitor_rect[0] + screen_margin,
        monitor_rect[1] + screen_margin,
        monitor_rect[2] - screen_margin,
        monitor_rect[3] - screen_margin,
    ]
    draw.rectangle(screen_rect, fill=screen_color)

    # Monitor stand
    stand_width = 60
    stand_height = 30
    stand_x = size // 2 - stand_width // 2
    stand_y = monitor_rect[3]
    draw.rectangle(
        [stand_x, stand_y, stand_x + stand_width, stand_y + stand_height],
        fill=monitor_color,
    )

    # Base
    base_width = 100
    base_height = 10
    base_x = size // 2 - base_width // 2
    base_y = stand_y + stand_height
    draw.rectangle(
        [base_x, base_y, base_x + base_width, base_y + base_height], fill=monitor_color
    )

    # System info display (simplified chart bars)
    chart_color = (0, 255, 0, 255)  # Green
    bar_width = 8
    bar_spacing = 12
    chart_x = screen_rect[0] + 20
    chart_y = screen_rect[1] + 20
    # Draw some bars representing system metrics
    for i in range(6):
        bar_height = 20 + (i * 8) % 60
        x = chart_x + i * bar_spacing
        bar_y = chart_y + 80 - bar_height
        draw.rectangle([x, bar_y, x + bar_width, chart_y + 80], fill=chart_color)

    # Save as ICO file with multiple sizes
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []

    for ico_size in sizes:
        resized = img.resize((ico_size, ico_size), Image.Resampling.LANCZOS)
        images.append(resized)

    # Save ICO file
    os.makedirs("assets", exist_ok=True)
    img.save("assets/icon.ico", format="ICO", sizes=[(s, s) for s in sizes])
    print("Icon created: assets/icon.ico")


if __name__ == "__main__":
    create_icon()
