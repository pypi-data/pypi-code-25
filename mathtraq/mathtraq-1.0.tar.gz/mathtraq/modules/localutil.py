'''
Author: Daniel Dowsett 05/2018
'''
import mpmath
import os
import uuid

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False  


def round_to_num_decimals(value, num_decimals):
    """
    Returns mpf float rounded to max of num_decimals decimal places
    """
    #ensure we have enough after the decimal
    temp = str(value) + ('0' * num_decimals) + '0'
    pos_of_dec = temp.find('.')
    index_of_eventual_last = pos_of_dec + num_decimals
    #if num_decimals == 0
    if temp[index_of_eventual_last] == '.':
        index_of_eventual_last -= 1
    decider =  temp[pos_of_dec + num_decimals + 1]
    eventual_last = int(temp[index_of_eventual_last])
    if decider >= '5':
        eventual_last += 1
    temp = temp[:index_of_eventual_last] + str(eventual_last)
    return mpmath.mpf(temp)


def get_random(minimum, maximum, max_decimal_places):
        """
        Returns a random mpmath.mpf between [minimum, maximum)
        with, at most, max_decimal_places digits after the decimal point.
        Note: would-be integers have .0 attached in mpf land
        """
        #get a random number between [minimum, maximum)
        if max_decimal_places == 0:
            num = maximum - mpmath.rand() * (maximum-minimum + 1)
        else:
            num = maximum - mpmath.rand() * (maximum-minimum)
        #scale it up
        num *= mpmath.power(10, max_decimal_places)
        #cut off it's tail
        temp = str(num).split('.')[0]
        num = mpmath.mpf(temp)
        #scale it back down
        num *= mpmath.power(10, -max_decimal_places)
        return num


def is_positive_int_compatible(val):
        """
        True if val can be converted to int which would 
        be posisitve
        """
        try:
            i = int(val)
            return i > 0
        except ValueError:
            return False


def is_positive_float_compatible(val):
    try:
        f = float(val)
        return f > 0
    except:
        return False


def remove_file_if_exists(filename):
    """
    Remove file if it exists
    """
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass

def create_dir_if_absent(dirname):
    """
    create folder if it doesn't exist
    """
    try:
        os.makedirs(dirname)
    except FileExistsError :
        pass


def get_unique_filenames(dir, attempts_before_error, extensions):
    """
    Returns a list of filenames with the given extensions that don't exist in
    the given dir. Each filename will have the same stub prepended to their extension. 
    Extensions to be given without the '.'. The first element in the list is the stub itself
    """
    for i in range(0, attempts_before_error):
        filename_stub = uuid.uuid4().hex
        possible_filenames = [os.path.join(dir, filename_stub + '.' + ext) for ext in extensions]
        unique = True
        for f in possible_filenames:
            if os.path.isfile(f):
                break
        ret = [filename_stub]
        ret.extend(possible_filenames)
        return ret
    raise IOError("Unable to create unique file")