from evtol.uav_data import Constants, DesignParameters
from evtol.constraint_analysis import cruise_constraint, rate_climb_constraint, stall_constraint
import numpy as np
import scipy
from scipy.optimize._constraints import NonlinearConstraint, LinearConstraint, Bounds


class Optimizer(object):
    def __init__(self, constants: Constants, design_parameters: DesignParameters):
        self.constants = constants
        self.design_parameters = design_parameters
        self.constraints = {}
        self._cost_function = None

    @property
    def cost_function(self):
        return self._cost_function

    @cost_function.setter
    def cost_function(self, func):
        if callable(func):
            self._cost_function = func

    def add_constraint(self, key, min, max):
        if key not in self.design_parameters.__dict__.keys():
            raise KeyError("Constraint key is not in design parameters")
        if max < min:
            raise ValueError("Maximum should be higher than minimum")
        self.constraints[key] = {'min': min, 'max': max}

    def generate_bounds(self):
        min_vector = np.ones((len(self.design_parameters.__dict__))) * -np.inf
        max_vector = np.ones((len(self.design_parameters.__dict__))) * np.inf
        names_design_param, _ = self.design_parameters.vectorize()
        for i, name in enumerate(self.constraints.keys()):
            min_vector[i] = self.constraints[name]['min']
            max_vector[i] = self.constraints[name]['max']
        bounds = Bounds(min_vector, max_vector)
        return bounds

    def generate_linear_constraints(self):
        """Generate constraint matrix from dict of constraints.
        The matrix has size num. design param x num. constraints
        :return:
        """
        contraint_matrix = np.zeros((len(self.constraints), len(self.design_parameters.__dict__)))
        min_vector = np.ones((len(self.design_parameters.__dict__))) * -np.inf
        max_vector = np.ones((len(self.design_parameters.__dict__))) * np.inf
        names_design_param, _ = self.design_parameters.vectorize()

        for i, name in enumerate(self.constraints.keys()):
            column_id = names_design_param.index(name)
            contraint_matrix[i, column_id] = 1
            min_vector[i] = self.constraints[name]['min']
            max_vector[i] = self.constraints[name]['max']

        constraint = LinearConstraint(contraint_matrix, min_vector, max_vector)
        return constraint

    def generate_non_linear_constraints(self):
        names_design_param, _ = self.design_parameters.vectorize()
        cruise_func = cruise_constraint(self.constants, self.design_parameters)
        roc_func = rate_climb_constraint(self.constants, self.design_parameters)
        stall_func = stall_constraint(self.constants, self.design_parameters)

        def stall_ineq(x):
            return -x[names_design_param.index('wing_loading')] + stall_func(x)

        def cruise_ineq(x):
            return x[names_design_param.index('power_over_weight')] - cruise_func(
                x[names_design_param.index('wing_loading')])

        def roc_ineq(x):
            return x[names_design_param.index('power_over_weight')] - roc_func(
                x[names_design_param.index('wing_loading')])

        # stall_final_const = NonlinearConstraint(stall_fun_opt, 0, np.inf)
        # cruise_final_const = NonlinearConstraint(cruise_fun_opt, 0, np.inf)
        # roc_final_const = NonlinearConstraint(roc_fun_opt, 0, np.inf)

        cons = ({'type': 'ineq', 'fun': cruise_ineq},
                {'type': 'ineq', 'fun': roc_ineq},
                {'type': 'ineq', 'fun': stall_ineq})
        return cons

    def solve(self):
        _, x0 = self.design_parameters.vectorize()
        bounds = self.generate_bounds()
        non_linear_cons = self.generate_non_linear_constraints()

        def callback(x, state):
            print(state)

        optimized_parameters = scipy.optimize.minimize(self.cost_function, x0,
                                                      bounds=bounds, constraints=non_linear_cons)
        return optimized_parameters
