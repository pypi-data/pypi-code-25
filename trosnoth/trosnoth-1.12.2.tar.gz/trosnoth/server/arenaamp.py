from twisted.protocols import amp


class AlreadyCalled(Exception):
    '''
    Some commands should only be called once.
    '''


class NotYetListening(Exception):
    '''
    This command cannot be called before calling ArenaListening.
    '''


class ArenaListening(amp.Command):
    '''
    Arena -> Auth

    Indicates that the arena process is ready to accept clients.
    '''

    arguments = [
        ('token', amp.String()),
    ]
    response = []
    errors = {
        AlreadyCalled: 'NOT_ALLOWED'
    }


class RegisterAuthTag(amp.Command):
    '''
    Auth -> Arena

    Registers the given auth token with an authorised user.
    '''

    arguments = [
        ('username', amp.String()),
        ('authTag', amp.Integer()),
    ]
    response = []


class SetArenaInfo(amp.Command):
    '''
    Arena -> Auth

    Gives info about the arena, to be displayed in the web interface.
    '''

    arguments = [
        ('status', amp.String(optional=True)),
        ('players', amp.Integer(optional=True)),
        ('paused', amp.Boolean(optional=True)),
    ]


class PauseGame(amp.Command):
    '''
    Auth -> Arena

    Request that the game be paused.
    '''
    arguments = []
    response = []


class ResumeGame(amp.Command):
    '''
    Auth -> Arena

    Request that the game be paused.
    '''
    arguments = []
    response = []


class ResetToLobby(amp.Command):
    '''
    Auth -> Arena

    Request that the game be returned to the lobby.
    '''
    arguments = []
    response = []


class SetTeamAbility(amp.Command):
    '''
    Auth -> Arena

    Request that the given team ability be set.
    '''
    arguments = [
        ('teamIndex', amp.Integer()),
        ('ability', amp.String()),
        ('valueJSON', amp.String()),
    ]