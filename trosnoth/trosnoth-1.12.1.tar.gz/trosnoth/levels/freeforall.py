# coding=utf-8
from twisted.internet import defer

from trosnoth.const import ACHIEVEMENT_TACTICAL, BOT_GOAL_KILL_THINGS
from trosnoth.levels.base import Level, playLevel
from trosnoth.messages import AwardPlayerCoinMsg, SetPlayerTeamMsg
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID
from trosnoth.triggers.coins import SlowlyIncrementLivePlayerCoinsTrigger
from trosnoth.triggers.deathmatch import (
    PlayerKillScoreTrigger, makeCirclesLayout, AddOneBotTrigger,
)

BONUS_COINS_FOR_WINNER = 500


class FreeForAllLevel(Level):
    allowAutoTeams = False
    levelName = 'Free for All'

    def __init__(self, duration=None):
        super(FreeForAllLevel, self).__init__()
        if duration is None:
            duration = 6 * 60
        self.duration = duration

    def getTeamToJoin(self, preferredTeam, user, bot):
        return None

    def setupMap(self):
        self.world.setLayout(makeCirclesLayout(self.world.layoutDatabase))

    @defer.inlineCallbacks
    def start(self):
        try:
            for player in self.world.players:
                if not player.bot:
                    self.world.sendServerCommand(
                        SetPlayerTeamMsg(player.id, NEUTRAL_TEAM_ID))

            SlowlyIncrementLivePlayerCoinsTrigger(self).activate()
            PlayerKillScoreTrigger(self, dieScore=-0.5).activate()
            AddOneBotTrigger(self).activate()
            self.world.setActiveAchievementCategories({ACHIEVEMENT_TACTICAL})
            self.setUserInfo('Free for All', (
                '* Kill as many other players as you can',
                '* You gain 1 point per kill',
                u'* You lose ½ point if you are killed',
            ), BOT_GOAL_KILL_THINGS)
            self.world.abilities.set(zoneCaps=False, balanceTeams=False)
            self.world.uiOptions.set(teamIdsHumansCanJoin=[NEUTRAL_TEAM_ID])
            if self.duration:
                self.world.clock.startCountDown(self.duration)
            else:
                self.world.clock.stop()
            self.world.clock.propagateToClients()

            yield self.world.clock.onZero.wait()

            # Game over!
            playerScores = self.world.scoreboard.playerScores
            maxScore = max(playerScores.values())
            winners = [
                p for p, score in playerScores.items()
                if score == maxScore]

            self.playSound('game-over-whistle.ogg')
            for winner in winners:
                self.notifyAll('{} wins'.format(winner.nick))
                self.world.sendServerCommand(
                    AwardPlayerCoinMsg(winner.id, BONUS_COINS_FOR_WINNER))
        finally:
            self.endLevel()


if __name__ == '__main__':
    playLevel(FreeForAllLevel(duration=180), aiCount=0)
