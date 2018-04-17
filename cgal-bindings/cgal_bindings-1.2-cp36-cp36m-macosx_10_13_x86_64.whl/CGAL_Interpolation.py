# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_CGAL_Interpolation')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_CGAL_Interpolation')
    _CGAL_Interpolation = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_CGAL_Interpolation', [dirname(__file__)])
        except ImportError:
            import _CGAL_Interpolation
            return _CGAL_Interpolation
        try:
            _mod = imp.load_module('_CGAL_Interpolation', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _CGAL_Interpolation = swig_import_helper()
    del swig_import_helper
else:
    import _CGAL_Interpolation
del _swig_python_version_info

try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError("'%s' object has no attribute '%s'" % (class_type.__name__, name))


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except __builtin__.Exception:
    class _object:
        pass
    _newclass = 0

import CGAL.CGAL_Triangulation_2
import CGAL.CGAL_Kernel
import CGAL.CGAL_Triangulation_3
class Double_and_bool(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Double_and_bool, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Double_and_bool, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _CGAL_Interpolation.new_Double_and_bool(*args)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this
    __swig_setmethods__["first"] = _CGAL_Interpolation.Double_and_bool_first_set
    __swig_getmethods__["first"] = _CGAL_Interpolation.Double_and_bool_first_get
    if _newclass:
        first = _swig_property(_CGAL_Interpolation.Double_and_bool_first_get, _CGAL_Interpolation.Double_and_bool_first_set)
    __swig_setmethods__["second"] = _CGAL_Interpolation.Double_and_bool_second_set
    __swig_getmethods__["second"] = _CGAL_Interpolation.Double_and_bool_second_get
    if _newclass:
        second = _swig_property(_CGAL_Interpolation.Double_and_bool_second_get, _CGAL_Interpolation.Double_and_bool_second_set)
    def __len__(self):
        return 2
    def __repr__(self):
        return str((self.first, self.second))
    def __getitem__(self, index): 
        if not (index % 2):
            return self.first
        else:
            return self.second
    def __setitem__(self, index, val):
        if not (index % 2):
            self.first = val
        else:
            self.second = val
    __swig_destroy__ = _CGAL_Interpolation.delete_Double_and_bool
    __del__ = lambda self: None
Double_and_bool_swigregister = _CGAL_Interpolation.Double_and_bool_swigregister
Double_and_bool_swigregister(Double_and_bool)

class Double_bool_bool(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Double_bool_bool, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Double_bool_bool, name)
    __repr__ = _swig_repr
    __swig_setmethods__["first"] = _CGAL_Interpolation.Double_bool_bool_first_set
    __swig_getmethods__["first"] = _CGAL_Interpolation.Double_bool_bool_first_get
    if _newclass:
        first = _swig_property(_CGAL_Interpolation.Double_bool_bool_first_get, _CGAL_Interpolation.Double_bool_bool_first_set)
    __swig_setmethods__["second"] = _CGAL_Interpolation.Double_bool_bool_second_set
    __swig_getmethods__["second"] = _CGAL_Interpolation.Double_bool_bool_second_get
    if _newclass:
        second = _swig_property(_CGAL_Interpolation.Double_bool_bool_second_get, _CGAL_Interpolation.Double_bool_bool_second_set)
    __swig_setmethods__["third"] = _CGAL_Interpolation.Double_bool_bool_third_set
    __swig_getmethods__["third"] = _CGAL_Interpolation.Double_bool_bool_third_get
    if _newclass:
        third = _swig_property(_CGAL_Interpolation.Double_bool_bool_third_get, _CGAL_Interpolation.Double_bool_bool_third_set)

    def __init__(self, *args):
        this = _CGAL_Interpolation.new_Double_bool_bool(*args)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def deepcopy(self, *args):
        return _CGAL_Interpolation.Double_bool_bool_deepcopy(self, *args)
    __swig_destroy__ = _CGAL_Interpolation.delete_Double_bool_bool
    __del__ = lambda self: None
Double_bool_bool_swigregister = _CGAL_Interpolation.Double_bool_bool_swigregister
Double_bool_bool_swigregister(Double_bool_bool)

class Point_2_and_double(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Point_2_and_double, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Point_2_and_double, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _CGAL_Interpolation.new_Point_2_and_double(*args)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this
    __swig_setmethods__["first"] = _CGAL_Interpolation.Point_2_and_double_first_set
    __swig_getmethods__["first"] = _CGAL_Interpolation.Point_2_and_double_first_get
    if _newclass:
        first = _swig_property(_CGAL_Interpolation.Point_2_and_double_first_get, _CGAL_Interpolation.Point_2_and_double_first_set)
    __swig_setmethods__["second"] = _CGAL_Interpolation.Point_2_and_double_second_set
    __swig_getmethods__["second"] = _CGAL_Interpolation.Point_2_and_double_second_get
    if _newclass:
        second = _swig_property(_CGAL_Interpolation.Point_2_and_double_second_get, _CGAL_Interpolation.Point_2_and_double_second_set)
    def __len__(self):
        return 2
    def __repr__(self):
        return str((self.first, self.second))
    def __getitem__(self, index): 
        if not (index % 2):
            return self.first
        else:
            return self.second
    def __setitem__(self, index, val):
        if not (index % 2):
            self.first = val
        else:
            self.second = val
    __swig_destroy__ = _CGAL_Interpolation.delete_Point_2_and_double
    __del__ = lambda self: None
Point_2_and_double_swigregister = _CGAL_Interpolation.Point_2_and_double_swigregister
Point_2_and_double_swigregister(Point_2_and_double)

class Weighted_point_2_and_double(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Weighted_point_2_and_double, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Weighted_point_2_and_double, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _CGAL_Interpolation.new_Weighted_point_2_and_double(*args)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this
    __swig_setmethods__["first"] = _CGAL_Interpolation.Weighted_point_2_and_double_first_set
    __swig_getmethods__["first"] = _CGAL_Interpolation.Weighted_point_2_and_double_first_get
    if _newclass:
        first = _swig_property(_CGAL_Interpolation.Weighted_point_2_and_double_first_get, _CGAL_Interpolation.Weighted_point_2_and_double_first_set)
    __swig_setmethods__["second"] = _CGAL_Interpolation.Weighted_point_2_and_double_second_set
    __swig_getmethods__["second"] = _CGAL_Interpolation.Weighted_point_2_and_double_second_get
    if _newclass:
        second = _swig_property(_CGAL_Interpolation.Weighted_point_2_and_double_second_get, _CGAL_Interpolation.Weighted_point_2_and_double_second_set)
    def __len__(self):
        return 2
    def __repr__(self):
        return str((self.first, self.second))
    def __getitem__(self, index): 
        if not (index % 2):
            return self.first
        else:
            return self.second
    def __setitem__(self, index, val):
        if not (index % 2):
            self.first = val
        else:
            self.second = val
    __swig_destroy__ = _CGAL_Interpolation.delete_Weighted_point_2_and_double
    __del__ = lambda self: None
Weighted_point_2_and_double_swigregister = _CGAL_Interpolation.Weighted_point_2_and_double_swigregister
Weighted_point_2_and_double_swigregister(Weighted_point_2_and_double)

class Point_3_and_double(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Point_3_and_double, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Point_3_and_double, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _CGAL_Interpolation.new_Point_3_and_double(*args)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this
    __swig_setmethods__["first"] = _CGAL_Interpolation.Point_3_and_double_first_set
    __swig_getmethods__["first"] = _CGAL_Interpolation.Point_3_and_double_first_get
    if _newclass:
        first = _swig_property(_CGAL_Interpolation.Point_3_and_double_first_get, _CGAL_Interpolation.Point_3_and_double_first_set)
    __swig_setmethods__["second"] = _CGAL_Interpolation.Point_3_and_double_second_set
    __swig_getmethods__["second"] = _CGAL_Interpolation.Point_3_and_double_second_get
    if _newclass:
        second = _swig_property(_CGAL_Interpolation.Point_3_and_double_second_get, _CGAL_Interpolation.Point_3_and_double_second_set)
    def __len__(self):
        return 2
    def __repr__(self):
        return str((self.first, self.second))
    def __getitem__(self, index): 
        if not (index % 2):
            return self.first
        else:
            return self.second
    def __setitem__(self, index, val):
        if not (index % 2):
            self.first = val
        else:
            self.second = val
    __swig_destroy__ = _CGAL_Interpolation.delete_Point_3_and_double
    __del__ = lambda self: None
Point_3_and_double_swigregister = _CGAL_Interpolation.Point_3_and_double_swigregister
Point_3_and_double_swigregister(Point_3_and_double)

class Data_access_double_2(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Data_access_double_2, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Data_access_double_2, name)
    __repr__ = _swig_repr

    def __init__(self):
        this = _CGAL_Interpolation.new_Data_access_double_2()
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def set(self, p, value):
        return _CGAL_Interpolation.Data_access_double_2_set(self, p, value)

    def get(self, p):
        return _CGAL_Interpolation.Data_access_double_2_get(self, p)
    __swig_destroy__ = _CGAL_Interpolation.delete_Data_access_double_2
    __del__ = lambda self: None
Data_access_double_2_swigregister = _CGAL_Interpolation.Data_access_double_2_swigregister
Data_access_double_2_swigregister(Data_access_double_2)

class Data_access_vector_2(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Data_access_vector_2, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Data_access_vector_2, name)
    __repr__ = _swig_repr

    def __init__(self):
        this = _CGAL_Interpolation.new_Data_access_vector_2()
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def set(self, p, value):
        return _CGAL_Interpolation.Data_access_vector_2_set(self, p, value)

    def get(self, p):
        return _CGAL_Interpolation.Data_access_vector_2_get(self, p)
    __swig_destroy__ = _CGAL_Interpolation.delete_Data_access_vector_2
    __del__ = lambda self: None
Data_access_vector_2_swigregister = _CGAL_Interpolation.Data_access_vector_2_swigregister
Data_access_vector_2_swigregister(Data_access_vector_2)


def natural_neighbor_coordinates_2(*args):
    return _CGAL_Interpolation.natural_neighbor_coordinates_2(*args)
natural_neighbor_coordinates_2 = _CGAL_Interpolation.natural_neighbor_coordinates_2

def regular_neighbor_coordinates_2(*args):
    return _CGAL_Interpolation.regular_neighbor_coordinates_2(*args)
regular_neighbor_coordinates_2 = _CGAL_Interpolation.regular_neighbor_coordinates_2

def surface_neighbors_certified_3(*args):
    return _CGAL_Interpolation.surface_neighbors_certified_3(*args)
surface_neighbors_certified_3 = _CGAL_Interpolation.surface_neighbors_certified_3

def surface_neighbors_3(*args):
    return _CGAL_Interpolation.surface_neighbors_3(*args)
surface_neighbors_3 = _CGAL_Interpolation.surface_neighbors_3

def surface_neighbor_coordinates_certified_3(*args):
    return _CGAL_Interpolation.surface_neighbor_coordinates_certified_3(*args)
surface_neighbor_coordinates_certified_3 = _CGAL_Interpolation.surface_neighbor_coordinates_certified_3

def surface_neighbor_coordinates_3(*args):
    return _CGAL_Interpolation.surface_neighbor_coordinates_3(*args)
surface_neighbor_coordinates_3 = _CGAL_Interpolation.surface_neighbor_coordinates_3

def linear_interpolation(range, norm, function_values):
    return _CGAL_Interpolation.linear_interpolation(range, norm, function_values)
linear_interpolation = _CGAL_Interpolation.linear_interpolation

def quadratic_interpolation(range, norm, p, function_values, gradients):
    return _CGAL_Interpolation.quadratic_interpolation(range, norm, p, function_values, gradients)
quadratic_interpolation = _CGAL_Interpolation.quadratic_interpolation

def sibson_c1_interpolation(range, norm, p, function_values, gradients):
    return _CGAL_Interpolation.sibson_c1_interpolation(range, norm, p, function_values, gradients)
sibson_c1_interpolation = _CGAL_Interpolation.sibson_c1_interpolation

def sibson_c1_interpolation_square(range, norm, p, function_values, gradients):
    return _CGAL_Interpolation.sibson_c1_interpolation_square(range, norm, p, function_values, gradients)
sibson_c1_interpolation_square = _CGAL_Interpolation.sibson_c1_interpolation_square

def farin_c1_interpolation(range, norm, p, function_values, gradients):
    return _CGAL_Interpolation.farin_c1_interpolation(range, norm, p, function_values, gradients)
farin_c1_interpolation = _CGAL_Interpolation.farin_c1_interpolation

def sibson_gradient_fitting(range, norm, p, function_values):
    return _CGAL_Interpolation.sibson_gradient_fitting(range, norm, p, function_values)
sibson_gradient_fitting = _CGAL_Interpolation.sibson_gradient_fitting

def sibson_gradient_fitting_nn_2(dt, gradients, function_values):
    return _CGAL_Interpolation.sibson_gradient_fitting_nn_2(dt, gradients, function_values)
sibson_gradient_fitting_nn_2 = _CGAL_Interpolation.sibson_gradient_fitting_nn_2

def sibson_gradient_fitting_rn_2(rt, gradients, function_values):
    return _CGAL_Interpolation.sibson_gradient_fitting_rn_2(rt, gradients, function_values)
sibson_gradient_fitting_rn_2 = _CGAL_Interpolation.sibson_gradient_fitting_rn_2
# This file is compatible with both classic and new-style classes.


