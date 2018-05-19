from pathlib import Path
import pandas as pd
import pytest

DATA_DIR = Path(__file__).parent.parent / 'data'

TEST_DIR = Path(__file__).parent
SAMPLES_DIR = TEST_DIR / 'samples'


# Add cmdline arguments
def pytest_addoption(parser):
    parser.addoption("--regenerate-samples", action="store", default=False,
                     help="Ask to regenerate samples")
    parser.addoption("--generate-samples", action="store", default=False,
                     help="Ask to generate samples for non existing ones only.")

class Recoder():
    def __init__(self, config):
        regenerate = config.getoption("--regenerate-samples")
        generate = config.getoption("--generate-samples")
        if regenerate and generate:
            raise ValueError("You set both regenerate-samples and generate-samples "
                             "to True. You should choose only one of them")

        if not (regenerate and generate):
            mode = "test"
        elif regenerate:
            mode = "regenerate"
        elif generate:
            mode = "generate"

        self.mode = mode


@pytest.fixture
def dataset():
    df = pd.read_csv(DATA_DIR / 'hurricanes.csv')
    return df
