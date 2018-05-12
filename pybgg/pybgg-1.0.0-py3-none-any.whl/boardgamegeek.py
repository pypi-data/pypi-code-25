import requests
import xml.etree.ElementTree

ElementTree = xml.etree.ElementTree
bggApiBaseURL = "https://www.boardgamegeek.com/xmlapi2/"
class boardGameGeek:
    # the string you pass in is the search query. Will return the first result's game info
    def GetGameInfo(self, game='', ID=0):
        if ID == 0:
            ID = self._GetGameId(game)
        gameInfo = self._GetGameInfoFromId(ID)
        return gameInfo

    # a "smart" search for the game's info. Not very smart
    def SearchForGameInfo(self, game=""):
        ID = self._SearchForGameId(game)
        gameInfo = self._GetGameInfoFromId(ID)
        return gameInfo

    def _GetGameId(self, game="", searchtype='boardgame'):
        # Query the BGG API
        response = requests.get(bggApiBaseURL + 'search?type=' + searchtype + '&query=' + game)

        # Create an XML Tree from the response
        tree = ElementTree.fromstring(response.content)

        # Assume the game is the first response
        game = tree[0] # assume the first result is the game we are looking for
        return game.get('id')

    # This function searches for the game name passed in and if found, returns the firs matching game id
    def _SearchForGameId(self, game="", searchtype='boardgame'):
        # Use only the first 2 words as our search term. BGG search is not very smart, so we try to give it less information
        search_list = game.split()[:2]
        search_string = ''
        for word in search_list:
            search_string += word
            search_string += '+'
        # Remove the trailing +
        search_string = search_string[:-1]

        # Query the BGG API
        response = requests.get(bggApiBaseURL + 'search?type=' + searchtype + '&query=' + search_string)

        # Create an XML Tree from the response
        tree = ElementTree.fromstring(response.content)
        
        # Assume the most recent game in the list is the one which we are looking for
        most_recent = 0 # id not found
        max_year = 0
        for game in tree.findall('item'):
            year = 1
            try:
                year = game.find('yearpublished').get('value')
            except:
                year = 1
            if int(year) > int(max_year):
                max_year = year
                most_recent = game.get('id')
        print(most_recent)
        return most_recent

    # Returns a dictionary of information about a game, given its ID
    def _GetGameInfoFromId(self, gameId=0):
        if gameId == 0:
            return
        response = requests.get(bggApiBaseURL + 'thing?id=' + str(gameId))
        tree = ElementTree.fromstring(response.content)
        game = None
        try:
            game = tree[0]
        except:
            print("_GetGameInfoFromId " + str(gameId) + " Id Not found")

        if game is None:
            return
        game_info = {}

        # Store the values in a dictionary
        try:
            game_info['name'] = game.find('name').get('value')
        except:
            game_info['name'] = ''

        try:
            game_info['play_time'] = game.find('playingtime').get('value')
        except:
            game_info['play_time'] = ''

        try:
            game_info['min_age'] = game.find('minage').get('value')
        except:
            game_info['min_age'] = ''
        
        try:
            game_info['year_published'] = game.find('yearpublished').get('value')
        except:
            game_info['year_published'] = ''

        # Build an array of game_categories
        game_categories = []
        for cat in game.iter('link'):
            if cat.get('type') != "boardgamecategory":
                continue
            game_categories.append(cat.get('value'))
            
        game_info['Themes'] = game_categories

        # Build an array of Game Mechanics
        game_mechanics = []
        for cat in game.iter('link'):
            if cat.get('type') != "boardgamemechanic":
                continue
            game_mechanics.append(cat.get('value'))
        game_info['Mechanics'] = game_mechanics

        # Get the designer, artist and publisher
        for cat in game.iter('link'):
            if cat.get('type') == "boardgamedesigner":
                game_info['designer'] = cat.get('value')
            if cat.get('type') == "boardgameartist":
                game_info['artist'] = cat.get('value')
            if cat.get('type') == "boardgamepublisher":
                game_info['publisher'] = cat.get('value')

        return game_info
