import json
from random import choice, randint
import time
import rules


class ValueErrorException(Exception):
    def __str__(self):
        return 'Value error'


class Cherv:
    def __str__(self):
        return f'Cherv'


class Bubna:
    def __str__(self):
        return f'Bubna'


class Vini:
    def __str__(self):
        return f'Vini'


class Krest:
    def __str__(self):
        return f'Krest'


class Card:
    NOMINAL = {
        'TUZ': 11,
        'KOROL': 4,
        'DAMA': 3,
        'VALET': 2,
        '10': 10,
        '9': 9,
        '8': 8,
        '7': 7,
        '6': 6,
        '5': 5,
        '4': 4,
        '3': 3,
        '2': 2
    }

    def __init__(self, suit, index):
        self.suit = suit
        self.index = index

    def __str__(self):
        key = self.get_key()
        result = '|'
        result += '-' * 20
        result += f'\n| {self.suit} | {key}'
        result += '\n'
        result += '|'
        result += '-' * 20
        return result

    def get_value(self):
        return [x for x in self.NOMINAL.values()][self.index]

    def get_key(self):
        return [x for x in self.NOMINAL.keys()][self.index]


class CardDeck:
    __SUIT = [Cherv(), Bubna(), Vini(), Krest()]
    __NOMINALS = Card.NOMINAL

    def __init__(self):
        self.deck_lst = []

    def collect_deck(self):
        self.deck_lst = []
        deck = {}
        for s in self.__SUIT:
            for i in range(len(self.__NOMINALS)):
                deck[Card(s, i)] = [x for x in self.__NOMINALS.values()][i]
        n = len(deck)
        while n > 0:
            rnd_key = choice([x for x in deck.keys()])
            if rnd_key not in self.deck_lst:
                self.deck_lst.append(rnd_key)
                n -= 1
        # TEST #####################################################
        # for i in deck:
        #     for j in deck:
        #         if i.suit != j.suit:
        #             if i.get_key() == '10':
        #                 self.deck_lst[0] = i
        #             if j.get_key() == 'TUZ':
        #                 self.deck_lst[1] = j
        #             if i.get_key() == '10':
        #                 self.deck_lst[2] = i
        #             if j.get_key() == 'TUZ':
        #                 self.deck_lst[3] = j
        ############################################################
        return self.deck_lst


class Bank:
    __DB = None
    __INDEX = 0
    __CREDIT_VALUE = {
        100: 1,
        500: 0.5,
        1000: 0.1
    }
    __VALUE_USER_IS_ZERO = False

    @property
    def VALUE_USER_IS_ZERO(self):
        return self.__VALUE_USER_IS_ZERO

    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.__value_bank = None
        self.__value_user = None
        self.__attempt = 3

    @property
    def attempt(self):
        return self.__attempt

    def get_value_bank(self):
        self.__value_bank = self.__DB[0]['value_bank']
        return self.__value_bank

    def __set_value_bank(self, value):
        self.__DB[0]['value_bank'] = value

    def bank_value_balance(self):
        if self.get_value_bank() < 500000:
            self.__set_value_bank(self.get_value_bank() + 100000)
        if self.get_value_bank() > 5000000:
            self.__set_value_bank(self.get_value_bank() - 100000)

    def get_value_user(self):
        if self.__check_username(self.__DB, self.__username):
            self.__value_user = self.__DB[self.__INDEX]['value_user']
        else:
            self.__value_user = 100
        return self.__value_user

    def set_value_user(self, value):
        self.__DB[self.__INDEX]['value_user'] = value

    def check_value_user(self):
        self.__debt_writeoff()
        if self.__DB[self.__INDEX]['value_user'] == 0:
            self.__VALUE_USER_IS_ZERO = True
        else:
            self.__VALUE_USER_IS_ZERO = False

    def __set_refundable_amount(self, value):
        self.__DB[self.__INDEX]['refundable_amount'] += value

    def __get_refundable_amount(self):
        return self.__DB[self.__INDEX]['refundable_amount']

    def __debt_writeoff(self):
        if self.get_value_user() - 100 >= self.__get_refundable_amount():
            self.__DB[0]['value_bank'] += self.__get_refundable_amount()
            self.__DB[self.__INDEX]['refundable_amount'] = 0

    def get_credit(self):
        print('AVAILABLE CREDIT')
        print('-' * 50)
        for i, val in enumerate(self.__CREDIT_VALUE.keys()):
            if i < len(self.__CREDIT_VALUE) - 1:
                print(val, end=" | ")
            else:
                print(val, end="")
        print()
        print('-' * 50)
        while True:
            enter_credit = input('Enter credit: ')
            check = any(map(lambda x: str(x) == enter_credit, self.__CREDIT_VALUE.keys()))
            if not check:
                print('Enter error (this credit does not exist)')
                continue
            self.set_value_user(int(enter_credit))
            self.__set_value_bank(self.get_value_bank() - int(enter_credit))
            amount = self.__calculate_refundable_amount(int(enter_credit))
            self.__set_refundable_amount(amount)
            print()
            break

    def __calculate_refundable_amount(self, value):
        amount = value
        for key, val in self.__CREDIT_VALUE.items():
            if value == key:
                amount += value * val
        return int(amount)

    def load_db(self, filename):
        with open(filename) as file:
            self.__DB = json.load(file)
        return self.__DB

    def save_db(self, filename, db):
        with open(filename, 'w') as file:
            json.dump(db, file, indent=2)

    def __check_username(self, db, name):
        for i, item in enumerate(db[1:]):
            if item['username'] == name:
                self.__INDEX = i + 1
                return True
            else:
                self.__INDEX = len(db)
        return False

    def new_user_flag(self):
        if self.__check_username(self.__DB, self.__username):
            return False
        return True

    def __check_password(self, db, password):
        if db[self.__INDEX]['password'] != password:
            print(f'-- password is wrong!')
            return False
        return True

    def __reenter_password(self):
        if not self.__check_password(self.__DB, self.__password):
            while True:
                if self.__attempt == 1:
                    att = 'attempt'
                else: att = 'attempts'
                if self.__attempt == 0:
                    break
                password = input(f'REenter password ({self.__attempt} {att}): ')
                if not self.__check_password(self.__DB, password):
                    self.__attempt -= 1
                    continue
                else:
                    self.__password = password
                    return self.__password
        else:
            return self.__password

    def __repeat_password(self):
        while True:
            repeat_pass = input('Repeat password: ')
            if repeat_pass != self.__password:
                self.__attempt -= 1
                if self.__attempt == 0:
                    exit()
                continue
            else:
                self.__password = repeat_pass
            return self.__password

    def add_db(self, db):
        if self.__check_username(db, self.__username):
            db[self.__INDEX] = {
                    "username": self.__username,
                    "password": self.__reenter_password(),
                    "value_user": self.get_value_user(),
                    "refundable_amount": self.__get_refundable_amount()
                }
        else:
            db.append(
                {
                    "username": self.__username,
                    "password": self.__repeat_password(),
                    "value_user": self.get_value_user(),
                    "refundable_amount": 0
                }
            )
        db[0]['value_bank'] = self.get_value_bank()

    def show_profile(self):
        print('-' * 50)
        print(f'{"":^24} | {"":^22}')
        print(f'{self.__DB[self.__INDEX]["username"] :^24} | {"BANK" :^22}')
        print(f'{"--------------":^24} | {"--------------":^22}')
        print(f'{self.get_value_user() :^24} | {self.get_value_bank() :^22}')
        if self.__get_refundable_amount() > 0:
            debt = "Debt: " + str(self.__get_refundable_amount())
            print(f'{debt :^24} | {"" :^22}')
        print(f'{"":^24} | {"":^22}')
        print('-' * 50)
        print()

    def release_bet(self, won, score, blackjack_bet):
        if won:
            if blackjack_bet:
                self.__DB[self.__INDEX]["value_user"] += score * 2
                self.__DB[0]["value_bank"] -= score
            else:
                self.__DB[self.__INDEX]["value_user"] += score
                self.__DB[0]["value_bank"] -= score
        else:
            self.__DB[self.__INDEX]["value_user"] -= score
            self.__DB[0]["value_bank"] += score

    def welcome(self, filename):
        self.__DB = self.load_db(filename)

    def save(self, filename):
        self.add_db(self.__DB)
        self.save_db(filename, self.__DB)


class UserDescriptor:
    def __set_name__(self, owner, name):
        self.name = "__" + name

    def __set__(self, instance, value):
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        return getattr(instance, self.name)


class User:
    name = UserDescriptor()
    password = UserDescriptor()

    def __init__(self, name, password):
        self.name = name
        self.password = password


class BlackJack:
    __BET_VALUE = [5, 10, 25, 50, 100, 150, 250, 500]
    __VALUE_SUM_USER = 0
    __VALUE_SUM_DEALER = 0
    __FLAG_USER = True
    __FLAG_DEALER = True
    __FLAG_RESULT = None
    __INDEX = 0
    __BLACKJACK = False
    __BLACKJACK_BET = None
    __COUNT_USER_WIN_SEQUENCE = 0

    @property
    def FLAG_RESULT(self):
        return self.__FLAG_RESULT

    @property
    def BLACKJACK_BET(self):
        return self.__BLACKJACK_BET

    def __init__(self):
        self.__lst_user = []
        self.__lst_dealer = []
        self.__lst_cheat = []
        self.__bet = 0
        self.__card = CardDeck()
        self.__result_cheat = []

    @property
    def bet(self):
        return self.__bet

    def do_bet(self, allin):
        available_bet = [bet for bet in self.__BET_VALUE if bet <= allin]
        available_bet.append('allin')
        available_bet.append('all')
        print('AVAILABLE BET')
        print('-' * 50)
        for i, bet in enumerate(available_bet[:-1]):
            if i < len(available_bet[:-1]) - 1:
                print(bet, end=' | ')
            else:
                print(bet, end='')
        print()
        print('-' * 50)
        while True:
            enter_bet = input('Enter bet: ')
            check = any(map(lambda x: str(x) == enter_bet, available_bet))
            if not check:
                print('Enter error (this bet does not exist)')
                continue
            if enter_bet not in ('allin', 'all'):
                self.__bet = int(enter_bet)
            else:
                self.__bet = allin
            return self.__bet

    def toplay(self, username):
        if self.__INDEX == 0 or self.__INDEX > 39:
            self.__card.collect_deck()
            self.__INDEX = 0
        self.__FLAG_USER = True
        self.__FLAG_DEALER = True
        self.__FLAG_RESULT = None
        self.__BLACKJACK = False
        self.__lst_user = []
        self.__lst_dealer = []
        self.__lst_cheat = []
        self.__VALUE_SUM_USER = 0
        self.__VALUE_SUM_DEALER = 0
        self.__lst_user.append(self.__card.deck_lst[self.__INDEX])
        self.__VALUE_SUM_USER += self.__card.deck_lst[self.__INDEX].get_value()
        self.__INDEX += 1
        self.__lst_user.append(self.__card.deck_lst[self.__INDEX])
        self.__VALUE_SUM_USER += self.__card.deck_lst[self.__INDEX].get_value()
        if self.__card.deck_lst[self.__INDEX].get_key() == 'TUZ' and \
                self.__VALUE_SUM_USER > 21:
            self.__VALUE_SUM_USER -= self.__card.deck_lst[self.__INDEX].get_value()
            self.__VALUE_SUM_USER += 1
        print()
        time.sleep(0.5)
        print('-' * 30)
        print(f'{username} HIT')
        print('-' * 30)
        time.sleep(1)
        for card in self.__lst_user:
            time.sleep(0.5)
            print(card)
        print(f'{username} score: {self.__VALUE_SUM_USER}')
        if self.__VALUE_SUM_USER == 21:
            print('BlackJack!')
            self.__BLACKJACK = True
            self.__BLACKJACK_BET = True
        while self.__FLAG_DEALER and self.__FLAG_USER:
            print("  |")
            print("  |")
            enter = self.__make_enter()
            self.__INDEX += 1
            if enter == 'y':
                time.sleep(0.5)
                print('-' * 30)
                print(f'{username} HIT')
                print('-' * 30)
                time.sleep(1)
                self.__lst_user.append(self.__card.deck_lst[self.__INDEX])
                self.__VALUE_SUM_USER += self.__card.deck_lst[self.__INDEX].get_value()
                if self.__card.deck_lst[self.__INDEX].get_key() == 'TUZ' and \
                        self.__VALUE_SUM_USER > 21:
                    self.__VALUE_SUM_USER -= self.__card.deck_lst[self.__INDEX].get_value()
                    self.__VALUE_SUM_USER += 1
                for card in self.__lst_user:
                    time.sleep(0.5)
                    print(card)
                print(f'{username} score: {self.__VALUE_SUM_USER}')
                if self.__VALUE_SUM_USER == 21:
                    print('BlackJack!')
                    self.__BLACKJACK = True
                if self.__VALUE_SUM_USER > 21:
                    print('Overkill!')
                    self.__FLAG_USER = False
                    self.__INDEX += 1
                    break
            else:
                time.sleep(0.5)
                print('-' * 30)
                print('DEALER HIT')
                print('-' * 30)
                time.sleep(1)
                # cheat method ######################################
                start = self.__VALUE_SUM_USER if self.__VALUE_SUM_USER == 21 \
                    else self.__VALUE_SUM_USER + 1
                target = choice([x for x in range(start, 22)])
                if self.__COUNT_USER_WIN_SEQUENCE > randint(2, 5):
                    sum_border = target
                    self.__cheat_cards(self.__card.deck_lst[self.__INDEX:], target)
                    self.__replace_cheat_cards(self.__card.deck_lst,
                                               self.__INDEX,
                                               self.__result_cheat)
                    self.__result_cheat = []
                else:
                    sum_border = 17
                #####################################################
                while self.__VALUE_SUM_DEALER < sum_border:
                    self.__lst_dealer.append(self.__card.deck_lst[self.__INDEX])
                    self.__VALUE_SUM_DEALER += self.__card.deck_lst[self.__INDEX].get_value()
                    if self.__card.deck_lst[self.__INDEX].get_key() == 'TUZ' and \
                            self.__VALUE_SUM_DEALER > 21:
                        self.__VALUE_SUM_DEALER -= self.__card.deck_lst[self.__INDEX].get_value()
                        self.__VALUE_SUM_DEALER += 1
                    if self.__VALUE_SUM_DEALER > 21:
                        self.__FLAG_DEALER = False
                        break
                    if self.__VALUE_SUM_DEALER == 21:
                        self.__FLAG_USER = self.__FLAG_DEALER = False
                    if self.__VALUE_SUM_DEALER >= 17:
                        self.__FLAG_USER = self.__FLAG_DEALER = False
                    self.__INDEX += 1
                for card in self.__lst_dealer:
                    time.sleep(0.5)
                    print(card)
                print(f'dealer score: {self.__VALUE_SUM_DEALER}')
                if self.__VALUE_SUM_DEALER == 21:
                    print('BlackJack!')
                if self.__VALUE_SUM_DEALER > 21:
                    print('Overkill!')

    def __cheat_cards(self, cards, target, part=[]):
        summa = sum([x.get_value() for x in part])
        if summa == target:
            self.__result_cheat.append(part)
        if len(self.__result_cheat) > 1:
            return
        if summa > target:
            return
        for i in range(len(cards)):
            n = cards[i]
            remain = cards[i + 1:]
            self.__cheat_cards(remain, target, part + [n])

    @staticmethod
    def __replace_cheat_cards(l, indx, r):
        ln = len(r) - 1
        n = indx - 1
        for item in r[ln]:
            n += 1
            for i in range(indx, len(l)):
                if item == l[i]:
                    tmp = l[n]
                    l[n] = item
                    l[i] = tmp

    def __make_enter(self):
        while True:
            if self.__BLACKJACK or self.__VALUE_SUM_USER == 20:
                enter = 'n'
                return enter
            else:
                enter = input('HIT ME (Y/N): ').lower()
            if enter not in ('y', 'n'):
                print('Not correct')
                continue
            return enter

    def result(self, username):
        print()
        if self.__VALUE_SUM_DEALER == self.__VALUE_SUM_USER and self.__VALUE_SUM_USER <= 21:
            print('-- Push')
            print()
            self.__FLAG_RESULT = None
            return
        if not self.__FLAG_USER and not self.__FLAG_DEALER and \
                self.__VALUE_SUM_USER < self.__VALUE_SUM_DEALER:
            print('-- Dealer win')
            self.__COUNT_USER_WIN_SEQUENCE = 0
            self.__FLAG_RESULT = False
            return
        if not self.__FLAG_USER and not self.__FLAG_DEALER and \
                self.__VALUE_SUM_USER > self.__VALUE_SUM_DEALER:
            print(f'-- {username} win')
            self.__COUNT_USER_WIN_SEQUENCE += 1
            self.__FLAG_RESULT = True
            return
        if not self.__FLAG_DEALER and self.__FLAG_USER:
            print(f'-- {username} win')
            self.__COUNT_USER_WIN_SEQUENCE += 1
            self.__FLAG_RESULT = True
        else:
            print('-- Dealer win')
            self.__COUNT_USER_WIN_SEQUENCE = 0
            self.__FLAG_RESULT = False

    def __bool__(self):
        if self.__FLAG_RESULT:
            return True
        else:
            return False


class Game:
    __SCORE = 0

    def __init__(self):
        self.__head()
        self.__rules()
        self.__game = BlackJack()
        self.__user = User(self.__set_username(), self.__set_password())
        self.__bank = Bank(self.__user.name, self.__user.password)

    def __head(self):
        print('-' * 50)
        bj = 'BLACKJACK 1.0.0'
        print()
        print(f'{bj :>33}')
        print()

    def __rules(self):
        print('-' * 50)
        print('RULES')
        while True:
            print('-' * 50)
            print('0 Skip')
            print('1 Credit')
            print('2 Bet')
            print('3 BlackJack')
            print('4 Card deck update')
            print('-' * 50)
            enter = input('Enter: ')
            print('-' * 50)
            if enter not in ('0', '1', '2', '3', '4', '5'):
                print('Not correct')
                continue
            if enter == '0':
                break
            if enter == '1':
                print(rules.Credit())
            if enter == '2':
                print(rules.Bet())
            if enter == '3':
                print(rules.BlackJack())
            if enter == '4':
                print(rules.CardsCollectUpdate())
            if enter == '5':
                print('Admin')

    def __welcome(self):
        self.__bank.welcome('db_bank.json')
        print('-' * 50)
        if not self.__bank.new_user_flag():
            print(f'Hello {self.__user.name}!')
        else:
            print(f'Hello new user {self.__user.name}!')

    def __set_username(self):
        name = input('Enter username: ')
        return name

    def __set_password(self):
        password = input('Enter password: ')
        return password

    def loop(self):
        self.__welcome()
        while True:
            self.__bank.save('db_bank.json')
            if self.__bank.attempt < 1:
                break
            time.sleep(1)
            self.__bank.bank_value_balance()
            self.__bank.show_profile()
            time.sleep(1)
            self.__bank.check_value_user()
            if self.__bank.VALUE_USER_IS_ZERO:
                self.__bank.get_credit()
            self.__game.do_bet(self.__bank.get_value_user())
            self.__game.toplay(self.__user.name)
            time.sleep(1)
            self.__game.result(self.__user.name)
            self.__SCORE += self.__game.bet
            if self.__game.FLAG_RESULT is not None:
                print(f'-- bet: {self.__game.bet}')
                print()
                self.__bank.release_bet(self.__game.__bool__(),
                                        self.__SCORE,
                                        self.__game.BLACKJACK_BET)
                go = self.__make_go()
            else:
                go = self.__make_go()
            if go == 'y':
                self.__bank.save('db_bank.json')
                self.__SCORE = 0
                continue
            if go == 'n':
                self.__bank.save('db_bank.json')
                self.__bank.show_profile()
                print(f'Goodbye {self.__user.name}!')
                break

    @staticmethod
    def __make_go():
        while True:
            go = input('AGAINE (Y/N): ').lower()
            if go not in ('y', 'n'):
                print('Not correct')
                continue
            return go

    def start(self):
        self.loop()


bj = Game()
bj.start()


# game = BlackJack()
# game.toplay()
# game.result()
# print(game.__bool__())
# print(game.bet)


# deck = CardDeck()
# deck.collect_deck()
# print(len(deck.deck_lst))
# for i in deck.deck_lst:
#     if i.get_key() == 'TUZ':
#         print(i, i.get_value())


















