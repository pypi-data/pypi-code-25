'''
Author: Daniel Dowsett 05/2018
'''
class EquationTemplate():
        def __init__(self, num_eqs, lhs_min, lhs_max_dec, lhs_max, ops, 
                     rhs_min, rhs_max_dec, rhs_max, ms_pause, ans_max_dec):
            """
            Validates and cleans arguments. self.valid = false if there's a problem.
            The problem is then stored in self.problem_message
            """
            self.num_eqs = num_eqs
            self.lhs_min = lhs_min
            self.lhs_max_dec = lhs_max_dec
            self.lhs_max = lhs_max
            self.ops = ops
            self.rhs_min = rhs_min
            self.rhs_max_dec = rhs_max_dec
            self.rhs_max = rhs_max  
            self.ms_pause = ms_pause
            self.ans_max_dec = ans_max_dec
            self.problem_message = None
            self.valid = True           

            #max has ot be greater than min
            if self.lhs_min > self.lhs_max or self.rhs_min > self.rhs_max:
                self.valid = False
                self.problem_message = "Maximums must be greater than minimums"

            # get rid of multiple ops
            # but keeps power and multiplication
            num_asterixes = self.ops.count("*")
            self.ops = set(self.ops)
            self.ops.discard("*")
            if num_asterixes == 1:
                self.ops.add("*")
            elif num_asterixes == 2:
                self.ops.add("**")
            elif num_asterixes == 3:
                self.ops.add("*")
                self.ops.add("**")


