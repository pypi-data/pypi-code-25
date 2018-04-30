from .right_angle import gen_right_angle_problem, RightAngleProblem
from .graph_transforms import generate_graph_transform_problem, GraphTransformProblem
from .unit_circle_eval import generate_unit_circle_eval_problem, UnitCircleEvalProblem
from .unit_circle_graph import generate_unit_circle_graph_problem, UnitCircleGraphProblem


def right_angle(level: int = 1) -> RightAngleProblem:
    return gen_right_angle_problem(level)


def graph_transform(level: int = 1) -> GraphTransformProblem:
    return generate_graph_transform_problem(level)


def unit_circle_eval(level: int = 1) -> UnitCircleEvalProblem:
    return generate_unit_circle_eval_problem(level)


def unit_circle_graph(level: int = 1) -> UnitCircleGraphProblem:
    return generate_unit_circle_graph_problem(level)
