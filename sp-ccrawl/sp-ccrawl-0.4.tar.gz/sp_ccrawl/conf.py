""" Configuration for the project """

from configparser import ConfigParser, ExtendedInterpolation


def to_bool(var):
    var_lc = var.lower()
    valid_true = {'true', 'yes', 'y', '1'}
    valid_false = {'false', 'no', 'n', '0'}
    if var_lc not in valid_true and var_lc not in valid_false:
        raise ValueError("bool value must be one of '{}' or '{}'".format(valid_true, valid_false))
    return var_lc in valid_true


class _Section:
    SECTION = 'undefined'
    PARAM = {}

    def __init__(self):
        for prm in self.PARAM.keys():
            super(_Section, self).__setattr__(prm, None)
        self._final = False

    def __setattr__(self, key, value):
        if '_final' in self.__dict__ and self._final:
            raise Conf.ConfError("Could not set attribute '{}' to '{}' in the finalized class '{}'"
                                 .format(key, value, self.__class__.__name__))
        super().__setattr__(key, value)

class _Download(_Section):
    SECTION = 'download'
    PARAM = {'s3_bucket': None, 's3_prefix': None, 's3_week_re': None, 'date_from': None,
             'date_to': None, 'output_fold': None, 'rewrite': to_bool, 'summ_file': None,
             'log_level': None}

    def __init__(self):
        super().__init__()


class _Process(_Section):
    SECTION = 'process'
    PARAM = {'input': None, 'parq_table': None, 'time_step': None,
             'num_in_partitions': int, 'num_out_partitions': int,
             'local_temp_dir': None, 'log_level': None, 'load_from_s3': to_bool,
             'rewrite': to_bool, 's3_prefix': None}

    def __init__(self):
        super().__init__()


class Conf(_Section):
    class ConfError(Exception):
        def __init__(self, msg):
            err = "Config error: {}".format(msg)
            super().__init__(msg)

    def __init__(self):
        super().__init__()
        self.download = _Download()
        self.process = _Process()
        self._final = False

    def __check_section_keys(self, parser, section_elem):
        """
        Check that section in configuration file has exactly required keys
        :param parser: ConfigParser object
        :param section_elem: self.download | self.process
        raise exception if keys are different
        """
        pkeys = set(parser.options(section_elem.SECTION))
        if pkeys != set(section_elem.PARAM.keys()):
            raise Conf.ConfError("Section '{}' must include parameters {}. Found {}. Difference: {}"
                                .format(section_elem.SECTION, section_elem.PARAM.keys(), pkeys,
                                        pkeys ^ section_elem.PARAM.keys()))

    def __set_prm(self, parser, section_elem):
        """
        Set parameters from a configuration file.
        :param parser: ConfigParser object
        :param section_elem: self.download | self.process
        """
        for key in parser.options(section_elem.SECTION):
            try:
                val = parser.get(section_elem.SECTION, key)
                conv = section_elem.PARAM[key]
                if conv is not None:
                    val = conv(val)
                section_elem.__setattr__(key, val)
            except Exception as err:
                raise ValueError("Section '{}', key '{}'. Error: {}"
                                 .format(section_elem.SECTION, key, err))

    def read(self, fname):
        """ Read data from config file """
        parser = ConfigParser(interpolation=ExtendedInterpolation())
        parser.read(fname)
        req_sections = set([_Download.SECTION, _Process.SECTION])
        if set(parser.sections()) != req_sections:
            raise Conf.ConfError("Required section: {}".format(req_sections))
        for section in (self.download, self.process):
            self.__check_section_keys(parser, section)
            self.__set_prm(parser, section)
        # finalize
        return self

    def finalize(self):
        for section in (self.download, self.process):
            section._final = True
        self._final = True


if __name__ == '__main__':
    cnf = Conf()
    cnf.read('proj.conf').finalize()
    print("Download:")
    print(cnf.download.date_from)
    # print(cnf.download.src_base)
    print(cnf.download.date_from)
    print(cnf.download.date_to)
    print(cnf.download.output_fold)
    print(cnf.download.rewrite)

    print("\nProcess:")
    print(cnf.process.parq_table)
    print(cnf.process.time_step)
    print(cnf.process.num_in_partitions)
    print(cnf.process.num_out_partitions)
    print(cnf.process.local_tmp_dir)
    print(cnf.process.log_level)

    print("\nSet element:")
    try:
        cnf.process.time_step = 'check'
    except Exception as err:
        print("Could not set attribute:", err)
    finally:
        print(cnf.process.time_step)
    print("Done")
