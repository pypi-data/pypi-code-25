from typing import List
from .point2 import Point2

from io import StringIO

import math


def triangle(a: Point2, b: Point2, c: Point2) -> str:
    return '<polygon points="{},{} {},{} {},{}" style="fill:none;stroke:black;" />\n'.format(
        a.x, a.y, b.x, b.y, c.x, c.y
    )


def polyline(points: List[Point2], color_r: int, color_g: int, color_b: int) -> str:
    point_list = StringIO()

    for point in points:
        point_list.write("{}, {} ".format(point.x, point.y))

    return '<polyline points="{}" style="fill:none;stroke:rgb({}, {}, {});" />\n'.format(
        point_list.getvalue(), color_r, color_g, color_b
    )


def text(pos: Point2, text: str) -> str:
    return '<text x="{}" y="{}" fill="black" font-size="12" text-anchor="middle" >{}</text>\n'.format(
        pos.x, pos.y, text
    )


def line(a: Point2, b: Point2, color_r: int = 0, color_g: int = 0, color_b: int = 0) -> str:
    return '<line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:rgb({},{},{});" />'.format(
        a.x, a.y, b.x, b.y, color_r, color_g, color_b
    )


def sweep_circle(center: Point2, radius: float, start_angle: float, end_angle: float) -> str:
    step_size = 25
    step = (end_angle - start_angle) / float(step_size)
    curr_angle = start_angle

    pt_str = ""

    for i in range(step_size+1):
        curr_radian = -math.radians(curr_angle)

        x = center.x + (math.cos(curr_radian) * radius)
        y = center.y + (math.sin(curr_radian) * radius)

        pt_str += "{},{} ".format(x, y)

        curr_angle = min(end_angle, curr_angle + step)

    return '<polyline points="{}" style="fill:none;stroke:black" />'.format(pt_str)
