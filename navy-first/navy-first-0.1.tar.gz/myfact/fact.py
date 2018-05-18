"myfact module"

def factorial(num):
    """
    return number
    """
    if num >=0:
        if num==0:
            return 1
        return num * factorial(num -1)
    else:
        return -1

