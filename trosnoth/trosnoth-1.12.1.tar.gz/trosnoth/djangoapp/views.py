# coding: utf-8
from __future__ import division

import json
import logging

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.http import JsonResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from trosnoth.const import POINT_VALUES
from trosnoth.gamerecording.achievementlist import availableAchievements
from trosnoth.model.upgrades import upgradeOfType
from trosnoth.server import arenaamp

from .models import (
    TrosnothServerSettings, TrosnothUser, GameRecord, PlayerKills,
    UpgradesUsedInGameRecord, TrosnothArena,
)

log = logging.getLogger(__name__)


@ensure_csrf_cookie
def index(request):
    from twisted.internet import reactor, threads
    from trosnoth.web.server import WebServer
    server = WebServer.instance
    initialJS = threads.blockingCallFromThread(
        reactor, server.getInitialEvents)

    context = {
        'settings': TrosnothServerSettings.get(),
        'arenas': TrosnothArena.objects.all(),
        'initialJS': initialJS,
    }
    return render(request, 'trosnoth/index.html', context)


@ensure_csrf_cookie
def arena(request, arenaId):
    arenaId = int(arenaId)
    try:
        arenaRecord = TrosnothArena.objects.get(id=arenaId)
    except TrosnothArena.DoesNotExist:
        raise Http404('Arena not found')

    context = {
        'settings': TrosnothServerSettings.get(),
        'arena': arenaRecord,
        'arenaInfo': json.dumps(getArenaInfo(arenaId)),
    }
    return render(request, 'trosnoth/arena.html', context)


def userProfile(request, userId, nick=None):
    try:
        user = TrosnothUser.fromUser(pk=userId)
    except User.DoesNotExist:
        raise Http404('User not found')

    unlocked = []
    locked = []
    for a in user.achievementprogress_set.all():
        try:
            name, description = availableAchievements.getAchievementDetails(
                a.achievementId)
        except KeyError:
            if not a.unlocked:
                continue
            name = a.achievementId
            description = (
                'This achievement does not exist in this version of Trosnoth')

        if finders.find(
                'trosnoth/achievements/{}.png'.format(a.achievementId)):
            imageId = a.achievementId
        else:
            imageId = 'default'

        info = {
            'name': name,
            'description': description,
            'imageId': imageId,
        }
        if a.unlocked:
            unlocked.append(info)
        else:
            locked.append(info)
    unlocked.sort(key=lambda a: a['name'])
    locked.sort(key=lambda a: a['name'])

    context = {
        'settings': TrosnothServerSettings.get(),
        'trosnothUser': user,
        'unlocked': unlocked,
        'locked': locked,
    }
    return render(request, 'trosnoth/user.html', context)


def userList(request):
    context = {
        'settings': TrosnothServerSettings.get(),
        'users': TrosnothUser.objects.order_by('-lastSeen'),
    }
    return render(request, 'trosnoth/userlist.html', context)


def viewGame(request, gameId):
    game = GameRecord.objects.get(pk=gameId)

    data = []

    for player in game.gameplayer_set.all():
        entry = {
            'player': player,
            'nick': player.user.nick if player.user else player.botName,
            'accuracy': (100.0 * player.shotsHit / player.shotsFired
                ) if player.shotsFired else 0.,
            'score': 0,
            'kdr': u'{:2.2f}'.format(player.kills / player.deaths
                ) if player.deaths else u'∞',
            'adr': u'{:2.2f}'.format(player.timeAlive / player.timeDead
                ) if player.timeDead else u'∞',
        }

        for stat, weighting in POINT_VALUES.items():
            if stat in entry:
                value = entry[stat]
            else:
                value = getattr(player, stat)
            entry['score'] += value * weighting

        data.append(entry)

    data.sort(key=(lambda entry: entry['score']), reverse=True)

    i = 1
    j = 0
    for entry in data:
        entry['index'] = j
        if entry['player'].bot:
            entry['rank'] = 'B'
        else:
            entry['rank'] = str(i)
            i += 1
        j += 1

    killData = {}
    for pkr in PlayerKills.objects.filter(killee__game=game):
        killData[pkr.killer, pkr.killee] = pkr.count

    killTable = []
    for killerEntry in data:
        killer = killerEntry['player']
        killRow = []
        maxKillCount = maxDeathCount = 0
        maxKill = maxDeath = '-'
        for killeeEntry in data:
            killee = killeeEntry['player']
            count = killData.get((killer, killee), 0)
            killRow.append(count)
            if count > maxKillCount:
                maxKillCount = count
                maxKill = '{} ({})'.format(killeeEntry['nick'], count)
            dieCount = killData.get((killee, killer), 0)
            if dieCount > maxDeathCount:
                maxDeathCount = dieCount
                maxDeath = '{} ({})'.format(killeeEntry['nick'], dieCount)
        killerEntry['maxKill'] = maxKill
        killerEntry['maxDeath'] = maxDeath

        killTable.append({
            'player': killerEntry['player'],
            'nick': killerEntry['nick'],
            'entries': killRow,
        })

    for i in range(len(killTable)):
        killTable[i]['entries'][i] = '-'

    otherKills = [
        killData.get((None, killeeEntry['player']), 0)
        for killeeEntry in data
    ]

    upgradeData = {}
    upgradeCodes = set()
    for ur in UpgradesUsedInGameRecord.objects.filter(gamePlayer__game=game):
        upgradeData[ur.gamePlayer, ur.upgrade] = ur.count
        upgradeCodes.add(ur.upgrade)

    if upgradeCodes:
        nameAndCode = []
        for code in upgradeCodes:
            if code in upgradeOfType:
                name = upgradeOfType[code].name
            else:
                name = '?{}?'.format(code)
            nameAndCode.append((name, code))

        nameAndCode.sort()
        upgradeList = [name for name, code in nameAndCode]
        upgradeTable = []
        for entry in data:
            entries = []
            maxUpgrade = '-'
            maxUpgradeCount = 0
            for name, code in nameAndCode:
                count = upgradeData.get((entry['player'], code), 0)
                entries.append(count)
                if count > maxUpgradeCount:
                    maxUpgrade = '{} ({})'.format(name, count)
                    maxUpgradeCount = count

            entry['maxUpgrade'] = maxUpgrade

            upgradeTable.append({
                'player': entry['player'],
                'nick': entry['nick'],
                'entries': entries,
            })
    else:
        upgradeList = []
        upgradeTable = []

    context = {
        'settings': TrosnothServerSettings.get(),
        'game': game,
        'playerData': data,
        'killTable': killTable,
        'otherKills': otherKills if any(otherKills) else None,
        'upgrades': upgradeList,
        'upgradeTable': upgradeTable,
    }
    return render(request, 'trosnoth/viewgame.html', context)


def gameList(request):
    context = {
        'settings': TrosnothServerSettings.get(),
        'games': GameRecord.objects.order_by('-started'),
    }
    return render(request, 'trosnoth/gamelist.html', context)


@permission_required('trosnoth.pause_arena')
def pauseArena(request):
    arenaId = int(request.GET['id'])
    sendArenaRequest(arenaId, arenaamp.PauseGame)
    return JsonResponse(getArenaInfo(arenaId))


@permission_required('trosnoth.pause_arena')
def resumeArena(request):
    arenaId = int(request.GET['id'])
    sendArenaRequest(arenaId, arenaamp.ResumeGame)
    return JsonResponse(getArenaInfo(arenaId))


@permission_required('trosnoth.restart_arena')
def restartArena(request):
    arenaId = int(request.GET['id'])

    from twisted.internet import reactor, threads
    from trosnoth.run.authserver import AuthenticationFactory
    authFactory = AuthenticationFactory.instance
    threads.blockingCallFromThread(reactor, authFactory.shutDownArena, arenaId)

    return JsonResponse(getArenaInfo(arenaId))


@permission_required('trosnoth.set_arena_level')
def resetArena(request):
    arenaId = int(request.GET['id'])
    sendArenaRequest(arenaId, arenaamp.ResetToLobby)
    return JsonResponse(getArenaInfo(arenaId))


@permission_required('trosnoth.enable_arena')
def disableArena(request):
    arenaId = int(request.GET['id'])

    try:
        arenaRecord = TrosnothArena.objects.get(id=arenaId)
    except TrosnothArena.DoesNotExist:
        return HttpResponseBadRequest('Arena not found')

    arenaRecord.enabled = False
    arenaRecord.save()

    from twisted.internet import reactor, threads
    from trosnoth.run.authserver import AuthenticationFactory
    authFactory = AuthenticationFactory.instance
    try:
        threads.blockingCallFromThread(
            reactor, authFactory.shutDownArena, arenaId)
    except Exception:
        log.exception('Error trying to shut down arena')

    return JsonResponse(getArenaInfo(arenaId))


@permission_required('trosnoth.enable_arena')
def enableArena(request):
    arenaId = int(request.GET['id'])

    try:
        arenaRecord = TrosnothArena.objects.get(id=arenaId)
    except TrosnothArena.DoesNotExist:
        return HttpResponseBadRequest('Arena not found')

    arenaRecord.enabled = True
    arenaRecord.save()

    return JsonResponse(getArenaInfo(arenaId))


@permission_required('trosnoth.change_team_abilities')
def disableShots(request):
    arenaId = int(request.GET['id'])
    teamIndex = int(request.GET['t'])
    setTeamAbility(arenaId, teamIndex, 'aggression', False)
    return JsonResponse(getArenaInfo(arenaId))


@permission_required('trosnoth.change_team_abilities')
def enableShots(request):
    arenaId = int(request.GET['id'])
    teamIndex = int(request.GET['t'])
    setTeamAbility(arenaId, teamIndex, 'aggression', True)
    return JsonResponse(getArenaInfo(arenaId))


@permission_required('trosnoth.change_team_abilities')
def disableCaps(request):
    arenaId = int(request.GET['id'])
    teamIndex = int(request.GET['t'])
    setTeamAbility(arenaId, teamIndex, 'zoneCaps', False)
    return JsonResponse(getArenaInfo(arenaId))


@permission_required('trosnoth.change_team_abilities')
def enableCaps(request):
    arenaId = int(request.GET['id'])
    teamIndex = int(request.GET['t'])
    setTeamAbility(arenaId, teamIndex, 'zoneCaps', True)
    return JsonResponse(getArenaInfo(arenaId))


def sendArenaRequest(arenaId, command, **kwargs):
    '''
    Connects to the running authentication server and asks it to communicate
    with the given arena server.
    '''
    from twisted.internet import reactor, threads
    from trosnoth.run.authserver import AuthenticationFactory
    authFactory = AuthenticationFactory.instance
    return threads.blockingCallFromThread(
        reactor, authFactory.sendArenaRequest, arenaId, command, **kwargs)


def getArenaInfo(arenaId):
    from twisted.internet import reactor, threads
    from trosnoth.run.authserver import AuthenticationFactory
    authFactory = AuthenticationFactory.instance
    return threads.blockingCallFromThread(
        reactor, authFactory.getArenaInfo, arenaId)


def setTeamAbility(arenaId, teamIndex, ability, value):
    from twisted.internet import reactor, threads
    from trosnoth.run.authserver import AuthenticationFactory
    authFactory = AuthenticationFactory.instance
    arenaProxy = threads.blockingCallFromThread(
        reactor, authFactory.getArena, arenaId)
    threads.blockingCallFromThread(
        reactor, arenaProxy.setTeamAbility, teamIndex, ability, value)
