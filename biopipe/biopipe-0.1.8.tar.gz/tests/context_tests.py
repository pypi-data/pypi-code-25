import biopipe.contexts


def no_output_test():
    with biopipe.contexts.no_output():
        print('No output!')
