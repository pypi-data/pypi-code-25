import random
import string


DEFAULT_TOKEN_SAMPLE = string.ascii_letters + string.digits


def generate_random_string(length=16, sample=DEFAULT_TOKEN_SAMPLE):
    lst = [random.choice(sample) for _ in range(length)]
    return ''.join(lst)
