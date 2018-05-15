import pyconrad.autoinit
import pytest
import os


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", reason="Skipping this test on Travis CI.")
def test_start_gui():
    pyconrad.start_gui()


if __name__ == "__main__":
    test_start_gui()
