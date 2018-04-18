import os
import sys
import yaml
import logging
import jsonschema
from .exceptions import SportsNotFoundError
from glob import glob
from colorlog import ColoredFormatter

# Logging
LOG_LEVEL = logging.DEBUG
LOGFORMAT = ("  %(log_color)s%(levelname)-8s%(reset)s |"
             " %(log_color)s%(message)s%(reset)s")
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)
log.addHandler(stream)
# logging.basicConfig(level=logging.DEBUG)


class BookieSports(dict):
    """ This class allows to read the data provided by bookiesports

        On instantiation of this class the following procedure happens
        internally:

            1. Open the directory that stores the sports
            2. Load all Sports
            3. For each sport, load the corresponding data subset (event groups, events, rules, participants, etc.)
            4. Validate each data subset
            5. Perform consistency checks
            6. Instantiate a dictionary (``self``)

        As a result, the following call will return a dictionary with all the
        bookiesports:

        .. code-block:: python

            from bookiesports import BookieSports
            x = BookieSports()

        It is possible to overload a custom sports_folder by providing it to
        ``BookieSports`` as parameter.
    """

    #: Singelton to store data and prevent rereading if Lookup is
    #: instantiated multiple times
    data = dict()

    #: Folder where the data is actually stored
    sports_folder = None

    #: Schema for validation of the data
    schema = None

    def __init__(
        self,
        sports_folder=None,
        *args,
        **kwargs
    ):
        """ Let's load all the data from the folder and its subfolders
        """
        self._cwd = os.path.dirname(os.path.realpath(__file__))
        # self._cwd = os.getcwd()

        if BookieSports.sports_folder is None:
            if not sports_folder:
                # Load bundled sports
                BookieSports.sports_folder = os.path.join(
                    self._cwd,
                    "bookiesports")
            else:
                # Load custom sports
                BookieSports.sports_folder = sports_folder
        elif sports_folder and sports_folder != BookieSports.sports_folder:
            # clear .data
            BookieSports._clear()
            BookieSports.sports_folder = sports_folder

        # Load schemata
        if not BookieSports.schema:
            BookieSports.schema = self._loadschema()

        # Do not reload sports if already stored in data
        if not BookieSports.data:
            if not os.path.isdir(BookieSports.sports_folder):
                # Reset the sports_folder (since it is a singelton)
                BookieSports.sports_folder = None
                raise SportsNotFoundError(
                    "You need to obtain bookiesports, first! ({})".format(
                        BookieSports.sports_folder)
                )

            # Load sports
            dict.__init__(
                self,
                self._loadSports(BookieSports.sports_folder)
            )

            # _tests
            self._tests()

    @staticmethod
    def _clear():
        """ Clear data
        """
        BookieSports.data = dict()
        BookieSports.sports_folder = None

    def _loadyaml(self, f):
        """ Load a YAML file

            :param str f: YAML File location
        """
        try:
            with open(f, encoding="utf-8") as fid:
                t = yaml.load(fid)
            return t
        except yaml.YAMLError as exc:
            log.error("Error in configuration file {}: {}".format(f, exc))
            sys.exit(1)
        except Exception:
            log.error("The file {} is required but doesn't exist!".format(f))
            sys.exit(1)

    def _loadschema(self):
        """ Load the validation schema
        """
        dirname = os.path.join(self._cwd, "schema")

        defs = self._loadyaml(os.path.join(dirname, "definitions.yaml"))
        sport = self._loadyaml(os.path.join(dirname, "sport.yaml"))
        eventgroup = self._loadyaml(os.path.join(dirname, "eventgroup.yaml"))
        bettingmarketgroup = self._loadyaml(
            os.path.join(dirname, "bettingmarketgroup.yaml"))
        participant = self._loadyaml(os.path.join(dirname, "participant.yaml"))
        rule = self._loadyaml(os.path.join(dirname, "rule.yaml"))

        sport.update(defs)
        eventgroup.update(defs)
        bettingmarketgroup.update(defs)
        participant.update(defs)
        rule.update(defs)

        return dict(
            defs=defs,
            sport=sport,
            eventgroup=eventgroup,
            bettingmarketgroup=bettingmarketgroup,
            participant=participant,
            rule=rule
        )

    def _loadSports(self, sports_folder):
        """ This loads all sports recursively from the ``sports/`` folder
        """
        ret = dict()
        for sportDir in glob(
            os.path.join(
                self._cwd,
                sports_folder,
                "*")):
            if not os.path.isdir(sportDir):
                continue
            sportname = os.path.basename(sportDir)
            sport = self._loadSport(sportDir)
            ret[sportname] = sport
        return ret

    def _loadSport(self, sportDir):
        """ Load an individual sport, recursively
        """
        sport = self._loadyaml(os.path.join(sportDir, "index.yaml"))

        # Validate
        jsonschema.validate(sport, self.schema["sport"])

        # Load Eventgroups
        eventgroups = dict()
        for eventgroupname in sport["eventgroups"]:
            eventgroupDir = os.path.join(sportDir, eventgroupname)
            eventgroup = self._loadyaml(
                os.path.join(eventgroupDir, "index.yaml"))

            # Validate
            jsonschema.validate(eventgroup, self.schema["eventgroup"])

            # Store in structure
            eventgroups[eventgroupname] = eventgroup
            eventgroups[eventgroupname]["sport_id"] = sport.get("id")
        sport["eventgroups"] = eventgroups

        # Rules
        rulesDir = os.path.join(sportDir, "rules")
        rules = dict()
        for ruleDir in glob(os.path.join(rulesDir, "*")):
            if ".yaml" not in ruleDir:
                continue
            rulename = os.path.basename(ruleDir).replace(".yaml", "")
            rule = self._loadyaml(ruleDir)

            # Validate
            jsonschema.validate(rule, self.schema["rule"])

            rules[rulename] = rule
        sport["rules"] = rules

        # participants
        participantsDir = os.path.join(sportDir, "participants")
        participants = dict()
        for participantDir in glob(os.path.join(participantsDir, "*")):
            if ".yaml" not in participantDir:
                continue
            participant_name = os.path.basename(
                participantDir).replace(".yaml", "")
            participant = self._loadyaml(participantDir)

            # Validate
            jsonschema.validate(participant, self.schema["participant"])

            participants[participant_name] = participant
        sport["participants"] = participants

        # def_bmgs
        def_bmgsDir = os.path.join(sportDir, "bettingmarketgroups")
        def_bmgs = dict()
        for def_bmgDir in glob(os.path.join(def_bmgsDir, "*")):
            if ".yaml" not in def_bmgDir:
                continue
            def_bmg_name = os.path.basename(def_bmgDir).replace(".yaml", "")
            bmg = self._loadyaml(def_bmgDir)

            # Validate
            jsonschema.validate(bmg, self.schema["bettingmarketgroup"])

            # Validate
            jsonschema.validate(participant, self.schema["participant"])
            def_bmgs[def_bmg_name] = bmg

        sport["bettingmarketgroups"] = def_bmgs

        return sport

    def _tests(self):
        """ Tests for consistencies and requirements
        """
        for sportname, sport in self.items():

            for evengroupname, eventgroup in sport["eventgroups"].items():

                for bmg in eventgroup["bettingmarketgroups"]:
                    # Test that each used BMG is deinfed
                    assert bmg in sport["bettingmarketgroups"], (
                        "Betting market group {} is used"
                        "in {}:{} but wasn't defined!"
                    ).format(
                        bmg, sportname, evengroupname
                    )
            for rule in sport["rules"]:
                pass
            for bmgname, bmg in sport["bettingmarketgroups"].items():

                # Test that each used rule is defined
                assert bmg["rules"] in sport["rules"], \
                    "Rule {} is used in {}:{} but wasn't defined!".format(
                        bmg["rules"],
                        sportname,
                        bmgname)
