print('Первая координата по горизонтали')


# рисуем игровое поле
field = [['-', '-', '-'],
         ['-', '-', '-'],
         ['-', '-', '-']]

def draw_field(field):
    print('-' * 12)
    
    print(' ', '1', '2', '3')
    for i, num in enumerate(range(1, 4)):
        print(num, ' '.join(field[i]))

    print('-' * 12)



# проверка на корректность ввода
# проверить входит ли в нужный диапазон введенная координата
# проверить свободна ли ячейка
# вернуть правильную координату
def get_input(field):
    x_id = 0
    y_id = 0
    while True:
        turn = input('Ваш ход: ')
        if len(turn) != 2:
            print('Слишком много или слишком мало введено')
            continue
        if turn.isalpha():
            print('Не корректный ввод')
            continue

        coord = [i for i in turn]
        if int(coord[0]) not in range(4) or int(coord[1]) not in range(4):
            print('Не правильные координаты')
            continue
        
        x_id = int(coord[0])-1
        y_id = int(coord[1])-1

        if field[y_id][x_id] == '-':
            break
        else:
            print('Ячейка занята')
    return x_id, y_id


# если не осталось не занятых ячеек, то ничья
def not_win(field):
    count = 0
    for i in range(3):
        if '-' in field[i]:
            count += 1
    return count == 1


# проверить по x и y на наличие символа оппонента и на заполненность ячейки
# таже самая проверка по диагоналям
def check_win(field):
    for y in range(3):
        if '-' not in field[y] and token[0] not in field[y] and token[1] in field[y]:
            return True
        if '-' not in field[y] and token[1] not in field[y] and token[0] in field[y]:
            return True
    for x in range(3):
        line = [field[0][x], field[1][x], field[2][x]]
        if '-' not in line and token[0] not in line and token[1] in line:
            return True
        if '-' not in line and token[1] not in line and token[0] in line:
            return True
            
    diag = [field[0][0], field[1][1], field[2][2]]
    if '-' not in diag and token[0] not in diag and token[1] in diag:
            return True
    if '-' not in diag and token[1] not in diag and token[0] in diag:
            return True
    diag = [field[0][2], field[1][1], field[2][0]]
    if '-' not in diag and token[0] not in diag and token[1] in diag:
            return True
    if '-' not in diag and token[1] not in diag and token[0] in diag:
            return True

    return False


token = 'XO'

    
def loop(field):
    n = 0
    while True:
        
        draw_field(field)
        
        if not_win(field):
            print('Ничья')
            break

        n += 1
        x, y = get_input(field)
        if n % 2 == 1:
            field[y][x] = token[0]
        if n % 2 == 0:
            field[y][x] = token[1]
        
        if check_win(field):
            
            draw_field(field)
            
            if n % 2 == 1:
                print('Победа', token[0])
            if n % 2 == 0:
                print('Победа', token[1])
            break

loop(field)
