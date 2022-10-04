#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""GUI for interactive batch image cropping.
"""

__author__ = """luphord"""
__email__ = """luphord@protonmail.com"""
__version__ = """0.1.0"""


from argparse import ArgumentParser
from math import atan, sin, cos, degrees, pi, copysign
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


def rescaled_image_size(canvas_width, canvas_height, image_width, image_height):
    """Compute image size to embed into canvas."""
    ar = image_width / image_height
    if ar >= canvas_width / canvas_height:
        # image is wider than window => cut away height
        iw, ih = canvas_width, canvas_width / ar
    else:
        # image is narrower than window => cut away width
        iw, ih = canvas_height * ar, canvas_height
    return int(iw), int(ih)


def rotation_angle(upper_left_x, upper_left_y, upper_right_x, upper_right_y):
    """Compute rotation angle by upper left and right points of selected rectangle.
    This is the angle *by which the selection is rotated*. To correct for it, you
    have to rotate the image *minus* this angle."""
    dx = upper_right_x - upper_left_x
    dy = upper_right_y - upper_left_y
    # minus for correcting that y increases downwards
    return -(atan(dy / dx) if dx != 0 else copysign(0.5 * pi, dy))


def containing_rectangle(x1, y1, x2, y2, x3, y3, x4, y4):
    """Compute smallest rectangle containing the given shape (rotated rectangle)."""
    xs = [x1, x2, x3, x4]
    ys = [y1, y2, y3, y4]
    return min(xs), min(ys), max(xs), max(ys)


def containing_rectangle_offsets(
    upper_left_x, upper_left_y, upper_right_x, upper_right_y, lower_left_y
):
    """Compute offset between selected rectangle and containing rectangle."""
    d_upper_y = upper_right_y - upper_left_y
    d_lower_y = upper_left_y - lower_left_y
    alpha = rotation_angle(upper_left_x, upper_left_y, upper_right_x, upper_right_y)
    return (d_lower_y * sin(alpha), d_upper_y * cos(alpha))


def canvas_coordinates_to_image(
    x, y, canvas_width, canvas_height, image_width, image_height
):
    """Transform canvas coordinates to image coordinates."""
    iw, ih = rescaled_image_size(canvas_width, canvas_height, image_width, image_height)
    ix, iy = (canvas_width - iw) // 2, (canvas_height - ih) // 2
    return (x - ix) / iw * image_width, (y - iy) / ih * image_height


def canvas_rectangle_to_image(
    x1, y1, x2, y2, canvas_width, canvas_height, image_width, image_height
):
    """Transform rectangle in canvas coordinates to rectangle in image coordinates."""
    xi1, yi1 = canvas_coordinates_to_image(
        x1, y1, canvas_width, canvas_height, image_width, image_height
    )
    xi2, yi2 = canvas_coordinates_to_image(
        x2, y2, canvas_width, canvas_height, image_width, image_height
    )
    return xi1, yi1, xi2, yi2


class CropCanvas(Canvas):
    """Canvas supporting image crop by mouse drag + click."""

    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = image
        self.circle = None
        self.rectangle = None
        self.projected = None
        self.lux = None
        self.luy = None
        self.rlx = None
        self.rly = None
        self.selected_rectangle = None
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<Motion>", self.on_mousemove)
        self.bind("<Configure>", self.on_resize)

    def redraw_image(self):
        self.winfo_toplevel().update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        iw, ih = rescaled_image_size(w, h, self.image.width, self.image.height)
        image_resized = self.image.resize((iw, ih), Image.NEAREST)
        # member variable is required for photo image to prevent garbage collection
        self._photo_image = ImageTk.PhotoImage(image_resized)
        self.create_image(
            (w - iw) // 2, (h - ih) // 2, image=self._photo_image, anchor="nw"
        )

    def on_resize(self, event):
        self.config(width=event.width, height=event.height)
        self.redraw_image()

    def _delete_circle_and_rectangle(self):
        if self.circle:
            self.delete(self.circle)
        if self.rectangle:
            self.delete(self.rectangle)
        if self.projected:
            self.delete(self.projected)
        self.selected_rectangle = None

    def on_click(self, event):
        if self.selected_rectangle:
            r = self.selected_rectangle
            canvas_width, canvas_height = self.winfo_width(), self.winfo_height()
            x1, y1, x2, y2 = canvas_rectangle_to_image(
                *containing_rectangle(*self.selected_rectangle),
                canvas_width,
                canvas_height,
                self.image.width,
                self.image.height,
            )
            self.image.crop((x1, y1, x2, y2)).rotate(
                -degrees(rotation_angle(r[0], r[1], r[2], r[3])), expand=True
            ).show()
            print(containing_rectangle_offsets(r[0], r[1], r[2], r[3], r[7]))
        self._delete_circle_and_rectangle()
        self.rlx = self.rly = None
        self.lux, self.luy = event.x, event.y

    def on_drag(self, event):
        self._delete_circle_and_rectangle()
        self.rlx, self.rly = event.x, event.y
        bbox = circle_bounding_box_from_diameter(self.lux, self.luy, self.rlx, self.rly)
        self.circle = self.create_oval(*bbox, fill="", outline="red", width=2)

    def on_mousemove(self, event):
        if self.rectangle:
            self.delete(self.rectangle)
        if self.projected:
            self.delete(self.projected)
        if self.lux and self.luy and self.rlx and self.rly:
            cx = self.lux + (self.rlx - self.lux) / 2
            cy = self.luy + (self.rly - self.luy) / 2
            r = ((cx - self.lux) ** 2 + (cy - self.luy) ** 2) ** 0.5
            x1, y1 = project_to_circle(event.x, event.y, cx, cy, r)
            self.projected = self.create_oval(
                x1 - 5, y1 - 5, x1 + 5, y1 + 5, fill="yellow"
            )
            x2, y2 = central_inversion(x1, y1, cx, cy)
            self.selected_rectangle = (
                self.lux,
                self.luy,
                x1,
                y1,
                self.rlx,
                self.rly,
                x2,
                y2,
            )
            self.rectangle = self.create_polygon(
                *self.selected_rectangle,
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
