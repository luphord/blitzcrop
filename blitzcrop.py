#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""GUI for interactive batch image cropping.
"""

__author__ = """luphord"""
__email__ = """luphord@protonmail.com"""
__version__ = """0.1.0"""


from argparse import ArgumentParser
from tkinter import Tk, Canvas
from PIL import Image, ImageTk

canvas = circle = rectangle = None
lux = luy = None
rlx = rly = None


def start_circle(event):
    global lux, luy, rlx, rly, circle, rectangle
    if circle:
        canvas.delete(circle)
    if rectangle:
        canvas.delete(rectangle)
    lux = luy = rlx = rly = None
    lux, luy = event.x, event.y


def draw_circle(event):
    global lux, luy, rlx, rly, circle, rectangle
    if circle:
        canvas.delete(circle)
    if rectangle:
        canvas.delete(rectangle)
    rlx, rly = event.x, event.y
    cx = lux + (rlx - lux) / 2
    cy = luy + (rly - luy) / 2
    r = ((cx - lux) ** 2 + (cy - luy) ** 2) ** 0.5
    circle = canvas.create_oval(
        cx - r, cy - r, cx + r, cy + r, fill=None, outline="red", width=2
    )


def draw_rectangle(event):
    global lux, luy, rlx, rly, circle, rectangle
    if rectangle:
        canvas.delete(rectangle)
    if lux and luy and rlx and rly:
        cx = lux + (rlx - lux) / 2
        cy = luy + (rly - luy) / 2
        r_squared = (cx - lux) ** 2 + (cy - luy) ** 2
        r = r_squared**0.5
        dy = event.y - cy
        dy = min(max(dy, -r), r)
        dx_squared = r_squared - dy**2
        dx_squared = max(dx_squared, 0)
        dx = dx_squared**0.5
        rectangle = canvas.create_polygon(
            lux, luy, cx + dx, cy + dy, rlx, rly, fill=None, outline="blue", width=2
        )


parser = ArgumentParser(description=__doc__)
parser.add_argument(
    "--version", help="Print version number", default=False, action="store_true"
)


def main() -> None:
    args = parser.parse_args()
    if args.version:
        print("""blitzcrop """ + __version__)
        return
    app = Tk()
    app.geometry("400x600")

    global canvas
    canvas = Canvas(app, bg="black")
    canvas.pack(anchor="nw", fill="both", expand=1)

    canvas.bind("<Button-1>", start_circle)
    canvas.bind("<B1-Motion>", draw_circle)
    canvas.bind("<Motion>", draw_rectangle)

    image = Image.open("img/test1.jpg")
    image = image.resize((400, 600), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image=image, anchor="nw")
    app.mainloop()


if __name__ == "__main__":
    main()
