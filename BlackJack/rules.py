class Credit:
    def __str__(self):
        text = 'CREDIT\n'
        text += '  bank loan: 100 - debt repayment 100%\n'
        text += '  bank loan: 500 - debt repayment 25%\n'
        text += '  bank loan: 1000 - debt repayment 10%'
        return f'{text}'


class Bet:
    def __str__(self):
        text = 'BET\n'
        text += '  write the bet "all-in": allin or all\n'
        return f'{text}'


class BlackJack:
    def __str__(self):
        text = 'BLACKJACK\n'
        text += '  if first deal of cards - blackjack: ' \
                '\n  returns a 200% from the bet'
        return f'{text}'


class CardsCollectUpdate:
    def __str__(self):
        text = 'CARDS DECK UPDATE\n'
        text += '  collection update: when is left < 25%'
        return f'{text}'














