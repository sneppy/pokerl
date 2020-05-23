import random
from pokerl.cards import Card
from pokerl.judger import compare_hands, eval_hand
from timeit import default_timer as timer

cards = [Card((suit << 4) | rank) for rank in range(13) for suit in range(4)]
random.shuffle(cards)

shared = cards[6:11]

hands = [
	[*cards[0:2], *shared],
	[*cards[2:4], *shared],
	[*cards[4:6], *shared]
]

print(hands)

print(compare_hands(hands))