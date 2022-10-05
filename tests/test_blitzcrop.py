import unittest
from math import cos, sin, pi, degrees

from blitzcrop import (
    parser,
    circle_bounding_box_from_diameter,
    rescaled_image_size,
    ImagePoint,
    CanvasPoint,
)


class TestBlitzcrop(unittest.TestCase):
    def assertPointAlmostEqual(self, point_expected, point_actual):
        self.assertAlmostEqual(point_expected[0], point_actual[0])
        self.assertAlmostEqual(point_expected[1], point_actual[1])

    def assertBoxAlmostEqual(self, box_expected, box_actual):
        self.assertAlmostEqual(box_expected[0], box_actual[0])
        self.assertAlmostEqual(box_expected[1], box_actual[1])
        self.assertAlmostEqual(box_expected[2], box_actual[2])
        self.assertAlmostEqual(box_expected[3], box_actual[3])

    def test_argument_parsing(self):
        args = parser.parse_args([])
        self.assertEqual(args.version, False)
        args = parser.parse_args(["--version"])
        self.assertEqual(args.version, True)

    def test_point_matching_type_assertions(self):
        a = ImagePoint(1, 2)
        b = ImagePoint(3, 4)
        c = CanvasPoint(5, 6)
        self.assertRaises(AssertionError, lambda: a + c)
        self.assertRaises(AssertionError, lambda: a - c)
        a + b
        a - b

    def test_point_arithmetic(self):
        a = ImagePoint(1, 2)
        b = ImagePoint(3, 4)
        self.assertEqual(a + b - b, a)
        self.assertEqual(0.5 * a * 2, a)

    def test_central_inversion(self):
        a = CanvasPoint(1, 2)
        b = a.central_inversion_through(CanvasPoint(0, 0))
        self.assertEqual(a, -b)

    def test_circle_bounding_box_from_diameter(self):
        bbox = circle_bounding_box_from_diameter(0, 0, 0, 0)
        self.assertBoxAlmostEqual((0, 0, 0, 0), bbox)
        bbox = circle_bounding_box_from_diameter(50, 0, 50, 100)
        self.assertBoxAlmostEqual((0, 0, 100, 100), bbox)
        bbox = circle_bounding_box_from_diameter(0, 0, 100, 0)
        self.assertBoxAlmostEqual((0, -50, 100, 50), bbox)
        phi = 0
        while phi < 2 * pi:
            x1 = 50 * (1 + cos(phi))
            y1 = 50 * (1 + sin(phi))
            x2 = 50 * (1 + cos(phi + pi))
            y2 = 50 * (1 + sin(phi + pi))
            bbox = circle_bounding_box_from_diameter(x1, y1, x2, y2)
            self.assertBoxAlmostEqual((0, 0, 100, 100), bbox)
            phi += 0.1 * pi

    def test_project_to_circle(self):
        p = CanvasPoint(50, 0).project_to_circle_around(CanvasPoint(0, 0), 100)
        self.assertPointAlmostEqual((100, 0), p)
        p = CanvasPoint(200, 0).project_to_circle_around(CanvasPoint(0, 0), 100)
        self.assertPointAlmostEqual((100, 0), p)
        p = CanvasPoint(0, 50).project_to_circle_around(CanvasPoint(0, 0), 100)
        self.assertPointAlmostEqual((0, 100), p)
        p = CanvasPoint(0, 200).project_to_circle_around(CanvasPoint(0, 0), 100)
        self.assertPointAlmostEqual((0, 100), p)
        phi = 0
        while phi < 2 * pi:
            x = 50 * (1 + cos(phi))
            y = 50 * (1 + sin(phi))
            p = CanvasPoint(x, y).project_to_circle_around(CanvasPoint(0, 0), 100)
            self.assertAlmostEqual(100, (p[0] ** 2 + p[1] ** 2) ** 0.5)
            phi += 0.1 * pi

    def test_rescaled_image_size(self):
        # square image
        s = rescaled_image_size(100, 100, 100, 100)
        self.assertPointAlmostEqual((100, 100), s)
        s = rescaled_image_size(200, 100, 100, 100)
        self.assertPointAlmostEqual((100, 100), s)
        s = rescaled_image_size(100, 50, 100, 100)
        self.assertPointAlmostEqual((50, 50), s)
        s = rescaled_image_size(200, 150, 100, 100)
        self.assertPointAlmostEqual((150, 150), s)
        s = rescaled_image_size(150, 200, 100, 100)
        self.assertPointAlmostEqual((150, 150), s)
        # portrait image
        s = rescaled_image_size(100, 100, 100, 200)
        self.assertPointAlmostEqual((50, 100), s)
        s = rescaled_image_size(200, 300, 100, 200)
        self.assertPointAlmostEqual((150, 300), s)
        s = rescaled_image_size(300, 200, 100, 200)
        self.assertPointAlmostEqual((100, 200), s)
        # landscape image
        s = rescaled_image_size(100, 100, 200, 100)
        self.assertPointAlmostEqual((100, 50), s)
        s = rescaled_image_size(200, 300, 200, 100)
        self.assertPointAlmostEqual((200, 100), s)
        s = rescaled_image_size(300, 200, 200, 100)
        self.assertPointAlmostEqual((300, 150), s)

    def test_rotation_angle(self):
        angle = CanvasPoint(0, 0).rotation_angle(CanvasPoint(1, 0))
        self.assertAlmostEqual(0, angle)
        angle = CanvasPoint(100, 100).rotation_angle(CanvasPoint(200, 100))
        self.assertAlmostEqual(0, angle)
        angle = degrees(CanvasPoint(100, 100).rotation_angle(CanvasPoint(200, 200)))
        self.assertAlmostEqual(-45, angle)
        angle = degrees(CanvasPoint(100, 100).rotation_angle(CanvasPoint(200, 0)))
        self.assertAlmostEqual(45, angle)
        angle = degrees(CanvasPoint(100, 100).rotation_angle(CanvasPoint(100, 200)))
        self.assertAlmostEqual(-90, angle)
        angle = degrees(CanvasPoint(100, 100).rotation_angle(CanvasPoint(100, 0)))
        self.assertAlmostEqual(90, angle)
