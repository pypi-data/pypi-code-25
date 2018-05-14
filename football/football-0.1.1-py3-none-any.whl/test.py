from football import Football
import json
import os

football = Football(os.environ["FOOTBALL_API_KEY"])

print(json.dumps(football.competition_fixtures(445)))
