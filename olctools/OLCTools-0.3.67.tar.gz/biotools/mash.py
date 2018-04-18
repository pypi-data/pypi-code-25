from biotools import accessoryfunctions

# Tools to use to run mash, and probably also parse its output.


class MashResult:
    def __init__(self, mash_result_row):
        x = mash_result_row.split()
        self.reference = x[0]
        self.query = x[1]
        self.distance = float(x[2])
        self.pvalue = float(x[3])
        self.matching_hash = x[4]


class ScreenResult:
    def __init__(self, screen_result_row):
        x = screen_result_row.split()
        self.identity = float(x[0])
        self.shared_hashes = x[1]
        self.median_multiplicity = x[2]
        self.pvalue = float(x[3])
        self.query_id = x[4]


def kwargs_to_string(kwargs):
    """
    Given a set of kwargs, turns them into a string which can then be passed to a command.
    :param kwargs: kwargs from a function call.
    :return: outstr: A string, which is '' if no kwargs were given, and the kwargs in string format otherwise.
    """
    outstr = ''
    for arg in kwargs:
        outstr += ' -{} {}'.format(arg, kwargs[arg])
    return outstr


def sketch(*args, output_sketch='sketch.msh', threads=1, returncmd=False, **kwargs):
    """
    Wrapper for mash sketch.
    :param args: Files you want to sketch. Any number can be passed in, file patterns (i.e. *fasta) can be used.
    :param output_sketch: Output file for your sketch. Default sketch.msh.
    :param threads: Number of threads to run analysis on.
    :param kwargs: Other arguments, in parameter='argument' format. If parameter is just a switch, do parameter=''
    :param returncmd: If true, will return the command used to call mash as well as out and err.
    :return: stdout and stderr from mash sketch
    """
    options = kwargs_to_string(kwargs)
    if len(args) == 0:
        raise ValueError('At least one file to sketch must be specified. You specified 0 files.')
    cmd = 'mash sketch '
    for arg in args:
        cmd += arg + ' '
    cmd += '-o {} -p {} {}'.format(output_sketch, str(threads), options)
    out, err = accessoryfunctions.run_subprocess(cmd)
    if returncmd:
        return out, err, cmd
    else:
        return out, err


def dist(*args, output_file='distances.tab', threads=1, returncmd=False, **kwargs):
    """
    Wrapper for mash dist.
    :param args: Files you want to find distances between. Can be
    :param output_file: Output file to write your distances to. Default distances.tab
    :param threads: Number of threads to run mash on.
    :param kwargs: Other arguments, in parameter='argument' format. If parameter is just a switch, do parameter=''
    :param returncmd: If true, will return the command used to call mash as well as out and err.
    :return: stdout and stderr from mash dist
    """
    options = kwargs_to_string(kwargs)
    if len(args) == 0:
        raise ValueError('At least one file to sketch must be specified. You specified 0 files.')
    cmd = 'mash dist '
    for arg in args:
        cmd += arg + ' '
    cmd += ' -p {} {} > {}'.format(str(threads), options, output_file)
    out, err = accessoryfunctions.run_subprocess(cmd)
    if returncmd:
        return out, err, cmd
    else:
        return out, err


def screen(*args, output_file='screen.tab', threads=1, returncmd=False, **kwargs):
    """
    Wrapper for mash screen. Requires mash v2.0 or higher.
    :param args: Files you want to screen. First argument must be a sketch.
    :param output_file: Output to write containment info to.
    :param threads: Number of threads to run mash on.
    :param returncmd: If set to true, function will return the cmd string passed to subprocess as a third value.
    :param kwargs: Other arguments, in parameter='argument' format. If parameter is just a switch, do parameter=''
    :return: stdout and stderr from mash screen
    """
    options = kwargs_to_string(kwargs)
    cmd = 'mash screen '
    for arg in args:
        cmd += arg + ' '
    cmd += ' -p {} {} | sort -gr > {}'.format(str(threads), options, output_file)
    out, err = accessoryfunctions.run_subprocess(cmd)
    if returncmd:
        return out, err, cmd
    else:
        return out, err


def read_mash_output(result_file):
    """
    :param result_file: Tab-delimited result file generated by mash dist.
    :return: mash_results: A list with each entry in the result file as an entry, with attributes reference, query,
    distance, pvalue, and matching_hash
    """
    with open(result_file) as handle:
        lines = handle.readlines()
    mash_results = list()
    for line in lines:
        result = MashResult(line)
        mash_results.append(result)
    return mash_results


def read_mash_screen(screen_result):
    """
    :param screen_result: Tab-delimited result file generated by mash screen.
    :return: results: A list with each line in the result file as an entry, with attributes identity, shared_hashes,
    median_multiplicity, pvalue, and query_id
    """
    with open(screen_result) as handle:
        lines = handle.readlines()
    results = list()
    for line in lines:
        result = ScreenResult(line)
        results.append(result)
    return results
