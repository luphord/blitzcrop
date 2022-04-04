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


def circle_bounding_box_from_diameter(x1, y1, x2, y2):
    """Compute bounding box for a circle from two arbitrary diametric points."""
    cx = x1 + (x2 - x1) / 2
    cy = y1 + (y2 - y1) / 2
    r = ((cx - x1) ** 2 + (cy - y1) ** 2) ** 0.5
    return cx - r, cy - r, cx + r, cy + r


def project_to_circle(x, y, cx, cy, r):
    """Project point (x, y) onto circle of radius r around (cx, cy)."""
    alpha = r / ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
    return cx + alpha * (x - cx), cy + alpha * (y - cy)


class CropCanvas(Canvas):
    """Canvas supporting image crop by mouse drag + click."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.circle = None
        self.rectangle = None
        self.lux = None
        self.luy = None
        self.rlx = None
        self.rly = None
        self.bind("<Button-1>", self.start_circle)
        self.bind("<B1-Motion>", self.draw_circle)
        self.bind("<Motion>", self.draw_rectangle)

    def start_circle(self, event):
        if self.circle:
            self.delete(self.circle)
        if self.rectangle:
            self.delete(self.rectangle)
        self.rlx = self.rly = None
        self.lux, self.luy = event.x, event.y

    def draw_circle(self, event):
        if self.circle:
            self.delete(self.circle)
        if self.rectangle:
            self.delete(self.rectangle)
        self.rlx, self.rly = event.x, event.y
        bbox = circle_bounding_box_from_diameter(self.lux, self.luy, self.rlx, self.rly)
        self.circle = self.create_oval(*bbox, fill=None, outline="red", width=2)

    def draw_rectangle(self, event):
        if self.rectangle:
            self.delete(self.rectangle)
        if self.lux and self.luy and self.rlx and self.rly:
            cx = self.lux + (self.rlx - self.lux) / 2
            cy = self.luy + (self.rly - self.luy) / 2
            r = ((cx - self.lux) ** 2 + (cy - self.luy) ** 2) ** 0.5
            x, y = project_to_circle(event.x, event.y, cx, cy, r)
            self.rectangle = self.create_polygon(
                self.lux,
                self.luy,
                x,
                y,
                self.rlx,
                self.rly,
                fill=None,
                outline="blue",
                width=2,
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

    canvas = CropCanvas(app, bg="black")
    canvas.pack(anchor="nw", fill="both", expand=1)

    image = Image.open("img/test1.jpg")
    image = image.resize((400, 600), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image=image, anchor="nw")
    app.mainloop()


if __name__ == "__main__":
    main()
