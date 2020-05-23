import random
import argparse
from pokerl.cards import Card, CardRank, CardSuit
from pokerl.judger import compare_hands, eval_hand
from timeit import default_timer as timer

parser = argparse.ArgumentParser('pokerl')
parser.add_argument('cards', nargs='+')
args = parser.parse_args()

cards = [Card((CardRank.from_symbol[card[0]], CardSuit.from_symbol[card[1]])) for card in args.cards]
print(cards)
print(eval_hand(cards))

exit(0)

cards = [Card((rank, suit)) for rank in range(13) for suit in range(4)]
random.shuffle(cards)

shared = cards[6:11]

hands = [
	[*cards[0:2], *shared],
	[*cards[2:4], *shared],
	[*cards[4:6], *shared]
]

print(hands)

print(compare_hands(hands))