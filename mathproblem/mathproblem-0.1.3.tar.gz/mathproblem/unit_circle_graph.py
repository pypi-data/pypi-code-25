from typing import List

from .problem import Problem
from .simple_svg import line, sweep_circle
from .point2 import Point2

from .trig_defs import deg

import random
import math


class UnitCircleGraphProblem(Problem):
    def __init__(self):
        Problem.__init__(self)

    def __repr__(self):
        return str.format("Unit Circle Graph Problem ({}): {}", self.level, self.prompt)


def _generate_diagram(start_angle: float, end_angle: float) -> str:
    center = Point2(60, 60)
    radius = 50.0
    line_length = radius * 1.25
    end_radians = -math.radians(end_angle)
    end_point = Point2.add(center, Point2(math.cos(end_radians) * line_length, math.sin(end_radians) * line_length))

    top = Point2.add(center, Point2(0, line_length))
    bottom = Point2.add(center, Point2(0, -line_length))
    left = Point2.add(center, Point2(-line_length, 0))
    right = Point2.add(center, Point2(line_length, 0))

    svg_text = "<svg>"
    svg_text += sweep_circle(center, radius, start_angle, end_angle)
    svg_text += line(center, end_point)
    svg_text += line(top, bottom)
    svg_text += line(left, right)
    svg_text += "</svg>"

    return svg_text


def _get_distractor(index, offset, min_index, max_index ) -> int:
    test_index = index + offset

    if test_index < min_index:
        return max_index - (min_index - test_index - 1)
    elif test_index > max_index:
        return min_index + (test_index - max_index - 1)
    else:
        return test_index


def _get_indices(min_index, max_index) -> List[int]:
    indices: List[int] = list()

    target = random.randint(min_index, max_index)
    indices.append(target)

    for i in range(1, 3):
        indices.append(_get_distractor(target, i, min_index, max_index))
        indices.append(_get_distractor(target, -i, min_index, max_index))

    return indices


def generate_unit_circle_graph_problem(level: int = 1) -> UnitCircleGraphProblem:
    problem = UnitCircleGraphProblem()
    problem.level = level

    indices: List[int] = list()
    for i in range(4):
        indices.append(random.randint(1, len(deg) - 2))

    for index in indices:
        angle = deg[index]
        problem.diagram.append(_generate_diagram(0, float(angle)))

    answer_index = random.randint(0, 3)

    problem.prompt = "Chose the corect graph for: {}".format(deg[indices[answer_index]])
    problem.answer = str(answer_index)

    return problem

