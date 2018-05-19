'''
Author: Daniel Dowsett 05/2018
'''
import mpmath
from . import numbertokenizer
from . import localutil
from . import audio
import os

# def set_max_num_digits(num_decimal_places):
#     mpmath.mp.dps = num_decimal_places


class Equation():
    """
    Abstraction for an equation holding a lhs, rhs, an operation
    and an answer. The lhs and rhs can be arbitrarily long
    depending on mpmath settings. 

    You can set max_digits at any time, which will affect the output of
    everything but not the internal data itself.
    """

    #allowed operations map
    ops = { '+': lambda x,y: x + y,
            '-': lambda x,y: x - y,
            '/': lambda x,y: x / y,
            '*': lambda x,y: x * y,
            '**': lambda x,y: x ** y,
    } 


    def __init__(self, lhs, op, rhs, max_digits, ms_pause, ans_max_dec):
        if not localutil.is_number(lhs) or not localutil.is_number(rhs) or not op in Equation.ops.keys():
            raise ValueError("Invalid arguments for Equation initialisation")
        self.max_digits = max_digits
        #multiple of 500 rounded down, minimum of 500
        self.ms_pause = (int(ms_pause / 500) or 1) * 500
        self.ans_max_dec = ans_max_dec 
        with mpmath.workdps(self.max_digits):
            self.lhs = mpmath.mpf(lhs)
            self.op = op
            self.rhs = mpmath.mpf(rhs)
            

    def _get_answer(self):
        """
        The answer is created on demand so it plays well with changing max_digits
        """
        try:
            answer = Equation.ops[self.op](self.lhs, self.rhs)
            return localutil.round_to_num_decimals(answer, self.ans_max_dec)
        except:
            return 'undefined'
        
 

    ##### JSON Representation #####
    def to_dict(self):
        """
        returns a simple dicitonary that describes the equation
        """
        ret = {
                'lhs':self.lhs_as_string(),
                'op':self.op_as_string(),
                'rhs':self.rhs_as_string(),
                'answer':self.answer_as_string(),
        }
        return ret
    ################################

    ##### String Representation #####
    def mpf_to_trimmed_string(self, f):
        """Trims trailing zeros and decimal from f which is 
        of type mpmath.mpf. 
        """
        #all mpf have decimal points so it's okay to strip 0s
        return str(f).rstrip('0').rstrip('.')
    def lhs_as_string(self):
        with mpmath.workdps(self.max_digits):
            return self.mpf_to_trimmed_string(self.lhs)
    def op_as_string(self):
            return self.op
    def rhs_as_string(self):
        with mpmath.workdps(self.max_digits): 
            return self.mpf_to_trimmed_string(self.rhs)
    def question_as_string(self):
        return ' '.join((self.lhs_as_string(), self.op, self.rhs_as_string()))
    def answer_as_string(self):
        with mpmath.workdps(self.max_digits):
            return self.mpf_to_trimmed_string(self._get_answer())
    def full_as_string(self):
        return " ".join((self.question_as_string(), "=", self.answer_as_string()))
    ################################


    ##### Token Representation #####
    def lhs_as_tokens(self):
        with mpmath.workdps(self.max_digits):
            return numbertokenizer.to_tokens(self.lhs)
    def op_as_tokens(self):
        return self.op
    def rhs_as_tokens(self):
        with mpmath.workdps(self.max_digits):
            return numbertokenizer.to_tokens(self.rhs)
    def question_as_tokens(self):
        t = self.lhs_as_tokens()
        t.append(self.op)
        t.extend(self.rhs_as_tokens())
        return t
    def answer_as_tokens(self):
        with mpmath.workdps(self.max_digits):
            return numbertokenizer.to_tokens(self._get_answer()) 
    def full_as_tokens(self):
        t = self.question_as_tokens()
        t.append('=')
        t.extend(self.answer_as_tokens())
        return t
    #################################


    ##### Audio FileNames Representation #####
    def lhs_as_audio_filenames(self):
        return audio.tokens_to_audio(self.lhs_as_tokens())
    def op_as_audio_filenames(self):
        return audio.tokens_to_audio(self.op_as_tokens())
    def rhs_as_audio_filenames(self):
        return audio.tokens_to_audio(self.rhs_as_tokens())
    def question_as_audio_filenames(self):
        return audio.tokens_to_audio(self.question_as_tokens())
    def answer_as_audio_filenames(self):
        return audio.tokens_to_audio(self.answer_as_tokens())
    def full_as_audio_filenames(self, tempdir):
        """
        specify tempdir where all the silence files will be
        pooled in
        """
        ret = self.question_as_audio_filenames()
        ret.append(audio.audio_segments['='])
        ret.append(self.get_pause_filename(tempdir))
        ret.extend(self.answer_as_audio_filenames())
        return ret
    #################################

    def get_pause_filename(self, tempdir):
        """
        Returns the filename that is unique per silence length.
        """
        return os.path.join(tempdir, str(self.ms_pause) + "ms_silence.mp3")






