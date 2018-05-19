'''
Author: Daniel Dowsett 05/2018
'''
import argparse
from . import equationtemplate
import re
import os
import mpmath


template_reg = r'^(?P<num_eqs>\d+)#(?P<lhs_min>-?\d+)\((?P<lhs_dec>\d+)\)(?P<lhs_max>-?\d+){(?P<ops>[-+*/]+)}(?P<rhs_min>-?\d+)\((?P<rhs_dec>\d+)\)(?P<rhs_max>-?\d+)\?(?P<pause>\d+)\((?P<ans_dec>\d+)\)$'

def generate_run_info(argv):
    """
    Translates command line arguments into a run_info object containing
    all the necessary information to run the app
    """
    run_info = generate_arg_parser().parse_args(argv[1:])
    #de-list all the damned values
    run_info.output_json = run_info.output_json[0]
    run_info.output_mp3 = run_info.output_mp3[0]
    run_info.max_digits = run_info.max_digits[0]
    run_info.buffer_size = run_info.buffer_size[0]
    run_info.temp_dir = run_info.temp_dir[0]
    run_info.verbosity = run_info.verbosity[0]
    run_info.ms_pause = run_info.ms_pause[0]
    run_info.equation_templates = run_info.equation_templates
    return run_info

def generate_arg_parser():
        """
        Returns the parser to use to parse
        the comman dline arguments
        """
        class StoreEquationTemplate(argparse.Action):
            """
            Custom class for action of argparse argument. Stores a full equation template
            in self.dest if the template-template was valid
            """
            
            #template_reg = r'^(?P<num_eqs>.*)'
            def __call__(self, parser, namespace, values, option_string=None):
                #has to match argument exactly
                equation_templates = list()
                for template_template in values:
                    matches = re.compile(template_reg).fullmatch(template_template)
                    if matches:
                        #create new equation template
                        equation_template = equationtemplate.EquationTemplate(
                            num_eqs = int(matches.group('num_eqs')),
                            lhs_min = mpmath.mpf(matches.group('lhs_min')),
                            lhs_max_dec = int(matches.group('lhs_dec')),  
                            lhs_max = mpmath.mpf(matches.group('lhs_max')), 
                            ops = str(matches.group('ops')),
                            rhs_min = mpmath.mpf(matches.group('rhs_min')),
                            rhs_max_dec = int(matches.group('rhs_dec')),  
                            rhs_max = mpmath.mpf(matches.group('rhs_max')),
                            ms_pause = int(matches.group('pause')),
                            ans_max_dec = int(matches.group('ans_dec'))
                        )
                        if equation_template.valid:
                            equation_templates.append(equation_template)
                        else:
                            raise argparse.ArgumentError(self, equation_template.problem_message)
                    
                    else:
                        raise argparse.ArgumentError(self, "Invalid equation template")
                setattr(namespace, self.dest, equation_templates)

        #custom type for positive int
        def positive_int(string):
            value = int(string)
            if value <= 0:
                raise argparse.ArgumentTypeError('Value has to be a positive integer')
            return value

        #custom type for writeable file
        def filename(string):
            try:
                #brute force validity check
                with open(string, 'w'):
                    pass
                os.remove(string)
            except:
                raise argparse.ArgumentTypeError('Unable to create writeable file')
            return string

        parser = argparse.ArgumentParser(description="Create an mp3 to practice arithmetic on the go")
        parser.epilog = "If you get an error whilst wanting a lot of precision, try raising the precision (-d argument)"
        parser.add_argument('-j', '--json', nargs=1, action='store', dest='output_json', default=[None], type=filename,
                            help="Specify a file to which the equation data will be written in JSON format")
        parser.add_argument('-o', '--output', nargs=1, action='store', dest='output_mp3', default=["mathtraq.mp3"], type=filename,
                            help="MP3 file output (default: %(default)s)")
        parser.add_argument('-d', '--digits', nargs=1, action='store', dest='max_digits', default=[600],
                            help="Maximum digits (precision) (default: %(default)s)", type=positive_int)
        buffer_help = "Mathtraq works by concatenating a number of small files. This argument specifies how many to join at a time."
        parser.add_argument('-b', '--buffer_size', nargs=1, action='store', dest='buffer_size', type=positive_int, default=[600],
                            help=buffer_help + " (default: %(default)s)")
        parser.add_argument('-v', '--verbosity', nargs=1, action='store', dest='verbosity', default=[1], type=int, choices=[0,1,2,3],
                            help="0 is no output and 3 is a lot (default: %(default)s)")
        parser.add_argument('-t', '--temp_dir', nargs=1, action='store', dest='temp_dir', default=["temp"],
                            help= "relative path to temporary folder (useful if multiple instances running at once- default: %(default)s)")
        parser.add_argument('-z', '--forget_mp3', action='store_true', dest='forget_mp3',
                            help="use with -j to only output the json")
        parser.add_argument('-f', '--flush_output', action='store_true', dest='flush_output',
                            help="include to immediately flush the output stream")
        parser.add_argument('-p', '--ms_pause', nargs=1, action='store', dest='ms_pause', default=[500], type=positive_int,
                            metavar='pause_between_questions',
                            help="Milliseconds to pause after each question. Rounds down to nearest 500, minimum 500 (default: %(default)s)")
        template_help = "Example: 10#0(1)1000{+/-}-50(2)60?3000(2) will create 10 questions where the lhs is between 0 and 1000 with"
        template_help += " maximum 1 decimal place and the rhs is between -50 and 60 with a maximum of 2 decimal places."
        template_help += " They will be a mix of addition, division and subtraction, and a 3000ms pause will occur before the"
        template_help += " answer is given. The answer will be rounded to 2 decimal places. Note that one * in the ops is"
        template_help += " multiplcation. Two * means 'to the power of' and three means both multiplication and powers"
        parser.add_argument('equation_templates', action=StoreEquationTemplate, nargs='+', help=template_help, metavar='template')

        return parser