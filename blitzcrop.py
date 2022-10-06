#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""GUI for interactive batch image cropping.
"""

__author__ = """luphord"""
__email__ = """luphord@protonmail.com"""
__version__ = """0.1.0"""


from argparse import ArgumentParser
from math import atan, sin, cos, degrees, pi, copysign
from abc import ABC, abstractmethod
from tkinter import Tk, Canvas
from PIL import Image, ImageTk


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


class Point(ABC):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"{type(self).__name__}({self.x}, {self.y})"

    def __iter__(self):
        """Implements iteration to support destructuring assignments for Points."""
        yield self.x
        yield self.y

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError(f"Points can only be indexed by 0 or 1, got {index}")

    def assert_same_type(self, other):
        assert type(self) == type(other), (
            f"Cannot perform operation as self is of type "
            f"{type(self).__name__} while other is of type {type(other).__name__}"
        )

    def __eq__(self, other):
        return type(self) == type(other) and self.x == other.x and self.y == other.y

    def __add__(self, other):
        self.assert_same_type(other)
        return type(self)(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        self.assert_same_type(other)
        return type(self)(self.x - other.x, self.y - other.y)

    def __mul__(self, factor):
        return type(self)(self.x * factor, self.y * factor)

    def __rmul__(self, factor):
        return self * factor

    def __neg__(self):
        return -1 * self

    def __abs__(self):
        return (self.x**2 + self.y**2) ** 0.5

    def middle_between(self, other):
        """Middle point between self and other."""
        return self + 0.5 * (other - self)

    def central_inversion_through(self, center):
        """Inversion of self through center, a.k.a point reflection."""
        return 2 * center - self

    def project_to_circle_around(self, center, radius):
        """Project self onto circle of given radius around center."""
        alpha = radius / abs(self - center)
        return center + alpha * (self - center)

    def rotation_angle(self, other):
        """Compute rotation angle of difference vector around self w.r.t. horizontal line.
        This is the angle *by which the vector is rotated*. To correct for it, you
        have to rotate *minus* this angle."""
        dx, dy = other - self
        # minus for correcting that y increases downwards
        return -(atan(dy / dx) if dx != 0 else copysign(0.5 * pi, dy))

    def circle_bounding_box_from_diameter(self, other):
        """Compute bounding box for a circle from diametric points self and other."""
        center = self.middle_between(other)
        radius = abs(center - self)
        return center - type(self)(radius, radius), center + type(self)(radius, radius)

    @abstractmethod
    def to_image_coordinates(
        self, canvas_width, canvas_height, image_width, image_height
    ):
        pass


class ImagePoint(Point):
    def to_image_coordinates(
        self, canvas_width, canvas_height, image_width, image_height
    ):
        return self


class CanvasPoint(Point):
    def to_image_coordinates(
        self, canvas_width, canvas_height, image_width, image_height
    ):
        iw, ih = rescaled_image_size(
            canvas_width, canvas_height, image_width, image_height
        )
        ix, iy = (canvas_width - iw) // 2, (canvas_height - ih) // 2
        return ImagePoint(
            (self.x - ix) / iw * image_width, (self.y - iy) / ih * image_height
        )


class Rectangle:
    def __init__(self, left_upper, right_upper, right_lower, left_lower):
        left_upper.assert_same_type(right_upper)
        left_upper.assert_same_type(right_lower)
        left_upper.assert_same_type(left_lower)
        self.left_upper = left_upper
        self.right_upper = right_upper
        self.right_lower = right_lower
        self.left_lower = left_lower

    def __repr__(self):
        return (
            f"{type(self).__name__}({self.left_upper}, {self.right_upper}, "
            f"{self.right_lower}, {self.left_lower})"
        )

    def __iter__(self):
        """Implements iteration to support destructuring assignments for Points."""
        yield self.left_upper
        yield self.right_upper
        yield self.right_lower
        yield self.left_lower

    def flatten(self):
        for point in self:
            for coordinate in point:
                yield coordinate

    def containing_rectangle(self):
        """Compute smallest rectangle (with sides parallel to the axes)
        containing self (a possibly rotated rectangle)."""
        xs = [point.x for point in self]
        ys = [point.y for point in self]
        PointType = type(self.left_upper)
        return Rectangle(
            PointType(min(xs), min(ys)),
            PointType(max(xs), min(ys)),
            PointType(max(xs), max(ys)),
            PointType(min(xs), max(ys)),
        )

    def containing_rectangle_offsets(self):
        """Compute offset between self and containing rectangle."""
        d_upper_y = self.right_upper.y - self.left_upper.y
        d_lower_y = self.left_upper.y - self.left_lower.y
        alpha = self.left_upper.rotation_angle(self.right_upper)
        return (d_lower_y * sin(alpha), d_upper_y * cos(alpha))

    def to_image_rectangle(
        self, canvas_width, canvas_height, image_width, image_height
    ):
        """Transform self in canvas coordinates to rectangle in image coordinates."""
        return Rectangle(
            *[
                point.to_image_coordinates(
                    canvas_width, canvas_height, image_width, image_height
                )
                for point in self
            ]
        )


class CropCanvas(Canvas):
    """Canvas supporting image crop by mouse drag + click."""

    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = image
        self.circle = None
        self.rectangle = None
        self.projected = None
        self.lu = None
        self.rl = None
        self.selected_rectangle = None
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<Motion>", self.on_mousemove)
        self.bind("<Configure>", self.on_resize)

    def redraw_image(self):
        self.winfo_toplevel().update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        iw, ih = rescaled_image_size(w, h, self.image.width, self.image.height)
        image_resized = self.image.resize((iw, ih), Image.Resampling.NEAREST)
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
            x1, y1, _, _, x2, y2, _, _ = (
                r.containing_rectangle()
                .to_image_rectangle(
                    canvas_width,
                    canvas_height,
                    self.image.width,
                    self.image.height,
                )
                .flatten()
            )
            cont_rect = self.image.crop((x1, y1, x2, y2)).rotate(
                -degrees(r.left_upper.rotation_angle(r.right_upper)),
                expand=True,
                resample=Image.Resampling.BICUBIC,
            )
            cont_rect_offsets = r.containing_rectangle_offsets()
            iw, _ = rescaled_image_size(
                canvas_width, canvas_height, self.image.width, self.image.height
            )
            ow, oh = tuple(abs(v) * self.image.width // iw for v in cont_rect_offsets)
            cont_rect.crop((ow, oh, cont_rect.width - ow, cont_rect.height - oh)).show()
        self._delete_circle_and_rectangle()
        self.rl = None
        self.lu = CanvasPoint(event.x, event.y)

    def on_drag(self, event):
        self._delete_circle_and_rectangle()
        self.rl = CanvasPoint(event.x, event.y)
        bbox_corner1, bbox_corner2 = self.lu.circle_bounding_box_from_diameter(self.rl)
        self.circle = self.create_oval(
            *(*bbox_corner1, *bbox_corner2), fill="", outline="red", width=2
        )

    def on_mousemove(self, event):
        if self.rectangle:
            self.delete(self.rectangle)
        if self.projected:
            self.delete(self.projected)
        if self.lu and self.rl:
            center = self.lu.middle_between(self.rl)
            r = abs(center - self.lu)
            corner1 = CanvasPoint(event.x, event.y).project_to_circle_around(center, r)
            self.projected = self.create_oval(
                corner1.x - 5,
                corner1.y - 5,
                corner1.x + 5,
                corner1.y + 5,
                fill="yellow",
            )
            corner2 = corner1.central_inversion_through(center)
            self.selected_rectangle = Rectangle(
                self.lu,
                corner1,
                self.rl,
                corner2,
            )
            self.rectangle = self.create_polygon(
                *self.selected_rectangle.flatten(),
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
