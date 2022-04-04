import unittest
from math import cos, sin, pi

from blitzcrop import parser, circle_bounding_box_from_diameter


class TestBlitzcrop(unittest.TestCase):
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
