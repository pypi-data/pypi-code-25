from twisted.internet import defer

from trosnoth.const import ACHIEVEMENT_TACTICAL, BOT_GOAL_KILL_THINGS
from trosnoth.levels.base import Level, playLevel
from trosnoth.messages import AwardPlayerCoinMsg, SetPlayerTeamMsg
from trosnoth.triggers.base import Trigger
from trosnoth.triggers.coins import SlowlyIncrementLivePlayerCoinsTrigger
from trosnoth.triggers.deathmatch import (
    makeCirclesLayout, AddLimitedBotsTrigger, PlayerLifeScoreTrigger,
    PlayerKillScoreTrigger,
)


MIN_HUNTERS = 4
MAX_HUNTERS = 12
BONUS_COINS_FOR_WINNER = 500


class HuntedLevel(Level):
    allowAutoTeams = False
    levelName = 'Hunted'

    def __init__(self, duration=None):
        super(HuntedLevel, self).__init__()
        if duration is None:
            duration = 6 * 60
        self.duration = duration
        self.blueTeam = self.redTeam = None

    def getTeamToJoin(self, preferredTeam, user, bot):
        return self.redTeam

    def setupMap(self):
        self.blueTeam = self.world.teams[0]
        self.redTeam = self.world.teams[1]
        self.world.setLayout(makeCirclesLayout(self.world.layoutDatabase))

    @defer.inlineCallbacks
    def start(self):
        try:
            self.setTeamName(self.blueTeam, 'Hunters')
            self.setTeamName(self.redTeam, 'Hunted')
            self.redTeam.abilities.set(aggression=False)

            for player in self.world.players:
                if not player.bot:
                    self.world.sendServerCommand(
                        SetPlayerTeamMsg(player.id, self.redTeam.id))

            SlowlyIncrementLivePlayerCoinsTrigger(self).activate()
            scoreTrigger = PlayerLifeScoreTrigger(
                self, teams={self.redTeam}).activate()
            PlayerKillScoreTrigger(self, dieScore=0).activate()
            botTrigger = AddLimitedBotsTrigger(
                self, MIN_HUNTERS, MAX_HUNTERS,
                'terminator', 'Terminator', self.blueTeam).activate()
            self.world.setActiveAchievementCategories({ACHIEVEMENT_TACTICAL})
            self.setUserInfo('Hunted', (
                '* Die as few times as possible',
                '* Players score points for every second they are alive',
            ), BOT_GOAL_KILL_THINGS)
            self.world.abilities.set(zoneCaps=False, balanceTeams=False)
            self.world.uiOptions.set(teamIdsHumansCanJoin=['B'])
            if self.duration:
                self.world.clock.startCountDown(self.duration)
            else:
                self.world.clock.stop()
            self.world.clock.propagateToClients()

            yield self.world.clock.onZero.wait()

            # Game over!
            scoreTrigger.deactivate()
            botTrigger.deactivate()
            playerScores = self.world.scoreboard.playerScores
            maxScore = max(playerScores.values())
            winners = [
                p for p, score in playerScores.items()
                if score == maxScore and p.team == self.redTeam]

            self.playSound('game-over-whistle.ogg')
            for winner in winners:
                self.notifyAll('{} wins'.format(winner.nick))
                self.world.sendServerCommand(
                    AwardPlayerCoinMsg(winner.id, BONUS_COINS_FOR_WINNER))

            yield self.world.sleep(3)
        finally:
            self.redTeam.abilities.set(aggression=True)
            self.endLevel()


class RespawnOnJoinTrigger(Trigger):
    def doActivate(self):
        self.world.onPlayerAdded.addListener(self.gotPlayerAdded)
        for player in self.world.players:
            self.gotPlayerAdded(player)

    def doDeactivate(self):
        self.world.onPlayerAdded.removeListener(self.gotPlayerAdded)

    def gotPlayerAdded(self, player, *args, **kwargs):
        if player.team == self.level.blueTeam:
            mapLayout = self.world.map.layout
            self.world.magicallyMovePlayer(
                player, (mapLayout.centreX, mapLayout.centreY), alive=True)


if __name__ == '__main__':
    playLevel(HuntedLevel(duration=180), aiCount=1)
