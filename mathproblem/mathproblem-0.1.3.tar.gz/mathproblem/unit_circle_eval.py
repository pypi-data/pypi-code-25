from typing import List

from .problem import Problem
from .trig_defs import RightAngleTrigFunction, AngleType, deg, rad

import random
import re


cos_v: List[str] = ["1", "sqrt(3)/2", "sqrt(2)/2", "1/2", "0",
                    "-1/2", "-sqrt(2)/2", "-sqrt(3)/2", "-1",
                    "-sqrt(3)/2", "-sqrt(2)/2", "-1/2", "0",
                    "1/2", "sqrt(2)/2", "sqrt3)/3", "1"]

sin_v: List[str] = ["0", "1/2", "sqrt(2)/2", "sqrt(3)/2", "1",
                    "sqrt(3)/2", "sqrt(2)/2", "1/2", "0",
                    "-1/2", "-sqrt(2)/2", "-sqrt(3)/2", "-1",
                    "-sqrt(3)/2", "-sqrt(2)/2", "-1/2", "0"]


class UnitCircleEvalProblem(Problem):
    def __init__(self):
        Problem.__init__(self)

    def __repr__(self):
        return str.format("Unit Circle Eval Problem ({}): {}", self.level, self.prompt)


def _get_display_text(text_str:str) -> str:
    p = re.compile(r"sqrt\((?P<num>.)\)")
    return p.sub('&radic;<span style="text-decoration: overline">\g<num></span>', text_str)


def generate_unit_circle_eval_problem(level: 1) -> UnitCircleEvalProblem:
    trig_func = RightAngleTrigFunction(random.randint(1, 2))
    angle_type = AngleType(random.randint(0, 1))

    index = random.randint(0, len(deg)-1)

    problem = UnitCircleEvalProblem()
    problem.level = level

    if angle_type == AngleType.Degrees:
        angle_measure = deg[index]
        problem.steps.append("Observe that {} degrees = {} radians".format(deg[index], rad[index]))
        problem.diagram.append("degrees")
    else:
        angle_measure = rad[index]
        problem.steps.append("Observe that {} radians = {} degrees".format(rad[index], deg[index]))
        problem.diagram.append("radians")

    if trig_func == RightAngleTrigFunction.Sin:
        problem.answer = sin_v[index]
    else:
        problem.answer = cos_v[index]

    query = "{}({})".format(trig_func.name.lower(), angle_measure)
    problem.steps.append("Recall that {} is {}".format(query, _get_display_text(problem.answer)))
    problem.prompt = "Find {}".format(query)

    return problem
