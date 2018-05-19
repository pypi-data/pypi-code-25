'''
Author: Daniel Dowsett 05/2018
'''
import mpmath

#we want to sync place_names with audio if we're working with it.
#otherwise we can go as high as we want text-wise
try:
    import audio
    place_names = audio.place_names
except ImportError:
    place_names = ('hundred', 'thousand', 'million', 'billion', 'trillion', 'somethings')





def to_tokens(number, include_commas=False, include_ands=True):
    """
    Takes an arbitrary number and returns a list of tokens
    that describe the number in english words. Each digit is described by either:
            .single -> e.g. "zero"   "one"        "three"
            .teens  -> e.g. "ten"   "eleven"    "thirteen"
            .tens   -> e.g.  n/a      n/a        "thirty"

    Example input : '-102132123234.14323'
    Example output: ['negative', '1.single', 'hundred', 'and', '2.single', 'billion', '1.single', 
                     'hundred', 'and', '3.tens', '2.single', 'million', '1.single', 'hundred', 
                     'and', '2.tens', '3.single', 'thousand', '2.single', 'hundred', 'and', '3.tens', 
                     '4.single', 'decimal', '1.single', '4.single', '3.single', '2.single', '3.single']

    number          -> anything that can be made into an mpmath.mpf
    include_commas  -> if True, will include commas where appropriate
    include_ands    -> if True, will include "and"s where appropriate

    """
    if number == 'undefined':
        return ['undefined']

    number = mpmath.mpf(number)
    token_list = list()

    #add negative token if necessary
    if number < 0:
        token_list.append('negative')

    #split into two camps for separate processing. 
    before_decimal, after_decimal = str(number).lstrip('-').split('.')
    
    #add before decimal
    token_list.extend(tokenize_integer(before_decimal, include_commas, include_ands))

    #add after token if there are any
    if len(after_decimal) > 0 and not all(x == '0' for x in after_decimal):
        token_list.append('decimal')
        token_list.extend([str(x) + ".single" for x in after_decimal])
    return token_list



def split_by_n_with_right_priority(s, n, padding=None):
    """
    Takes a string and divides it up into chunks of size n.
    The division is from the right, meaning '1234' with n=3 -> ['1', '234'].
    If a padding is provided, it wil be used to round out the last chunk 
    (for example, if padding = '0', '1234' -> ['001', '234'])
    """
    out = []
    while len(s):
        chunk = s[-n:]
        if not padding == None:
            while len(chunk) < n:
                chunk = padding + chunk
        out.insert(0, chunk)
        s = s[:-n]
    return out



def tokenize_integer(number, include_commas, include_ands):
    """
    Takes an integer (arbitrary length if string) and returns a list of tokens
    that describe the number in english words. Each digit is described by either:
            .single -> e.g. "zero"   "one"        "three"
            .teens  -> e.g. "ten"   "eleven"    "thirteen"
            .tens   -> e.g.  n/a      n/a        "thirty"

    Example input : '102132123230'
    Example output: ['1.single', 'hundred', 'and', '2.single', 'billion', '1.single', 
                     'hundred', 'and', '3.tens', '2.single', 'million', '1.single', 'hundred', 
                     'and', '2.tens', '3.single', 'thousand', '2.single', 'hundred', 'and', '3.tens']

    number          -> anything that can be stringified into digits- preferably a string of digits
    include_commas  -> if True, will include commas where appropriate
    include_ands    -> if True, will include "and"s where appropriate

    """
    number = str(number)
    ret = list()
    # after this we have eg 12345 as ['012', '345']
    chunks = split_by_n_with_right_priority(number, 3, padding='0')
    
    only_one_chunk = len(chunks) == 1
    last_chunk_number = len(chunks) - 1
    for chunk_number, chunk in enumerate(chunks):
        #handle '000'
        if all(digit == '0' for digit in chunk):
            #i.e. the number was 0
            if only_one_chunk:
                return ['0.single']
            #i.e. ignore this triplet (e.g. 40,000,353 -> we ignore the 000 when we say it)
            else:
                continue
        
        #no (globa) hundreds value -> we need an "and" between thousands and tens/ones
        if chunk[0] == '0' and chunk_number == last_chunk_number and not only_one_chunk and include_ands:
            ret.append('and')
        #otherwise unless this is the highest chunk, add a separator before the chunk tokenisations
        elif not chunk_number == 0 and include_commas:
            ret.append(',')

        #handle (local) hundreds place (i.e. highest vlaue in triplet)
        if not chunk[0] == '0':
            ret.append(chunk[0] + '.single')
            ret.append('hundred')
            #add "and" if there's something in this chunk to come after it
            if not chunk[2] == '0' or not chunk[1] == '0' and include_ands:
                ret.append('and')

        #add the tens if not x0x and not x1x
        if not chunk[1] == '0' and not chunk[1] == '1':
            ret.append(chunk[1] + '.tens')
        #for x1x, add the teens (e.g. sixteen)
        if chunk[1] == '1':
            ret.append(chunk[2] + '.teens')
        #if we didnt add a teen and there's a ones place, add it
        elif not chunk[2] == '0':
            ret.append(chunk[2] + '.single')


        #add modifier  ("thousand", "million", etc.) if not in last chunk (you don't say "3 thousand 732 hundred")
        if not chunk_number == last_chunk_number:
            place = last_chunk_number - chunk_number
            if place < len(place_names):
                ret.append(place_names[place])
            else:
                ret.append(place_names[-1])

    return ret               



# print(tokenize_integer(102132123230, include_commas=False, include_ands=True))
# print(number_to_token_list('-13234.1432'))
# print(number_to_token_list(mpmath.mpf('-102132123234.14323')))
# print(number_to_token_list('-102132123234.14322'))
# print(number_to_token_list('1232'))
# print(number_to_token_list('-0.2'))
# print(number_to_token_list('0'))
# print(number_to_token_list('10000300'))
# print(number_to_token_list('3002'))