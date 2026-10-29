from random import choice


val = 21
start = val if val == 21 else val + 1
target = choice([x for x in range(start, 22)])

print(target)























