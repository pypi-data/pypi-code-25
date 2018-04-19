import logging

from trosnoth.levels.base import playLevel
from trosnoth.levels.standard import StandardRandomLevel
from trosnoth.triggers.coins import AwardStartingCoinsTrigger

log = logging.getLogger(__name__)


class TestingLevel(StandardRandomLevel):

#    allowAutoBalance = False

    def pregameCountdownPhase(self, **kwargs):
        AwardStartingCoinsTrigger(self, coins=10000).activate()


if __name__ == '__main__':
    playLevel(TestingLevel(halfMapWidth=3, mapHeight=2), aiCount=0)