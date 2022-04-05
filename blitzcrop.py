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


def central_inversion(x, y, cx, cy):
    """Inversion of point (x, y) through (cx, cy), a.k.a point reflection."""
    return 2 * cx - x, 2 * cy - y


class CropCanvas(Canvas):
    """Canvas supporting image crop by mouse drag + click."""

    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = image
        self.circle = None
        self.rectangle = None
        self.lux = None
        self.luy = None
        self.rlx = None
        self.rly = None
        self.bind("<Button-1>", self.start_circle)
        self.bind("<B1-Motion>", self.draw_circle)
        self.bind("<Motion>", self.draw_rectangle)
        self.bind("<Configure>", self.on_resize)

    def redraw_image(self):
        self.winfo_toplevel().update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        ar = self.image.width / self.image.height
        if ar >= w / h:
            # image is wider than window => cut away height
            iw, ih = w, w / ar
        else:
            # image is narrower than window => cut away width
            iw, ih = h * ar, h
        iw, ih = int(iw), int(ih)
        image_resized = self.image.resize((iw, ih), Image.NEAREST)
        # member variable is required for photo image to prevent garbage collection
        self._photo_image = ImageTk.PhotoImage(image_resized)
        self.create_image(
            (w - iw) // 2, (h - ih) // 2, image=self._photo_image, anchor="nw"
        )

    def on_resize(self, event):
        self.config(width=event.width, height=event.height)
        self.redraw_image()

    def delete_circle_and_rectangle(self):
        if self.circle:
            self.delete(self.circle)
        if self.rectangle:
            self.delete(self.rectangle)

    def start_circle(self, event):
        self.delete_circle_and_rectangle()
        self.rlx = self.rly = None
        self.lux, self.luy = event.x, event.y

    def draw_circle(self, event):
        self.delete_circle_and_rectangle()
        self.rlx, self.rly = event.x, event.y
        bbox = circle_bounding_box_from_diameter(self.lux, self.luy, self.rlx, self.rly)
        self.circle = self.create_oval(*bbox, fill="", outline="red", width=2)

    def draw_rectangle(self, event):
        if self.rectangle:
            self.delete(self.rectangle)
        if self.lux and self.luy and self.rlx and self.rly:
            cx = self.lux + (self.rlx - self.lux) / 2
            cy = self.luy + (self.rly - self.luy) / 2
            r = ((cx - self.lux) ** 2 + (cy - self.luy) ** 2) ** 0.5
            x1, y1 = project_to_circle(event.x, event.y, cx, cy, r)
            x2, y2 = central_inversion(x1, y1, cx, cy)
            self.rectangle = self.create_polygon(
                self.lux,
                self.luy,
                x1,
                y1,
                self.rlx,
                self.rly,
                x2,
                y2,
                fill="",
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

    image = Image.open("img/test1.jpg")
    canvas = CropCanvas(image, app, bg="black")
    canvas.pack(anchor="nw", fill="both", expand=1)
    canvas.redraw_image()
    app.mainloop()


if __name__ == "__main__":
    main()
