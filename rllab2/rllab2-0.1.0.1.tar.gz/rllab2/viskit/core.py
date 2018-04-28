from __future__ import with_statement
from __future__ import absolute_import
import csv
from rllab2.misc import ext
import os
import numpy as np
import base64
import pickle
import json
import itertools
# import ipywidgets
# import IPython.display
# import plotly.offline as po
# import plotly.graph_objs as go
import pdb
from io import open
from itertools import imap
from itertools import ifilter


def unique(l):
    return list(set(l))


def flatten(l):
    return [item for sublist in l for item in sublist]


def load_progress(progress_csv_path):
    print u"Reading %s" % progress_csv_path
    entries = dict()
    with open(progress_csv_path, u'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for k, v in row.items():
                if k not in entries:
                    entries[k] = []
                try:
                    entries[k].append(float(v))
                except:
                    entries[k].append(0.)
    entries = dict([(k, np.array(v)) for k, v in entries.items()])
    return entries


def to_json(stub_object):
    from rllab2.misc.instrument import StubObject
    from rllab2.misc.instrument import StubAttr
    if isinstance(stub_object, StubObject):
        assert len(stub_object.args) == 0
        data = dict()
        for k, v in stub_object.kwargs.items():
            data[k] = to_json(v)
        data[u"_name"] = stub_object.proxy_class.__module__ + \
                        u"." + stub_object.proxy_class.__name__
        return data
    elif isinstance(stub_object, StubAttr):
        return dict(
            obj=to_json(stub_object.obj),
            attr=to_json(stub_object.attr_name)
        )
    return stub_object


def flatten_dict(d):
    flat_params = dict()
    for k, v in d.items():
        if isinstance(v, dict):
            v = flatten_dict(v)
            for subk, subv in flatten_dict(v).items():
                flat_params[k + u"." + subk] = subv
        else:
            flat_params[k] = v
    return flat_params


def load_params(params_json_path):
    with open(params_json_path, u'r') as f:
        data = json.loads(f.read())
        if u"args_data" in data:
            del data[u"args_data"]
        if u"exp_name" not in data:
            data[u"exp_name"] = params_json_path.split(u"/")[-2]
    return data


def lookup(d, keys):
    if not isinstance(keys, list):
        keys = keys.split(u".")
    for k in keys:
        if hasattr(d, u"__getitem__"):
            if k in d:
                d = d[k]
            else:
                return None
        else:
            return None
    return d


def load_exps_data(exp_folder_paths,disable_variant=False):
    exps = []
    for exp_folder_path in exp_folder_paths:
        exps += [x[0] for x in os.walk(exp_folder_path)]
    exps_data = []
    for exp in exps:
        try:
            exp_path = exp
            params_json_path = os.path.join(exp_path, u"params.json")
            variant_json_path = os.path.join(exp_path, u"variant.json")
            progress_csv_path = os.path.join(exp_path, u"progress.csv")
            progress = load_progress(progress_csv_path)
            if disable_variant:
                params = load_params(params_json_path)
            else:
                try:
                    params = load_params(variant_json_path)
                except IOError:
                    params = load_params(params_json_path)
            exps_data.append(ext.AttrDict(
                progress=progress, params=params, flat_params=flatten_dict(params)))
        except IOError, e:
            print e
    return exps_data


def smart_repr(x):
    if isinstance(x, tuple):
        if len(x) == 0:
            return u"tuple()"
        elif len(x) == 1:
            return u"(%s,)" % smart_repr(x[0])
        else:
            return u"(" + u",".join(imap(smart_repr, x)) + u")"
    else:
        if hasattr(x, u"__call__"):
            return u"__import__('pydoc').locate('%s')" % (x.__module__ + u"." + x.__name__)
        else:
            return repr(x)


def extract_distinct_params(exps_data, excluded_params=(u'exp_name', u'seed', u'log_dir'), l=1):
    # all_pairs = unique(flatten([d.flat_params.items() for d in exps_data]))
    # if logger:
    #     logger("(Excluding {excluded})".format(excluded=', '.join(excluded_params)))
    # def cmp(x,y):
    #     if x < y:
    #         return -1
    #     elif x > y:
    #         return 1
    #     else:
    #         return 0

    try:
        stringified_pairs = sorted(
            imap(
                eval,
                unique(
                    flatten(
                        [
                            list(
                                imap(
                                    smart_repr,
                                    list(d.flat_params.items())
                                )
                            )
                            for d in exps_data
                        ]
                    )
                )
            ),
            key=lambda x: (
                tuple(0. if it is None else it for it in x),
            )
        )
    except Exception, e:
        print e
        import ipdb; ipdb.set_trace()
    proposals = [(k, [x[1] for x in v])
                 for k, v in itertools.groupby(stringified_pairs, lambda x: x[0])]
    filtered = [(k, v) for (k, v) in proposals if len(v) > l and all(
        [k.find(excluded_param) != 0 for excluded_param in excluded_params])]
    return filtered


class Selector(object):
    def __init__(self, exps_data, filters=None, custom_filters=None):
        self._exps_data = exps_data
        if filters is None:
            self._filters = tuple()
        else:
            self._filters = tuple(filters)
        if custom_filters is None:
            self._custom_filters = []
        else:
            self._custom_filters = custom_filters

    def where(self, k, v):
        return Selector(self._exps_data, self._filters + ((k, v),), self._custom_filters)

    def custom_filter(self, filter):
        return Selector(self._exps_data, self._filters, self._custom_filters + [filter])

    def _check_exp(self, exp):
        # or exp.flat_params.get(k, None) is None
        return all(
            ((unicode(exp.flat_params.get(k, None)) == unicode(v) or (k not in exp.flat_params)) for k, v in self._filters)
        ) and all(custom_filter(exp) for custom_filter in self._custom_filters)

    def extract(self):
        return list(ifilter(self._check_exp, self._exps_data))

    def iextract(self):
        return ifilter(self._check_exp, self._exps_data)


# Taken from plot.ly
color_defaults = [
    u'#1f77b4',  # muted blue
    u'#ff7f0e',  # safety orange
    u'#2ca02c',  # cooked asparagus green
    u'#d62728',  # brick red
    u'#9467bd',  # muted purple
    u'#8c564b',  # chestnut brown
    u'#e377c2',  # raspberry yogurt pink
    u'#7f7f7f',  # middle gray
    u'#bcbd22',  # curry yellow-green
    u'#17becf'  # blue-teal
]


def hex_to_rgb(hex, opacity=1.0):
    if hex[0] == u'#':
        hex = hex[1:]
    assert (len(hex) == 6)
    return u"rgba({0},{1},{2},{3})".format(int(hex[:2], 16), int(hex[2:4], 16), int(hex[4:6], 16), opacity)

# class VisApp(object):
#
#
#     def __init__(self, exp_folder_path):
#         self._logs = []
#         self._plot_sequence = []
#         self._exps_data = None
#         self._distinct_params = None
#         self._exp_filter = None
#         self._plottable_keys = None
#         self._plot_key = None
#         self._init_data(exp_folder_path)
#         self.redraw()
#
#     def _init_data(self, exp_folder_path):
#         self.log("Loading data...")
#         self._exps_data = load_exps_data(exp_folder_path)
#         self.log("Loaded {nexp} experiments".format(nexp=len(self._exps_data)))
#         self._distinct_params = extract_distinct_params(self._exps_data, logger=self.log)
#         assert len(self._distinct_params) == 1
#         self._exp_filter = self._distinct_params[0]
#         self.log("******************************************")
#         self.log("Found {nvary} varying parameter{plural}".format(nvary=len(self._distinct_params), plural="" if len(
#             self._distinct_params) == 1 else "s"))
#         for k, v in self._distinct_params:
#             self.log(k, ':', ", ".join(map(str, v)))
#         self.log("******************************************")
#         self._plottable_keys = self._exps_data[0].progress.keys()
#         assert len(self._plottable_keys) > 0
#         if 'AverageReturn' in self._plottable_keys:
#             self._plot_key = 'AverageReturn'
#         else:
#             self._plot_key = self._plottable_keys[0]
#
#     def log(self, *args, **kwargs):
#         self._logs.append((args, kwargs))
#
#     def _display_dropdown(self, attr_name, options):
#         def f(**kwargs):
#             self.__dict__[attr_name] = kwargs[attr_name]
#         IPython.display.display(ipywidgets.interactive(f, **{attr_name: options}))
#
#     def redraw(self):
#         # print out all the logs
#         for args, kwargs in self._logs:
#             print(*args, **kwargs)
#
#         self._display_dropdown("_plot_key", self._plottable_keys)
#
#         k, vs = self._exp_filter
#         selector = Selector(self._exps_data)
#         to_plot = []
#         for v in vs:
#             filtered_data = selector.where(k, v).extract()
#             returns = [exp.progress[self._plot_key] for exp in filtered_data]
#             sizes = map(len, returns)
#             max_size = max(sizes)
#             for exp, retlen in zip(filtered_data, sizes):
#                 if retlen < max_size:
#                     self.log("Excluding {exp_name} since the trajectory is shorter: {thislen} vs. {maxlen}".format(
#                         exp_name=exp.params["exp_name"], thislen=retlen, maxlen=max_size))
#             returns = [ret for ret in returns if len(ret) == max_size]
#             mean_returns = np.mean(returns, axis=0)
#             std_returns = np.std(returns, axis=0)
#             self._plot_sequence.append((''))
#             to_plot.append(ext.AttrDict(means=mean_returns, stds=std_returns, legend=str(v)))
#         make_plot(to_plot)
