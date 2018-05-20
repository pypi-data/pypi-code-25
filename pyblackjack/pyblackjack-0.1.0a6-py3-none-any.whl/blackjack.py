import random
import sys


class DealerBlackjack(BaseException):
    '''Non-local control flow for when the dealer has a blackjack.'''


ACTION_HIT = '[H]it'
ACTION_STAND = '[S]tand'
ACTION_SPLIT = 'S[p]lit'
ACTION_DOUBLE = '[D]ouble down'
ACTION_SURRENDER = 'S[u]rrender'


class Card(int):
    '''An individual playing card. Subclass of int for simplicity.'''

    def __new__(cls, rank, value):
        self = super().__new__(cls, value)
        self.rank = rank
        return self

    def __str__(self):
        return (str(self.rank))


CARDSET = [
    Card('A', 1),
    Card('2', 2),
    Card('3', 3),
    Card('4', 4),
    Card('5', 5),
    Card('6', 6),
    Card('7', 7),
    Card('8', 8),
    Card('9', 9),
    Card('10', 10),
    Card('J', 10),
    Card('Q', 10),
    Card('K', 10),
]

DECK = CARDSET * 4


class Shoe:
    def __init__(self, decks=6):
        self.numdecks = decks
        self.new()

    def deal(self):
        return self.cards.pop()

    def time_to_shuffle(self):
        return len(self.cards) <= self.cut

    def new(self):
        self.cards = DECK * self.numdecks
        random.shuffle(self.cards)
        if self.numdecks == 1:
            self.cut = len(self.cards) / 2
        else:
            self.cut = len(self.cards) / 4


class Hand:
    def __init__(self, shoe):
        self.cards = []
        self.shoe = shoe

    def hard_total(self):
        return sum(self.cards)

    def soft_total(self):
        total = self.hard_total()
        if total > 11 or 1 not in self.cards:
            return None
        return total + 10

    def total(self):
        return self.soft_total() or self.hard_total()

    def print_hand(self, downcard=False):
        cards = self.cards[:]
        if downcard:
            cards[0] = '[]'
        cardtext = ' '.join(str(card) for card in cards)
        if downcard:
            return cardtext
        else:
            return '{} ({})'.format(cardtext, self.total())

    def check_blackjack(self):
        return len(self.cards) == 2 and self.total() == 21

    def check_bust(self):
        return self.hard_total() > 21

    def hit(self):
        self.cards.append(self.shoe.deal())

    def reset(self):
        self.cards = []


class Dealer(Hand):
    def __init__(self, shoe, hit_soft_17=True):
        super().__init__(shoe)
        self.hard_stand = 17
        if hit_soft_17:
            self.soft_stand = 18
        else:
            self.soft_stand = 17

    def check_insurance(self):
        return self.cards[1] == 1

    def play_hand(self):
        while True:
            if ((self.soft_total() and self.soft_total() >= self.soft_stand) or
                    self.hard_total() >= self.hard_stand):
                break
            self.hit()


class Player(Hand):
    _id = 0

    def __init__(self, shoe, name=None, chips=1000):
        super().__init__(shoe)
        self.__class__._id += 1
        self.id = self.__class__._id
        if name is None:
            self.name = 'Player {}'.format(self.id)
        else:
            self.name = name
        self.chips = chips
        self.bet = 0
        self.split_hand = None
        self.insurance = False

    def check_bet(self):
        return self.chips >= self.bet

    def check_split(self):
        return (len(self.cards) == 2
                and self.cards[0].rank == self.cards[1].rank)

    def split(self):
        self.chips -= self.bet
        self.split_hand = Hand(self.shoe)
        self.split_hand.cards.append(self.cards.pop())
        self.hit()

    def check_double(self):
        return len(self.cards) == 2 and 9 <= self.total() <= 11

    def double_down(self):
        self.chips -= self.bet
        self.bet *= 2
        self.hit()

    def surrender(self):
        self.chips += self.bet // 2

    def buy_insurance(self):
        price = self.bet // 2
        self.chips -= price
        self.insurance = price

    def reset(self):
        super().reset()
        if self.split_hand:
            self.split_hand = None


class Game:
    def __init__(self, players=[None], chips=1000, decks=6, hit_soft_17=True):
        self.shoe = Shoe(decks)
        self.dealer = Dealer(self.shoe, hit_soft_17=hit_soft_17)
        self.players = []
        for name in players:
            self.players.append(Player(self.shoe, name=name, chips=chips))
        self.all_hands = self.players + [self.dealer]
        self.active_players = []

    def mainloop(self):
        while self.play_hand():
            print('=' * 10)
            if self.shoe.time_to_shuffle():
                self.shoe.new()
                print('New shoe in play!')
                print('=' * 10)

    def play_hand(self):
        self.active_players = []
        self.collect_bets()
        if not self.players:
            return False
        self.deal_cards()
        print('Dealer: {}'.format(self.dealer.print_hand(downcard=True)))
        for player in self.active_players:
            print('{}: {}'.format(player.name, player.print_hand()))
        print('-' * 10)
        try:
            self.check_blackjack()
        except DealerBlackjack:
            return True
        for player in self.active_players.copy():
            self.play_player_hand(player)
        if self.active_players:
            print('-' * 10)
            self.dealer.play_hand()
            print('Dealer: {}'.format(self.dealer.print_hand()))
            self.pay_winners()
        return True

    def collect_bets(self):
        for player in self.players.copy():
            self.get_bet(player)

    def get_bet(self, player: Player):
        if player.chips == 0:
            print('{} is out of chips and is eliminated.'.format(player.name))
            self.players.remove(player)
            return
        print('{} has {} chips.'.format(player.name, player.chips))
        while True:
            betstr = input('Enter a bet, or [q]uit: ')
            if not betstr:
                continue
            if betstr[0].lower() == 'q':
                self.players.remove(player)
                return
            try:
                bet = int(betstr)
            except ValueError:
                print('Invalid bet!')
                continue
            if bet <= 0 or bet > player.chips:
                print('Invalid bet!')
                continue
            break
        player.bet = bet
        player.chips -= bet
        self.active_players.append(player)

    def deal_cards(self):
        for hand in self.all_hands:
            hand.reset()
        for _ in range(2):
            for hand in self.all_hands:
                hand.hit()

    def check_blackjack(self):
        if self.dealer.check_insurance():
            for player in self.active_players:
                while True:
                    x = input('{}: Buy insurance? [y/n] '.format(player.name))
                    if not x:
                        continue
                    x = x[0].lower()
                    if x not in 'yn':
                        print('Invalid input!')
                        continue
                    break
                if x == 'y':
                    player.buy_insurance()
        if self.dealer.check_blackjack():
            print('Dealer has blackjack!')
            for player in self.active_players:
                if player.insurance:
                    player.chips += player.insurance * 3
                    player.insurance = False
                if player.check_blackjack():
                    print('{} has blackjack!'.format(player.name))
                    player.chips += player.bet
            self.active_players.clear()
            raise DealerBlackjack
        for player in self.active_players:
            if player.insurance:
                player.insurance = False
        for player in self.active_players.copy():
            if player.check_blackjack():
                print('{} has blackjack!'.format(player.name))
                player.chips += int(player.bet * 2.5)
                self.active_players.remove(player)

    def play_player_hand(self, player: Player):
        while not player.check_bust():
            if player.split_hand:
                name = '{} (hand 1)'.format(player.name)
            else:
                name = player.name
            print('{}: {}'.format(name, player.print_hand()))
            if player.split_hand and player.cards[0] == 1:
                break
            if player.total() == 21:
                break
            actionlist = [ACTION_HIT, ACTION_STAND]
            actioncheck = 'hs'
            lowchipscheck = ''
            if len(player.cards) == 2 and not player.split_hand:
                if player.check_split():
                    if player.check_bet():
                        actionlist.append(ACTION_SPLIT)
                        actioncheck += 'p'
                    else:
                        lowchipscheck += 'p'
                if player.check_double():
                    if player.check_bet():
                        actionlist.append(ACTION_DOUBLE)
                        actioncheck += 'd'
                    else:
                        lowchipscheck += 'd'
                actionlist.append(ACTION_SURRENDER)
                actioncheck += 'u'
            actions = ', '.join(actionlist)
            while True:
                action = input(actions + '? ')
                if not action:
                    continue
                action = action[0].lower()
                if action in lowchipscheck:
                    print('You have insufficient chips for that action.')
                    continue
                elif action not in actioncheck:
                    print('Invalid action!')
                    continue
                else:
                    break
            if action == 'h':
                player.hit()
                continue
            elif action == 's':
                break
            elif action == 'p':
                player.split()
                continue
            elif action == 'd':
                player.double_down()
                print('{}: {}'.format(name, player.print_hand()))
                break
            elif action == 'u':
                player.surrender()
                self.active_players.remove(player)
                break
        else:
            print('{}: {}'.format(name, player.print_hand()))
            print('{} busted!'.format(name))
            if not player.split_hand:
                self.active_players.remove(player)
        if player.split_hand:
            player.split_hand.hit()
            name = '{} (hand 2)'.format(player.name)
            while not player.split_hand.check_bust():
                print('{}: {}'.format(name, player.split_hand.print_hand()))
                if player.split_hand and player.split_hand.cards[0] == 1:
                    break
                if player.split_hand.total() == 21:
                    break
                actions = '{}, {}? '.format(ACTION_HIT, ACTION_STAND)
                while True:
                    action = input(actions)
                    if not action:
                        continue
                    action = action[0].lower()
                    if action not in 'hs':
                        print('Invalid action!')
                        continue
                    else:
                        break
                if action == 'h':
                    player.split_hand.hit()
                    continue
                elif action == 's':
                    break
            else:
                print('{}: {}'.format(name, player.split_hand.print_hand()))
                print('{} busted on the split hand!'.format(player.name))
                if player.check_bust():
                    self.active_players.remove(player)

    def pay_winners(self):
        for player in self.active_players:
            self.resolve_hand(player, player)
            if player.split_hand:
                self.resolve_hand(player, player.split_hand)

    def resolve_hand(self, player, hand):
        if hand is player:
            msg = ''
        else:
            msg = ' on the split hand'
        if hand.check_bust():
            return
        elif (self.dealer.check_bust() or
                hand.total() > self.dealer.total()):
            player.chips += player.bet * 2
            print('{} wins{}!'.format(player.name, msg))
        elif hand.total() == self.dealer.total():
            player.chips += player.bet
            print('{} pushes{}.'.format(player.name, msg))
        else:
            print('{} loses{}.'.format(player.name, msg))


def setup():
    while True:
        pstr = input('Enter number of players [1-6] or [q]uickstart: ')
        if not pstr:
            continue
        if pstr[0].lower() == 'q':
            return Game()
            break
        try:
            pnum = int(pstr)
        except ValueError:
            print('Invalid input!')
            continue
        if pnum < 1 or pnum > 6:
            print('Number of players must be between 1 and 6.')
            continue
        break

    players = []
    for n in range(pnum):
        while True:
            name = input('Enter name for player {}: '.format(n))
            if name:
                break
        players.append(name)

    while True:
        cstr = input('Enter starting chips: ')
        if not cstr:
            continue
        try:
            chips = int(cstr)
        except ValueError:
            print('Invalid input!')
            continue
        if chips <= 0:
            print('Invalid input!')
            continue
        break

    while True:
        dstr = input('Enter number of decks in the shoe: ')
        if not dstr:
            continue
        try:
            decks = int(dstr)
        except ValueError:
            print('Invalid input!')
            continue
        if decks < 1 or decks > 8:
            print('Number of decks must be between 1 and 8.')
            continue
        break

    while True:
        dealstr = input('Should dealer hit on soft 17? [y/n] ')
        if not dealstr:
            continue
        dealstr = dealstr[0].lower()
        if dealstr not in 'yn':
            print('Invalid input!')
            continue
        break
    hit_soft_17 = True if dealstr == 'y' else False

    return Game(players, chips, decks, hit_soft_17)


def main():
    print('Welcome to PyBlackjack!')
    game = setup()
    game.mainloop()
    print('Thanks for playing!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
