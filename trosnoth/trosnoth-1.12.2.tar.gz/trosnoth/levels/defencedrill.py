from twisted.internet import defer

from trosnoth.const import BOT_GOAL_CAPTURE_MAP
from trosnoth.levels.base import playLevel
from trosnoth.levels.standard import StandardRandomLevel


class DefenceDrillLevel(StandardRandomLevel):
    @defer.inlineCallbacks
    def mainGamePhase(self):
        self.world.teams[1].abilities.set(zoneCaps=False)
        try:
            yield super(DefenceDrillLevel, self).mainGamePhase()
        finally:
            self.world.teams[1].abilities.set(zoneCaps=True)

    def setMainGameUserInfo(self):
        self.setUserInfo('Defence Drill', (
            '* Red players cannot capture zones',
            '* Try not to lose your zones',
        ), BOT_GOAL_CAPTURE_MAP)


if __name__ == '__main__':
    playLevel(DefenceDrillLevel(), aiCount=1)