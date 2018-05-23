"""
EasyMunk provides an interface alternative to the Munkres module for score-based (Hungarian algorithm) assignments.


Benefits and Overview
_____________________
The EasyMunk module interfaces with the Munkres module to:
    1. Provide an easy and adaptable method of pair assignment.
    2. Reduce the amount of pre-processing required for Munkres.
    3. Automatically account for some special-case Munkres decisions.
    4. Do all of the above without reducing Munkres' functionality.

Ultimately, EasyMunk's goal is to reduce the number of steps necessary in implementing cost or profit based
sorting/assignments.

Creating an array/list of every pairing, calculating the cost of every pairing, validating the optimized cost indexes,
using the validated cost indexes to identify the pair which created the cost within, and then
creating an assignment for each object in the pair is still a core part of a typical Hungarian algorithm process.

The EasyMunk class will handle these processes for you. The actual method in which you calculate
the cost per pair will need to be passed to the EasyMunk.sort() method as cost_function;
as will the assignment method to run per each optimal pair as assignment_function.


Suggestions
___________
cost_function as a Profit Function{
The Hungarian algorithm uses cost, not profit. However, it can still be used to assign based on profit.
The Munkres module has documentation available on creating a cost matrix from a profit matrix. If you set
convert_profit_to_cost to True without supplying a profit_to_cost_function, the default profit inversion
function subtracts each value from the maximum value in the matrix to represent cost. It has been expanded
by EasyMunk to allow munkres.DISALLOWED values to be passed instead of a numeric profit value.
}


cost_function and assignment_function Basic Implementation{
99.9% of the time, I use a static method within one of the two objects' classes for both functions.
If, instead of a module level function, you directly pass
    an object's method as (either
        cost_function or assignment_function) (
        and the method you use is not a static method):
            be aware that the namespace of the method will always
            be the same as the object which first passed the method to EasyMunk.
            The same goes for any function passed to EasyMunk.
}


cost_function and assignment_function Dynamic Function Selection{
If you wish to dynamically choose functions for cost calculation, you might create a static method which then calls upon
an internal consistently-named method in each input class - using the returned object to search its namespace for
the correct version of the method; i.e., use primary.its_cost_function() inside of the coordinating cost_function
passed to EasyMunk instead of relying on cost_function to perform calculations.

You might consider creating a HungarianObject base class from which all possibly sorted objects draw from,
and then redefining/modifying the cost and assignment method in each subclass.
}


Cost and Assignment Examples
____________________________
'''
Here is an example of a potential general cost function using the distance between two objects,
and a general assignment function.

Your call to the sorter object would look like:
EasyMunk.sort(your_primary_object_list, your_secondary_object_list, calculate_distance, assign_pair)
'''
import math


# Example of a module cost function which uses distance for cost - any numeric metric can work instead of distance.
def calculate_distance(primary, secondary):
    '''Calculate the distance between two locations represented as objects, dictionaries, or lists.'''
    try:
        x_distance = primary.x - secondary.x  # Calculate Object attribute:value cost.
        y_distance = primary.y - secondary.y
    except AttributeError:
        try:
            x_distance = primary['x'] - secondary['x']  # Calculate Dictionary key:value cost.
            y_distance = primary['y'] - secondary['y']
        except TypeError:
            x_distance = primary[0] - secondary[0]  # Calculate List index:value cost.
            y_distance = primary[1] - secondary[1]
    distance = math.sqrt(math.pow(x_distance, 2) + math.pow(y_distance, 2))
    return distance


# Example of a module assignment function which only creates an assigment reference in the primary object.
def assign_pair(primary, secondary):
    '''Assign two objects to eachother.'''
    try:
        primary.assigned_pair = secondary  # Assign Object attribute:value
    except AttributeError:
        try:
            primary['assigned_pair'] = secondary  # Assign Dictionary key:value
        except TypeError:
            primary.append(secondary)  # Assign List index:value cost.

____
'''
Alternatively, you might want to change the function per object class in the primary_objects list.

Your call to the sorter object would look like:
EasyMunk.sort(your_primary_object_list, your_secondary_object_list, call_hungarian_cost_method, call_assign_pair)
'''
import math
import munkres


# General module level function passed to EasyMunk for calling the 'actual' cost calculation method.
def call_hungarian_cost_method(primary, secondary):
        '''Find the score of an object pair using the primary object's method.'''
        score = primary.calculate_hungarian_score(secondary)
        return score


# General module level function passed to EasyMunk for calling the 'actual' pair assignment method.
def call_assign_pair(primary, secondary):
        '''Assign pair.'''
        primary.assign_pair(secondary)


# Base class from which all matched object classes are subclassed.
class BaseHungarianObject(object):
    '''Parent class for objects which need to match other objects/tasks using cost or profit.'''
    def __init__(self):
        pass

    @staticmethod
    def calculate_hungarian_score(_):
        '''Placeholder score method; returns un-assignable score if used.'''
        return munkres.DISALLOWED

    @staticmethod
    def assign_pair(_):
        '''Placeholder assignment method.'''
        pass


# Basic matched object subclass.
class ExampleHungarianObject(BaseHungarianObject):
    '''Example subclass of BaseHungarianObject.'''
    def __init__(self, x, y):
        '''Example subclass __init__'''
        super(ExampleHungarianObject, self).__init__()
        self.x = x
        self.y = y
        self.assigned_pair = None

    def calculate_hungarian_score(self, secondary):
        '''Example score method using distance as cost.'''
        x_distance = self.x - secondary.x
        y_distance = self.y - secondary.y
        distance = math.sqrt(math.pow(x_distance, 2) + math.pow(y_distance, 2))
        return distance

    def assign_pair(self, secondary):
        '''Example basic assignment method.'''
        self.assigned_pair = secondary
        try:
            secondary.assigned_pair = self
        except AttributeError:
            pass


# Example of a matched object subclass which uses a different cost and assignment function.
class ExampleHungarianObjectDifferentMethods(ExampleHungarianObject):
    '''Example subclass of ExampleHungarianObject.'''
    def __init__(self, child_only_attribute, *args):
        '''Example ExampleHungarianObject subclass __init__'''
        super(ExampleHungarianObjectDifferentMethods, self).__init__(*args)
        self.example_attribute = child_only_attribute

    def calculate_hungarian_score(self, secondary):
        '''Example score method.'''
        x_distance = self.x - secondary.x
        score = x_distance * self.example_attribute
        return score

    def assign_pair(self, secondary):
        '''Example of an assignment method which changes based on object class.'''
        self.assigned_pair = secondary.some_referenced_object_in_secondary

____
EasyMunk module by Andrew M. Hogan. (EasyMunk Copyright 2018 Hogan Consulting Group)
"""
import munkres


class EasyMunk(object):
    """Match two groups using the cost-minimizing Hungarian algorithm."""
    Forbidden = munkres.DISALLOWED  # Optional EZ DISALLOWED value.
    _primary_default_name = "primary"  # Key for primary object.
    _secondary_default_name = "secondary"  # Key for secondary object.
    _score_default_name = "score"  # Key for score value.
    _score_methods_internal = []  # Initial score methods syntax list set by _internal_methods.
    _profit_to_cost_methods_internal = []  # Profit to cost conversion syntax list set by _internal_methods.
    _profit_to_cost_argument_indexes_internal = []  # Profit to cost syntax index list set by _internal_methods.
    _assign_methods_internal = []  # Assignment function syntax list set by _internal_methods.
    last_profit_matrix = None  # Last profit matrix, if convert to cost matrix was set to True.
    last_cost_matrix = None  # Last cost matrix.
    last_chosen_indexes = None  # Last [primary_objects, secondary_objects] indices chosen by Munkres.
    last_total_cost = None  # Last total cost as calculated by chosen indices -> last_cost_matrix
    last_total_profit = None  # Last total profit as calculated by chosen indices -> last_profit_matrix (if it exists)

    def __init__(self):
        """Placeholder __init__ method."""
        pass

    @classmethod
    def print_info(cls):
        """Print EasyMunk profit & cost matrices, along with Munkres chosen indexes and total cost & profit."""
        print("____")
        if cls.last_profit_matrix:
            print("\nProfit Matrix: ")
            munkres.print_matrix(cls.last_profit_matrix)
        if cls.last_cost_matrix:
            print("\nCost Matrix: ")
            munkres.print_matrix(cls.last_cost_matrix)
        else:
            print("No info to print.")
        if cls.last_chosen_indexes:
            print("\nSelected Match Indexes: ")
            print("(primary index, secondary index)")
            print(cls.last_chosen_indexes)
        if cls.last_total_cost is not None:
            print("\nTotal Cost: " + str(cls.last_total_cost))
        if cls.last_total_profit is not None:
            print("Total Profit: " + str(cls.last_total_profit))
        print("____")

    @classmethod
    def _set_class_internal_methods(cls):
        """Set supplied function internal call syntax methods."""
        # Tested until working syntax is found, then places that syntax as the starting point for further calls.
        if not cls._score_methods_internal:
            # Default scoring supplied function call syntaxes.
            cls._score_methods_internal = [cls._call_function_with_args_kwargs,
                                           cls._call_function_with_kwargs,
                                           cls._call_function_no_args_nor_kwargs]
        if not cls._profit_to_cost_methods_internal:
            # Default profit conversion supplied function call syntaxes.
            cls._profit_to_cost_methods_internal = [cls._call_function_with_args_kwargs,
                                                    cls._call_function_with_kwargs,
                                                    cls._call_function_no_args_nor_kwargs]
        if not cls._profit_to_cost_argument_indexes_internal:
            # Default profit conversion internal arguments supplied per syntax attempt loop.
            cls._profit_to_cost_argument_indexes_internal = [4, 3, 1]
        if not cls._assign_methods_internal:
            # Default assigning supplied function call syntaxes.
            cls._assign_methods_internal = [cls._call_function_with_args_kwargs,
                                            cls._call_function_with_kwargs,
                                            cls._call_function_no_args_nor_kwargs]

    @classmethod
    def sort(cls, primary_objects, secondary_objects, score_function, assignment_function,
             *args, convert_profit_to_cost=False, profit_to_cost_function=None, **kwargs):
        """
        Determine pair scores between primary and secondary objects using the supplied cost function,
        then determine primary object to secondary object assignments using the Hungarian algorithm,
        then create references to those assignments using the supplied assignment function.
        ____
        Limitations / Options:
        Set an assignment as disallowed in your assignment function using munkres.DISALLOWED.

        Will raise munkres.UnsolvableMatrix (Exception) if optimal pairings cannot be determined.

        The Hungarian algorithm only supports rectangle (square included) cost matrices. EasyMunk accounts
        for this limitation on its own. However, you can create (effectively) irregular-shaped cost
        matrices using the munkres.DISALLOWED value. You might create a class or attribute based exclusion
        statement in your cost_function, or a method called within each class to exclude matches with
        certain classes.
        ____
        sort()

        :Parameters:
            :param list primary_objects: primary_objects: List of anything you wish to assign an object/task/etc.
            :param list secondary_objects: List of anything you wish to assign primary_objects to.
            :param function score_function: Score function for each possible pair; must return a numeric metric.
                score_function input: primary_object, secondary_object, *args, **kwargs.
                score_function return float: Your cost function's return should be an int or float or munkres.DISALLOWED
                representing that match's cost or profit.
            :param function assignment_function: Function for operating on pair assignments externally.
                assignment_function input: primary_object, secondary_object, *args, **kwargs.
                assignment_function return None: Your assignment function should not return anything.
            :param bool convert_profit_to_cost: Determine if profit to cost function is used.
            :param function profit_to_cost_function: If None and convert_profit_to_cost is True,
                    default conversion of (cost_index_value = max(profit_array) - profit_index_value) is used.
                profit_to_cost_function input: single profit value, *args, **kwargs.
                profit_to_cost_function return float: Your conversion function's return should be the same
                type as the cost_function's return; in other words, a numeric value.
            *args: tuple
                Optional arguments passed to score_function, assignment_function, and profit_to_cost_function.
            **kwargs: dict
                Optional keyword arguments passed to score_function, assignment_function, and profit_to_cost_function.

        :rtype: None
        :return: None
        ____
            score_function()

            inputs:
            primary_object of type [whatever type you passed a list of as primary_objects, can be anything]
            secondary_object of type [whatever type you passed a list of as secondary_objects, can be anything]
            *args & **kwargs for optional score calculation inputs

            returns:
            pair score (Typically an int or float, or munkres.DISALLOWED if the pairing cannot happen)
        ____
            assigment_function()

            inputs:
            primary_object of type [whatever type you passed a list of as primary_objects, can be anything]
            secondary_object of type [whatever type you passed a list of as secondary_objects, can be anything]
            *args & **kwargs for optional assignment output processing variables

            returns:
            -None
        ____
            profit_to_cost_function()

            inputs:
            single profit value of numeric type (Typically an int or float, or munkres.DISALLOWED)
            optional input {primary_object, secondary_object} dict associated with the profit value
                only if pass_objects_for_convert is set to True
            optional input list of {primary_object, secondary_object, profit} dicts
                only if pass_objects_for_convert is set to True
            *args & **kwargs for optional cost calculation inputs

            returns:
            pair cost (Typically an int or float, or munkres.DISALLOWED if the pairing cannot happen)
        ____
        Underlying Hungarian algorithm implemented with the Munkres module.
        EasyMunk module by Andrew M. Hogan. (EasyMunk Copyright 2018 Hogan Consulting Group)
        """
        # Init internal working syntax for supplied function call caching.
        if (not cls._score_methods_internal
                or not cls._profit_to_cost_methods_internal
                or not cls._profit_to_cost_argument_indexes_internal
                or not cls._assign_methods_internal):
            cls._set_class_internal_methods()

        # Create cost (or profit -> cost) matrix.
        try:
            if convert_profit_to_cost:
                score_matrix, row_stacks = cls._create_and_score_profit_row_stacks(
                    primary_objects, secondary_objects, score_function, profit_to_cost_function, *args, **kwargs)
            else:
                cls.last_profit_matrix = None
                score_matrix, row_stacks = cls._create_and_score_row_stacks(
                    primary_objects, secondary_objects, score_function, "Normal", *args, **kwargs)
        except AssertionError:
            raise
        cls.last_cost_matrix = score_matrix[:]

        # Init Munkres and calculate optimal assignments.
        hungarian_object = munkres.Munkres()
        try:
            indexes = hungarian_object.compute(score_matrix)
        except munkres.UnsolvableMatrix:
            raise
        cls.last_chosen_indexes = indexes[:]

        # Validate and process assignments.
        chosen_pairs, cls.last_total_cost, cls.last_total_profit = cls._choose_pairs(
            indexes, len(primary_objects), len(secondary_objects), row_stacks, score_matrix, cls.last_profit_matrix)
        cls._assign_pairs(chosen_pairs, assignment_function, *args, **kwargs)

    @classmethod
    def _create_and_score_row_stacks(cls, primary_objects, secondary_objects, score_function, _ezmk_score_format,
                                     *args, **kwargs):
        """Create a list of dicts containing each pairing along with a list of each score."""
        _ezmk_score_formats = {"Normal": [["list_of_lists_of_pair_scores"], ["list_of_lists_of_pair_dict"]],
                               "&SingleDict": [["list_of_lists_of_pair_scores"], ["list_of_lists_of_pair_dict"],
                                               ["list_of_lists_of_score_primary_secondary_and_dict"]]
                               }
        score_methods = cls._score_methods_internal
        _ezmk_score_exports = tuple([] for _ in _ezmk_score_formats[_ezmk_score_format])
        for p_object in primary_objects:
            _ezmk_scores_this_row = tuple([] for _ in _ezmk_score_exports)
            for s_object in secondary_objects:
                new_pair = {cls._primary_default_name: p_object, cls._secondary_default_name: s_object}
                try:
                    score = cls._get_score(score_methods, score_function, new_pair, *args, **kwargs)
                except AssertionError:
                    raise
                cls._row_append(_ezmk_scores_this_row, [score, new_pair])
            for _ezmk_row_xp_id, _ezmk_row_xp_list in enumerate(_ezmk_scores_this_row):
                _ezmk_score_exports[_ezmk_row_xp_id].append(_ezmk_row_xp_list)
        return tuple(_ezmk_score_exports)

    @classmethod
    def _get_score(cls, score_methods, score_function, new_pair, *args, **kwargs):
        """Cycle function syntaxes until working is found, then return score if found or raise error."""
        chosen_method_id = score = None
        try:
            _function_arguments = [*new_pair.values(), args, kwargs]
        except (TypeError, SyntaxError):  # Python < 3.5 - will test later for exact error.
            _function_arguments = []  # Pretty sure it is just a TypeError though.
            for _val in new_pair.values():
                _function_arguments.append(_val)
            _function_arguments += [args, kwargs]
        for id_method, score_method in enumerate(score_methods):
            try:
                score = score_method(score_function, _function_arguments, 2)
            except TypeError:
                pass
            else:
                chosen_method_id = id_method
                break
        if chosen_method_id != 0:
            assert chosen_method_id is not None, cls._get_function_type_error_message(score_function, TypeError)
            score_methods[:] = score_methods[chosen_method_id:] + score_methods[:chosen_method_id]
        return score

    @classmethod
    def _row_append(cls, _ezmk_scores_this_row, _ezmk_append_arguments):
        """Append pair information to either two or three export fields."""
        for export_id, export_field in enumerate(_ezmk_scores_this_row):
            try:
                export_field.append(_ezmk_append_arguments[export_id])
            except IndexError:
                try:
                    export_field.append({cls._score_default_name: _ezmk_append_arguments[0],
                                         **_ezmk_append_arguments[1]})
                except (TypeError, SyntaxError):  # Python < 3.5
                    dict_for_export = {cls._score_default_name: _ezmk_append_arguments[0]}
                    for key, value in _ezmk_append_arguments[1].items():
                        dict_for_export[key] = value
                    export_field.append(dict_for_export)

    @classmethod
    def _create_and_score_profit_row_stacks(cls, primary_objects, secondary_objects, score_function,
                                            profit_to_cost_function, *args, **kwargs):
        """Convert a profit matrix to a cost matrix using profit_to_cost_conversion_function, or =Max-value default."""
        # If using default Munkres conversion.
        if profit_to_cost_function is None:
            # Use original score matrix creation
            score_matrix, row_stacks = cls._create_and_score_row_stacks(primary_objects, secondary_objects,
                                                                        score_function, "Normal", *args, **kwargs)

            maximum_value = max(max(value if value is not munkres.DISALLOWED else 0
                                    for value in row) for row in score_matrix)
            cost_matrix = []
            for row in score_matrix:
                cost_matrix.append([maximum_value - value if value is not munkres.DISALLOWED
                                    else munkres.DISALLOWED for value in row])
        else:
            # &SingleDict: Create list of {object, object, profit} dict for possible profit->cost conversion usage.
            score_matrix, row_stacks, all_profits_and_pairs = cls._create_and_score_row_stacks(
                primary_objects, secondary_objects, score_function, "&SingleDict", *args, **kwargs)
            profit_to_cost_argument_indexes = cls._profit_to_cost_argument_indexes_internal
            profit_to_cost_methods = cls._profit_to_cost_methods_internal
            cost_matrix = []
            for row in all_profits_and_pairs:
                row_scores = []
                for profit, primary, secondary in row:
                    try:
                        cost = cls._get_cost(profit_to_cost_argument_indexes, profit_to_cost_methods,
                                             profit_to_cost_function, profit, primary, secondary,
                                             all_profits_and_pairs, *args, **kwargs)
                    except AssertionError:
                        raise
                    row_scores.append(cost)
                cost_matrix.append(row_scores)
        cls.last_profit_matrix = score_matrix[:]
        return cost_matrix, row_stacks

    @classmethod
    def _get_cost(cls, profit_to_cost_argument_indexes, profit_to_cost_methods, profit_to_cost_function, profit,
                  primary, secondary, all_profits_and_pairs, *args, **kwargs):
        """Cycle function syntaxes until working is found, then return cost if found or raise error."""
        chosen_method_id = cost = chosen_arg_index_id = None
        _function_arguments = [profit, primary, secondary, all_profits_and_pairs, args, kwargs]
        for id_arg_index, argument_index in enumerate(profit_to_cost_argument_indexes):
            for id_method, convert_method in enumerate(profit_to_cost_methods):
                try:
                    cost = convert_method(profit_to_cost_function, _function_arguments, argument_index)
                except TypeError:
                    pass
                else:
                    chosen_arg_index_id = id_arg_index
                    chosen_method_id = id_method
                    break
        if chosen_method_id != 0:
            assert (chosen_method_id is not None), (
                cls._get_function_type_error_message(profit_to_cost_function, TypeError))
            profit_to_cost_methods[:] = (profit_to_cost_methods[chosen_method_id:]
                                         + profit_to_cost_methods[:chosen_method_id])
        if chosen_arg_index_id != 0:
            profit_to_cost_argument_indexes[:] = (profit_to_cost_argument_indexes[chosen_arg_index_id:]
                                                  + profit_to_cost_argument_indexes[:chosen_arg_index_id])
        return cost

    @staticmethod
    def _choose_pairs(indexes, primary_object_count, secondary_object_count, row_stacks, cost_matrix, profit_matrix):
        """Validate pair choices from munkres against number of real objects. (Munkres auto-pads to square matrix)"""
        total_cost = 0
        total_profit = 0
        chosen_pairs = []
        for row, column in indexes:
            if row < primary_object_count and column < secondary_object_count:
                chosen_pairs.append(row_stacks[row][column])
                total_cost += cost_matrix[row][column]
                try:
                    total_profit += profit_matrix[row][column]
                except TypeError:
                    total_profit = None
        return chosen_pairs, total_cost, total_profit

    @classmethod
    def _assign_pairs(cls, chosen_pairs, assignment_function, *args, **kwargs):
        """Set external references / assignments / actions from optimized pairs."""
        assign_methods = cls._assign_methods_internal
        chosen_method_id = None
        _python_strict_unpack = False
        for pair in chosen_pairs:
            try:
                _function_arguments = [*pair.values(), args, kwargs]
            except (TypeError, SyntaxError):  # Python < 3.5
                _python_strict_unpack = True
                _function_arguments = []
                for _val in pair.values():
                    _function_arguments.append(_val)
                _function_arguments += [args, kwargs]
            for id_method, assign_method in enumerate(assign_methods):
                try:
                    assign_method(assignment_function, _function_arguments, 2)
                except (TypeError, SyntaxError) as e:
                    if _python_strict_unpack:  # Python < 3.5
                        try:
                            _py_less_35_primary = pair[cls._primary_default_name]
                            _py_less_35_secondary = pair[cls._secondary_default_name]
                            assignment_function(_py_less_35_primary, _py_less_35_secondary, *args, **kwargs)
                        except TypeError:
                            pass
                        else:
                            chosen_method_id = id_method
                            break
                    elif isinstance(e, SyntaxError):  # NOT Python < 3.5 and not due to call syntax; raise except.
                        raise
                    else:
                        pass
                else:
                    chosen_method_id = id_method
                    break
            if chosen_method_id != 0:
                assert chosen_method_id is not None, (
                    cls._get_function_type_error_message(assignment_function, TypeError))
                assign_methods[:] = assign_methods[chosen_method_id:] + assign_methods[:chosen_method_id]

    @staticmethod
    def _get_function_type_error_message(function_with_error, error_type):
        """Create error message for supplied function and exception type."""
        error_message = ("Unable to use " + str(function_with_error.__name__)
                         + " without " + error_type.__name__ + ".")
        return error_message

    # Possible function call syntaxes.
    @staticmethod
    def _call_function_with_args_kwargs(supplied_function, arg_list, stop_arg_index):
        """Call supplied function with both *args and **kwargs."""
        return supplied_function(*arg_list[:stop_arg_index], *arg_list[-2], **arg_list[-1])

    @staticmethod
    def _call_function_with_kwargs(supplied_function, arg_list, stop_arg_index):
        """Call supplied function without *args, but with **kwargs."""
        return supplied_function(*arg_list[:stop_arg_index], **arg_list[-1])

    @staticmethod
    def _call_function_no_args_nor_kwargs(supplied_function, arg_list, stop_arg_index):
        """Call supplied function without either *args nor **kwargs."""
        return supplied_function(*arg_list[:stop_arg_index])

    @classmethod
    def change_function_syntax_defaults_and_order(cls, score_methods=None, profit_to_cost_methods=None,
                                                  profit_to_cost_argument_indexes=None, assign_methods=None):
        """Change the order or syntax of call function syntax attempts - not advised. All params are lists."""
        if score_methods:
            cls._score_methods_internal = score_methods
        if profit_to_cost_methods:
            cls._profit_to_cost_methods_internal = profit_to_cost_methods
        if profit_to_cost_argument_indexes:
            cls._profit_to_cost_argument_indexes_internal = profit_to_cost_argument_indexes
        if assign_methods:
            cls._assign_methods_internal = assign_methods

    @classmethod
    def change_default_dict_keys(cls, primary_name=None, secondary_name=None, score_name=None):
        """Change the dict key names - not advised. Params are any dict-key compatible type - cannot be None."""
        if primary_name is not None:
            cls._primary_default_name = primary_name  # Key for primary object.
        if secondary_name is not None:
            cls._secondary_default_name = secondary_name  # Key for secondary object.
        if score_name is not None:
            cls._score_default_name = score_name  # Key for score value.


if __name__ == '__main__':
    # Basic test object.
    class TestObject(object):
        """Example class for testing."""

        def __init__(self, *args):
            """Example __init__."""
            self.scores_array = None
            self.id_number = -1
            if len(args) > 1:
                self.scores_array = [arg for arg in args]
            else:
                self.id_number = args[0]
            self.assigned_pair = None

        @staticmethod
        def calculate_hungarian_score(primary, secondary):
            """Example score method from array."""
            return primary.scores_array[secondary.id_number]

        @staticmethod
        def assign_pair(primary, secondary):
            """Example assignment method."""
            primary.assigned_pair = secondary
            secondary.assigned_pair = primary

    # Some test cost matrices used by Munkres for its test validation.
    all_matrices = [
        ([[400, 150, 400],
          [400, 450, 600],
          [300, 225, 300]], 850),
        ([[400, 150, 400, 1],
         [400, 450, 600, 2],
         [300, 225, 300, 3]], 452),
        ([[10, 10, 8],
         [9, 8, 1],
         [9, 7, 4]], 18),
        ([[10, 10, 8, 11],
         [9, 8, 1, 1],
         [9, 7, 4, 10]], 15),
        ([[4, 5, 6, munkres.DISALLOWED],
         [1, 9, 12, 11],
         [munkres.DISALLOWED, 5, 4, munkres.DISALLOWED],
         [12, 12, 12, 10]], 20),
        ([[1, munkres.DISALLOWED, munkres.DISALLOWED, munkres.DISALLOWED],
          [munkres.DISALLOWED, 2, munkres.DISALLOWED, munkres.DISALLOWED],
          [munkres.DISALLOWED, munkres.DISALLOWED, 3, munkres.DISALLOWED],
          [munkres.DISALLOWED, munkres.DISALLOWED, munkres.DISALLOWED, 4]], 10)]

    # Run test for each matrix.
    for matrix, check_cost in all_matrices:
        # Create test primary objects.
        test_primary_objects = []
        for test_row in matrix:
            test_primary_objects.append(TestObject(*test_row))

        # Create test secondary objects.
        num_columns = len(matrix[0])
        test_secondary_objects = []
        for test_column in range(num_columns):
            test_secondary_objects.append(TestObject(test_column))

        # Optional args.
        some_optional_args = [35324234, 28, "purple", -98918247, "for the robolution", -5]
        some_optional_kwargs = {"random_value": 100000, "and_another": 24365674, "yet_another": "because_why_not"}

        # Run test.
        EasyMunk.sort(test_primary_objects, test_secondary_objects,
                      TestObject.calculate_hungarian_score, TestObject.assign_pair,
                      *some_optional_args, **some_optional_kwargs)
        EasyMunk.print_info()
        print("Expected Total: " + str(check_cost))

        # Validate test.
        assert check_cost == EasyMunk.last_total_cost
