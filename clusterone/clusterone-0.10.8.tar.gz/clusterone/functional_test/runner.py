import logging
from sys import exit


def run(scenario_cls):
    """
    Performs initializing, running and cleaning up after a scenario
    """

    scenario = scenario_cls()

    try:
        scenario.run()
        logging.info("SUCCESS!")
        exit(0)
    except AssertionError:
        logging.exception("TESTS FAILED AT:")
        exit(1)
    except Exception:
        logging.exception("TESTS FAILED DUE TO TEST CODE MALFUNCTION:")
        exit(2)
    finally:
        logging.info("cleaning...")
        scenario.clean()
        logging.info("cleaning done, exiting")
