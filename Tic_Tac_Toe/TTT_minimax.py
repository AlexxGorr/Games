from random import randint
from time import sleep
import sys


class BoardException(Exception):
    pass


class IndxException(BoardException):
    def __str__(self):
        return f'Index error!'


class PlaceException(Exception):
    pass


class Cell:
    def __init__(self, value=None):
        self.__value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, val):
        self.__value = val


class Board:
    FREE_CELL = None
    WIN_SITUATION = [
        (0, 0, 0),
        (1, 1, 1),
        (2, 2, 2),
        (0, 1, 2),
        (2, 1, 0),
    ]

    def __init__(self):
        self.__field = [[Cell() for _ in range(3)] for _ in range(3)]

    @property
    def field(self):
        return self.__field

    @field.setter
    def field(self, val):
        self.__field = val

    def __str__(self):
        line = '----------'
        numbers = f'\n  1  2  3'
        result = ''
        result += line
        result += numbers
        for num, row in enumerate(self.__field):
            result += f'\n{num + 1} ' \
                      f'{" ".join(list(map(lambda x: "_|" if x.value is None else x.value, row)))}'
        return result

    def __getitem__(self, item):
        if not self.__valid_indx(item, len(self.__field)):
            raise IndxException()
        x, y = item
        return self.__field[x][y]

    def __setitem__(self, key, value):
        if not self.__valid_indx(key, len(self.__field)):
            raise IndxException()
        x, y = key
        self.__field[x][y] = value

    @staticmethod
    def __valid_indx(indx, size):
        x, y = indx
        return x in range(size) and y in range(size)

    def check_status(self, simbol, field) -> bool:
        flag = False
        for row in self.WIN_SITUATION:
            if field[0][row[0]].value == \
                    field[1][row[1]].value == \
                    field[2][row[2]].value == simbol:
                flag = True
        for i in range(3):
            if field[i][0].value == \
                    field[i][1].value == \
                    field[i][2].value == simbol:
                flag = True
        return flag

    def game_over(self) -> bool:
        n = 0
        for row in self.__field:
            for i in row:
                if i.value != self.FREE_CELL:
                    n += 1
        if n == 9:
            return True

    def init(self):
        for row in self.__field:
            for i in row:
                i.value = self.FREE_CELL

    def make_move(self, target, simbol):
        x, y = target
        if self.__field[x][y].value is None:
            self.__field[x][y].value = simbol
        else: return False


class Player:
    def __init__(self, board, simbol):
        self.board = board
        self.simbol = simbol

    def ask(self):
        raise PlaceException()

    def turn(self, whois):
        print(f'{whois} -->')
        target = self.ask()
        try:
            repeat = self.board.make_move(target, self.simbol)
            return repeat
        except PlaceException as e:
            print(e)


class User(Player):
    def ask(self):
        while True:
            enter = input('enter: ').split()
            if len(enter) != 2:
                print('Not correct enter!')
                continue
            if not (enter[0].isdigit() and enter[1].isdigit()):
                print('Not correct enter!')
                continue
            y, x = int(enter[0]) - 1, int(enter[1]) - 1
            if not (x in range(3) and y in range(3)):
                print('Not correct enter!')
                continue
            if self.board[x, y].value != self.board.FREE_CELL:
                print('cell busy')
                continue
            return x, y


class AI(Player):
    def ask(self):
        game = Game()
        enter = None
        n = 0
        for row in self.board.field:
            for x in row:
                if not x.value == self.board.FREE_CELL:
                    n += 1
        if n == 0:
            x = randint(0, 2)
            y = randint(0, 2)
            # print(f'random | x: {x}, y: {y}')
            return x, y
        best_value = -sys.maxsize
        new_board = [self.board.field[x].copy() for x in range(3)]
        for x in range(3):
            for y in range(3):
                if self.board[x, y].value == self.board.FREE_CELL:
                    new_board[x][y].value = self.simbol
                    intended_value = game.minimax(new_board, 0, False)
                    new_board[x][y].value = self.board.FREE_CELL
                    # print(f'(ask) intended value: {intended_value}')
                    # print(f'(ask) new board | x: {x}, y: {y}')
                    # print('-' * 30)
                    if intended_value > best_value:
                        best_value = intended_value
                        enter = x, y
        # print(f'(ask) enter: {enter}')
        return enter


class Game:
    _SIMBOL_X = 'X|'
    _SIMBOL_0 = '0|'

    board = Board()
    board.init()

    def minimax(self, board, depth, is_maximizing=None):
        if self.board.check_status(self._SIMBOL_X, board):
            return depth - 100
        if self.board.check_status(self._SIMBOL_0, board):
            return 100 - depth
        if self.board.game_over():
            return 0
        if is_maximizing:
            best_value = -sys.maxsize
            simbol = self._SIMBOL_0
            for x in range(3):
                for y in range(3):
                    if board[x][y].value == self.board.FREE_CELL:
                        board[x][y].value = simbol
                        intended_value = self.minimax(board, depth + 1, False)
                        board[x][y].value = self.board.FREE_CELL
                        best_value = max(best_value, intended_value)
        else:
            best_value = sys.maxsize
            simbol = self._SIMBOL_X
            for x in range(3):
                for y in range(3):
                    if board[x][y].value == self.board.FREE_CELL:
                        board[x][y].value = simbol
                        intended_value = self.minimax(board, depth + 1, True)
                        board[x][y].value = self.board.FREE_CELL
                        best_value = min(best_value, intended_value)
        return best_value

    @staticmethod
    def _def_turn():
        print('Define first turn...')
        print('0 %')
        for i in range(1, 10 + 1):
            print(f'{i}0 %')
            sleep(0.3)
        x = randint(0, 1)
        return x

    def loop(self):
        print('TicTacToe 1.0.0')
        print('-' * 20)
        print(self.board)
        print()
        user = User(self.board, self._SIMBOL_X)
        ai = AI(self.board, self._SIMBOL_0)
        start_count = self._def_turn()
        n = start_count
        while True:
            if n % 2 == 0:
                print()
                user.turn('USER')
                print(self.board)
                print('-' * 20)
            else:
                print()
                ai.turn('AI')
                sleep(randint(1, 3))
                print(self.board)
                print('-' * 20)
            n += 1
            if self.board.check_status(self._SIMBOL_X, self.board.field):
                print()
                print('USER win!')
                break
            if self.board.check_status(self._SIMBOL_0, self.board.field):
                print()
                print('AI win!')
                break
            if self.board.game_over():
                print()
                print('Is draw!')
                break

    def start(self):
        return self.loop()


g = Game()
g.start()


















