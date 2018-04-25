import biopipe.contexts


def test_no_output():
    with biopipe.contexts.no_output():
        print('No output!')
