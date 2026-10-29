from datetime import datetime
from random import randint, choice
from string import ascii_lowercase
import time
import json


class GameException(Exception):
    pass


class InitialException(GameException):
    def __str__(self):
        return 'Initial error!'


class OutPoleException(GameException):
    def __str__(self):
        return 'Out pole'


class CellUsedException(GameException):
    def __str__(self):
        return 'REPEAT'


class PlaceException(GameException):
    pass


class Ship:
    MARK_CELL = "■"

    def __init__(self, length, tp=1, x=None, y=None):
        self._length: int = length
        self._tp: int = tp
        self._x: int = x
        self._y: int = y
        # self._cells = [self.MARK_CELL for _ in range(length)]
        ##########################################################
        self._cells = [i + 1 for i in range(length)]
        ##########################################################
        self._is_move = True
        self._live = length

    def set_start_coords(self, x, y):
        self._x, self._y = x, y

    def get_start_coords(self) -> tuple:
        return self._x, self._y

    def move(self, go) -> tuple:
        if self._is_move:
            if self._tp == 1:
                return self._x + go, self._y
            if self._tp == 2:
                return self._x, self._y + go
        return self._x, self._y

    @staticmethod
    def contour(cell) -> list:
        contour = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1),
        ]
        result = []
        for i, j in cell:
            for dx, dy in contour:
                cell_contour = i + dx, j + dy
                result.append(cell_contour)
        return result

    def build_ship_tuples(self) -> list:
        result = []
        for i in range(self._length):
            if self._tp == 1:
                result.append((self._x + i, self._y))
            if self._tp == 2:
                result.append((self._x, self._y + i))
        return result

    def is_collide(self, ship) -> bool:
        ship_1 = self.build_ship_tuples()
        ship_2 = ship.build_ship_tuples()
        result = set(ship_1) & set(self.contour(ship_2))
        return len(result) > 0

    def is_out_pole(self, size) -> bool:
        if self._tp == 1:
            return not (self._x + self._length < size and self._x in range(size))
        if self._tp == 2:
            return not (self._y + self._length < size and self._y in range(size))

    def __getitem__(self, item):
        return self._cells[item]

    def __setitem__(self, key, value):
        self._cells[key] = value


# class Field:
#     def __init__(self, size, pole, hide, water):
#         self.size = size
#         self.pole = pole
#         self.hide = hide
#         self.water = water
#
#     def __str__(self):
#         abc = list(map(lambda x: x, ascii_lowercase))
#         result = ''
#         result += f'     {" ".join(abc[:self.size])}'
#         for num, line in enumerate(self.pole):
#             if self.hide:
#                 row = [str(x).replace(str(x), self.water) if
#                           str(x).isdigit() else x for x in line]
#             else:
#                 row = [x for x in line]
#             result += f'\n{abc[num]} {str(num + 1).rjust(2, "0")} {" ".join(row)}'
#         return result
#
#     @property
#     def result(self):
#         return self.result
#


class GamePole:
    MARK_WATER = '-'
    MARK_CONTOUR = '+'
    MARK_SHOT = '*'
    MARK_CELL_KILL = 'X'

    def __init__(self, size=10, hide=False):
        self._size = size
        self._ships = []
        self._ships_ghost = []
        self._pole = [[self.MARK_WATER for _ in range(size)] for _ in range(size)]
        self._busy_shot = []
        self._busy_shot_contour = []
        self._count_ships = 0
        self._hide = hide
        self._flag_wound = False
        self._flag_dead = False
        self._wound_coords = []
        self._cell_used = False
        self._var = 1
        self._count_shot = 0
        self._count_shot_cell_used = 0

    @property
    def hide(self):
        return self._hide

    @hide.setter
    def hide(self, val):
        self._hide = val

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, val):
        self._size = val

    def __build_ships_stek(self):
        ships_collection = []
        deck = None
        if self.size <= 10:
            deck = 4
        elif 10 < self.size <= 12:
            deck = 5
        var = [(i + 1, j) for i, j in enumerate(range(deck, 0, -1))]
        for a, b in var:
            for _ in range(b):
                ship = Ship(a, tp=randint(1, 2))
                ships_collection.append(ship)
        ships_collection.reverse()
        return ships_collection

    def init(self):
        self.__install_ships()
        self.__draw_pole()

    def __install_ships(self):
        cnt = 0
        for ship in self.__build_ships_stek():
            while True:
                cnt += 1
                if cnt > 2000:
                    return None
                ship.set_start_coords(
                    randint(0, self._size - 1),
                    randint(0, self._size - 1)
                )
                if not ship.is_out_pole(self._size):
                    result = any([check_ship.is_collide(ship) for check_ship in self._ships])
                    if not result:
                        try:
                            self._ships.append(ship)
                            break
                        except InitialException as e:
                            print(e)

    def get_ships(self):
        return self._ships

    def get_ships_move(self):
        return [x for x in self._ships_ghost]

    @staticmethod
    def __check_go_perimetr(go, coord, size, ln):
        return go + coord in range(0, size - ln)

    @staticmethod
    def __check_go_collision(ghost_ship, ships, ghost_ships):
        result = []
        cnt = 1
        if len(ghost_ships) == 0:
            for x in range(len(ships)):
                if ships[x]._length != ghost_ship._length:
                    if ghost_ship.is_collide(ships[x]):
                        result.append(ships[x])
        else:
            for x in range(len(ghost_ships)):
                cnt += 1
                if ghost_ship.is_collide(ghost_ships[x]):
                    result.append(ghost_ships[x])
            for x in range(cnt, len(ships)):
                if ghost_ship.is_collide(ships[x]):
                    result.append(ships[x])
        return not len(result) > 0

    def __is_collision_is_perimert(self, ship_ln, ship_tp, ship, go, ship_axis):
        collision = self.__check_go_collision(Ship(
            ship_ln,
            ship_tp,
            ship.move(go)[0],
            ship.move(go)[1]),
            self._ships,
            self._ships_ghost
        )
        perimetr = self.__check_go_perimetr(
            go,
            ship_axis,
            self._size,
            ship_ln
        )
        return collision, perimetr

    def __calculate_go(self, go, ship, ship_axis, ship_ln, ship_tp):
        collision, perimetr = self.__is_collision_is_perimert(
            ship_ln,
            ship_tp,
            ship,
            go,
            ship_axis
        )
        if not (collision and perimetr):
            go *= -1
        else:
            go
        collision, perimetr = self.__is_collision_is_perimert(
            ship_ln,
            ship_tp,
            ship,
            go,
            ship_axis
        )
        if not (collision and perimetr):
            go = 0
        self._ships_ghost.append(Ship(
            ship_ln,
            ship_tp,
            ship.move(go)[0],
            ship.move(go)[1],
        ))
        return go

    def move_ships(self):
        self.reset_pole()
        for ship in self._ships:
            cell = 0
            positive = 1
            negative = -1
            go = choice([positive, negative])
            if ship._tp == 1:
                go_result = self.__calculate_go(
                    go,
                    ship,
                    ship._x,
                    ship._length,
                    ship._tp
                )
                for i in range(ship._length):
                    for y, x in [ship.move(go_result)]:
                        self._pole[x][y + i] = ship[cell]
                        cell += 1
            if ship._tp == 2:
                go_result = self.__calculate_go(
                    go,
                    ship,
                    ship._y,
                    ship._length,
                    ship._tp
                )
                for i in range(ship._length):
                    for y, x in [ship.move(go_result)]:
                        self._pole[x + i][y] = ship[cell]
                        cell += 1
        self._ships_ghost = []

    def __draw_pole(self):
        for ship in self._ships:
            start_coord = ship.get_start_coords()
            x = start_coord[0]
            y = start_coord[1]
            if ship._tp == 1:
                for i in range(ship._length):
                    self.__fill_position(x + i, y, ship[i])
            if ship._tp == 2:
                for i in range(ship._length):
                    self.__fill_position(x, y + i, ship[i])

    def __fill_position(self, x, y, cell):
        self._pole[y][x] = cell

    def _fill_contour(self, contour, verbose_contour=True):
        for b, a in contour:
            if a in range(0, self._size) and b in range(0, self._size):
                if self._pole[a][b] == self.MARK_WATER:
                    if verbose_contour:
                        self._pole[a][b] = self.MARK_CONTOUR
                    else:
                        self._pole[a][b] = self.MARK_WATER

    def show(self):
        # field = Field(self.size, self._pole, self._hide, self.MARK_WATER)
        abc = list(map(lambda x: x, ascii_lowercase))
        print('    ', ' '.join([abc[x] for x in range(self._size)]))
        # print('    ', ' '.join([str(x) for x in range(self._size)]))
        for num, line in enumerate(self._pole):
            if self._hide:
                result = [str(x).replace(str(x), self.MARK_WATER) if
                          str(x).isdigit() else x for x in line]
                # result = [str(x).replace(str(x), self.MARK_WATER) if
                #           Ship.MARK_CELL else x for x in line]
            else:
                result = [x for x in line]
            print(abc[num], str(num + 1).rjust(2, '0'), *result)
        print()

    def get_pole(self):
        return tuple(tuple(self.MARK_WATER if type(i) is str else i for i in line)
                     for line in self._pole)

    def reset_pole(self):
        self._pole = [[self.MARK_WATER for _ in line] for line in self._pole]
        return self._pole

    def shot(self, x) -> bool:
        if not (x[0] in range(self._size) or x[1] in range(self._size)):
            raise OutPoleException()
        if x in self._busy_shot_contour or x in self._busy_shot:
            self._cell_used = True
            self._count_shot_cell_used += 1
            print(f'Cell used: ({x[0] + 1}, {x[1] + 1})')
            print(f'count shot (cell used): {self._count_shot_cell_used}')
            print('-' * 20)
            raise CellUsedException()
        self._busy_shot.append(x)
        self._count_shot_cell_used = 0
        #############################################################
        # print(f'busy shot: \n{self._busy_shot}')
        # print(f'busy shot contour: \n{self._busy_shot_contour}')
        #############################################################
        time.sleep(0.3)
        for ship in self._ships:
            if x in ship.build_ship_tuples():
                ship[ship.build_ship_tuples().index(x)] = self.MARK_CELL_KILL
                ship._live -= 1
                if ship._live == 0:
                    self._count_ships += 1
                    print(f'- DEAD ({x[0] + 1}, {x[1] + 1})')
                    print('-' * 30)
                    time.sleep(1)
                    ship._is_move = False
                    self._flag_wound = False
                    self._flag_dead = True
                    self._wound_coords = []
                    self._count_shot = 0
                    if ship._tp == 1:
                        for i in range(ship._length):
                            contour = ship.contour([(ship._x + i, ship._y)])
                            self.__app_contour_dead(contour, self._busy_shot_contour)
                    else:
                        for i in range(ship._length):
                            contour = ship.contour([(ship._x, ship._y + i)])
                            self.__app_contour_dead(contour, self._busy_shot_contour)
                    return True
                else:
                    print(f'- WOUND ({x[0] + 1}, {x[1] + 1})')
                    print('-' * 30)
                    time.sleep(1)
                    ship._is_move = False
                    self._flag_wound = True
                    self._flag_dead = False
                    self._wound_coords.append(x)
                    return True
            else:
                self._flag_wound = False
                self._flag_dead = False
        print(f'- MISSED ({x[0] + 1}, {x[1] + 1})')
        print('-' * 30)
        time.sleep(1)
        return False

    def __app_contour_dead(self, contour, busy_shot_contour):
        for j in contour:
            if j not in busy_shot_contour:
                busy_shot_contour.append(j)

    def defeat(self):
        return self._count_ships == len(self._ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise PlaceException()

    def turn(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except GameException as e:
                print(e)


class AI(Player):
    __MAP = {1: (-1, 0), 2: (0, -1), 3: (1, 0), 4: (0, 1)}

    def ask(self):
        # print(f'count shot cell used: {self.enemy._count_shot_cell_used}')
        while True:
            rand_coord = randint(0, self.board._size - 1), randint(0, self.board._size - 1)
            if self.enemy._count_shot_cell_used > 10:
                coord = rand_coord
                return coord
            if not self.enemy._flag_wound and len(self.enemy._wound_coords) == 0:
                coord = rand_coord
                return coord
            if len(self.enemy._wound_coords) >= 2:
                coord = self.__shot_analizer_finish_off(self.enemy._wound_coords[:1],
                                                        self.enemy._wound_coords[-1:],
                                                        self.enemy._flag_wound,
                                                        self.enemy._cell_used)
                return coord
            if len(self.enemy._wound_coords) == 1:
                coord = self.__shot_analizer(self.enemy._wound_coords[-1:],
                                             self.board._size)
                return coord
            if self.enemy._flag_wound and len(self.enemy._wound_coords) == 0:
                coord = self.__shot_analizer(self.enemy._wound_coords[-1:],
                                             self.board._size)
                return coord

    @classmethod
    def __shot_analizer(cls, wound_coord, size):
        lst = []
        for x, y in wound_coord:
            for dx, dy in cls.__MAP.values():
                cell_contour = x + dx, y + dy
                lst.append(cell_contour)
        for n, cell in enumerate(lst):
            if cell[0] not in range(size) or cell[1] not in range(size):
                del lst[n]
        return choice(lst)

    def __shot_analizer_finish_off(self, wound_coord, wound_coord_2, wound, cell_used):
        orient = None
        if wound_coord[0][0] != wound_coord_2[0][0]:
            orient = 1
        if wound_coord[0][1] != wound_coord_2[0][1]:
            orient = 2
        super_step = len(self.enemy._wound_coords)
        if wound_coord[0][0] > wound_coord_2[0][0] or wound_coord[0][1] > wound_coord_2[0][1]:
            inc = -1
        else: inc = 1
        if not wound or cell_used:
            self.enemy._count_shot += 1
        if self.enemy._count_shot % 2 == 0:
            self.enemy._var = inc
        else: self.enemy._var = -inc
        # print(f'bad shot: {self.enemy._count_shot} | var: {self.enemy._var}')
        for x, y in wound_coord_2:
            if wound:
                if orient == 1:
                    out = self.__is_out_range(x, self.enemy._var, self.board._size)
                    # print(f'out x: {out}')
                    time.sleep(0.3)
                    if out:
                        coord = x + super_step * (self.enemy._var * -1), y
                        # print(f'x: {x + 1} | super step: {super_step} | var: {self.enemy._var}')
                    else: coord = x + self.enemy._var, y
                else:
                    out = self.__is_out_range(y, self.enemy._var, self.board._size)
                    # print(f'out y: {out}')
                    time.sleep(0.3)
                    if out:
                        coord = x, y + super_step * (self.enemy._var * -1)
                        # print(f'y: {y + 1} | super step: {super_step} | var: {self.enemy._var}')
                    else: coord = x, y + self.enemy._var
                return coord
            else:
                if orient == 1:
                    coord = x + super_step * self.enemy._var, y
                else: coord = x, y + super_step * self.enemy._var
                return coord

    @staticmethod
    def __is_out_range(n, var, size):
        if n + var not in range(size):
            return True
        return False


class User(Player):
    def ask(self):
        letters = list(map(lambda x: x, ascii_lowercase))
        text = ''
        size = self.board._size
        ln = None
        if size < 10:
            ln = 2
            text = 'digit'
        if size >= 10:
            ln = 3
            text = 'digits'
        while True:
            enter = input(f'Enter (letter & {text}): ').replace(' ', '')
            valid_alpha = [x for x in enter if x.isalpha()]
            if len(enter) == 0:
                print(f'NOT correct - (is empty!)')
                continue
            if len(enter) == 1 or enter[0].isdigit():
                print(f'NOT correct - ({ln} simbols: 1 letter, {ln - 1} {text})')
                continue
            if len(valid_alpha) > 1:
                print('NOT correct - (letter must be only one!)')
                continue
            alpha = enter[0]
            digit = enter[1:]
            if ln == 2:
                digit = int(digit[0])
            if ln == 3:
                digit = int(digit)
            if not (len(enter) <= ln and alpha.isalpha() and isinstance(digit, int)):
                print(f'NOT correct - ({ln} simbols: 1 letter, {ln - 1} {text})')
                continue
            elif int(digit) - 1 not in range(self.board._size):
                print('NOT correct - (range out)')
                continue
            elif letters.index(alpha.lower()) not in range(self.board._size):
                print('NOT correct - (first simbol range out)')
                continue
            coord = letters.index(alpha.lower()), int(digit) - 1
            return coord


class Statistic:
    __DB = None
    __WIN = None
    __CNT_USER = 0
    __CNT_AI = 0

    def load_db(self, filename):
        with open(filename) as file:
            self.__DB = json.load(file)
        return self.__DB

    def save_db(self, filename, db):
        with open(filename, 'w') as file:
            json.dump(db, file, indent=2)

    def __init__(self, username, size):
        self.__username = username
        self.__size = size
        self.__score = 0

    @property
    def username(self):
        return self.__username

    @staticmethod
    def __check_name(name, db):
        for row in range(len(db)):
            if name == db[row]['username']:
                return True
        return False

    def log_in(self, db):
        while True:
            if self.__check_name(self.__username, db):
                self.__username += '1'
            else: break

    def set_win(self, win=None):
        self.__WIN = win

    def set_cnt_user(self, cnt=0):
        self.__CNT_USER = cnt

    def set_cnt_ai(self, cnt=0):
        self.__CNT_AI = cnt

    def __calculate_score(self):
        user_koef = self.__CNT_USER / self.__size
        ai_koef = self.__CNT_AI / self.__size
        if self.__WIN:
            self.__score = round(user_koef, 2)
        else: self.__score = - round(ai_koef, 2)
        return self.__score

    def add_db(self, db):
        t = datetime.now()
        time_str = str(t.hour) + ':' + \
                   str(t.minute) + '-' + \
                   str(t.day) + '/' + \
                   str(t.month) + '/' + \
                   str(t.year)
        self.__fix_size(db)
        db.append(
            {
                "username": self.__username,
                "score": self.__calculate_score(),
                "size": self.__size,
                "win": self.__WIN,
                "cnt_user": self.__CNT_USER,
                "cnt_ai": self.__CNT_AI,
                "time": time_str
            }
        )

    def welcome(self, filename):
        self.__DB = self.load_db(filename)
        self.log_in(self.__DB)
        print(f'---> Welcome {self.__username}!')
        time.sleep(1)
        print('-' * 50)

    @staticmethod
    def __sort_db(copy_DB):
        for i in range(len(copy_DB) - 1):
            for j in range(len(copy_DB) - 1 - i):
                if copy_DB[j]["score"] >= copy_DB[j + 1]["score"]:
                    copy_DB[j], copy_DB[j + 1] = copy_DB[j + 1], copy_DB[j]

    def __fix_size(self, DB):
        ln = len(DB)
        while ln > 25:
            del DB[0]
            return self.__fix_size(DB)

    def show_tab(self):
        copy_DB = self.__DB.copy()
        last = copy_DB[len(copy_DB) - 1]['time']
        self.__sort_db(copy_DB)
        choice = ['USER', 'AI']
        for i in range(len(copy_DB)):
            if len(copy_DB[i]["username"]) > 8:
                username = self.__maxlen_name(copy_DB[i]["username"])
            else: username = copy_DB[i]["username"]
            if copy_DB[i]["win"]:
                winner = choice[0]
            else: winner = choice[1]
            time.sleep(0.1)
            if copy_DB[i]['time'] == last:
                print(f'| '
                      f'{username :10}   '
                      f'size: {copy_DB[i]["size"] :2}   '
                      f'win: {winner :4}   '
                      f'score: {copy_DB[i]["score"] :5}')
            else:
                print(f'  '
                      f'{username :10} | '
                      f'size: {copy_DB[i]["size"] :2} | '
                      f'win: {winner :4} | '
                      f'score: {copy_DB[i]["score"] :5}')

    def __maxlen_name(self, text):
        text = text[:8] + '..'
        return text

    def save(self, filename):
        self.add_db(self.__DB)
        self.save_db(filename, self.__DB)


class SeaBatle:
    __CNT_TURN_USER = 0
    __CNT_TURN_AI = 0

    def __init__(self):
        self.size_board = self.__set_size()
        self.player = GamePole(size=self.size_board)
        self.comp = GamePole(size=self.size_board)
        self.player.init()
        self.comp.init()
        self.comp.hide = True
        self.ai = AI(self.comp, self.player)
        self.us = User(self.player, self.comp)
        self.statistic = Statistic(self.__set_username(), self.size_board)

    def __show_statistic(self):
        self.statistic.welcome('stat_db.json')
        time.sleep(1)
        self.statistic.show_tab()
        time.sleep(3)
        print('-' * 50)
        time.sleep(1)

    def __set_username(self):
        username = input('Enter username: ')
        print()
        return username

    def __head(self):
        print('-' * 50)
        print()
        seabatle = 'SEABATTLE _0.0.2'
        vs = '(user vs ai)'
        print(f' {seabatle :>31}\n{vs :>30}')
        print()
        print('-' * 50)

    def __set_size(self):
        self.__head()
        while True:
            size = input('Enter size board (8 - 12): ')
            if not size.isdigit():
                print('Not correct value')
                continue
            if int(size) not in range(8, 13):
                print('Not correct range')
                continue
            print('-' * 50)
            return int(size)

    @staticmethod
    def __rand_turn(size):
        text = 'Define first turn...'
        print('-' * 50)
        print(text.upper())
        print()
        for i in range(10):
            time.sleep(0.3)
            print(f'{i + 1 :>2}0 %')
        print('-' * 6)
        x = randint(0, 1)
        return x

    def __fill_mark(self):
        for x, y in self.comp._busy_shot:
            if x in range(self.ai.board._size) and y in range(self.ai.board._size):
                if self.ai.board._pole[y][x] != self.player.MARK_CELL_KILL:
                    self.ai.board._pole[y][x] = self.player.MARK_SHOT
        for ship in self.comp.get_ships():
            x = ship.get_start_coords()[0]
            y = ship.get_start_coords()[1]
            if ship._live == 0:
                if ship._tp == 1:
                    for i in range(ship._length):
                        contour = ship.contour([(x + i, y)])
                        self.comp._fill_contour(contour)
                if ship._tp == 2:
                    for i in range(ship._length):
                        contour = ship.contour([(x, y + i)])
                        self.comp._fill_contour(contour)

    def loop(self):
        self.__show_statistic()
        self.us.board.show()
        self.ai.board.show()
        n = self.__rand_turn(self.size_board)
        while True:
            if n % 2 == 0:
                print(f'USER {self.statistic.username} turn --> | cnt: {self.__CNT_TURN_USER}')
                repeat = self.us.turn()
                self.__CNT_TURN_USER += 1
                self.statistic.set_cnt_user(cnt=self.__CNT_TURN_USER)
            else:
                print(f'AI turn --> | cnt: {self.__CNT_TURN_AI}')
                time.sleep(randint(1, 3))
                repeat = self.ai.turn()
                self.__CNT_TURN_AI += 1
                self.statistic.set_cnt_ai(cnt=self.__CNT_TURN_AI)
            if repeat:
                n -= 1
            self.player.move_ships()
            self.comp.move_ships()
            # self.us.board.move_ships()
            # self.ai.board.move_ships()
            self.__fill_mark()
            self.us.board.show()
            self.ai.board.show()
            if self.ai.board.defeat():
                self.statistic.set_win(win=True)
                self.statistic.save('stat_db.json')
                print(f'USER {self.statistic.username} win!')
                print('-' * 50)
                self.statistic.show_tab()
                break
            if self.us.board.defeat():
                self.statistic.set_win(win=False)
                self.statistic.save('stat_db.json')
                print('AI win!')
                print('-' * 50)
                self.statistic.show_tab()
                break
            n += 1

            # print('-' * 30)
            # print('ships user:')
            # print(len(self.player.get_ships()))
            # for num, i in enumerate(self.player.get_ships()):
            #     print(f'- {str(num + 1).rjust(2, "0")} ln: {i._length} | '
            #           f'tp: {i._tp} | ({i._x}, {i._y}) | '
            #           f'cells: {i._cells} | move: {i._is_move}')
            #
            # print('-' * 30)
            # print('ships ai:')
            # print(len(self.comp.get_ships()))
            # for num, i in enumerate(self.comp.get_ships()):
            #     print(f'- {str(num + 1).rjust(2, "0")} ln: {i._length} | '
            #           f'tp: {i._tp} | ({i._x}, {i._y}) | '
            #           f'cells: {i._cells} | move: {i._is_move}')

    def start_game(self):
        self.loop()


batle = SeaBatle()
batle.start_game()

print('-' * 50)


# SIZE_GAME_POLE = 10

# pole = GamePole(SIZE_GAME_POLE)
# pole.init()
# pole.show()
# print()
# pole.move_ships()
# pole.show()


# print('-' * 30)
# print('ships:')
# for num, i in enumerate(pole.get_ships()):
#     print(f'- {str(num+1).rjust(2, "0")} ln: {i._length} | tp: {i._tp} | ({i._x}, {i._y}) | '
#           f'cells: {i._cells} | move: {i._is_move}')
#
# print('-' * 30)
# print('ships move:')
# for num, i in enumerate(pole.get_ships_move()):
#     print(f'- {str(num+1).rjust(2, "0")} ln: {i._length} | tp: {i._tp} | ({i._x}, {i._y}) | '
#           f'cells: {i._cells} | move: {i._is_move}')













