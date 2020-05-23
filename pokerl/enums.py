class HandRanking:
	"""  """

	STRAIGHT_FLUSH = 1
	POKER = 2
	FULL = 3
	FLUSH = 4
	STRAIGHT = 5
	TRIS = 6
	TWO_PAIR = 7
	PAIR = 8
	HIGH = 9
	NONE = 10

	as_string = [
		'Five of a kind',
		'Straight flush',
		'Four of a kind',
		'Full house',
		'Flush',
		'Straight',
		'Three of a kind',
		'Two pair',
		'One pair',
		'High card'
	]

class CardSuit:
	"""  """

	SPADES = 0x0
	HEARTS = 0x1
	DIAMONDS = 0x2
	CLUBS = 0x3

	NUM_SUITS = 4

	as_string = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
	as_symbol = ['\u2660', '\u2665', '\u2666' '\u2663']

	from_symbol = {
		'S': SPADES,
		'H': HEARTS,
		'D': DIAMONDS,
		'C': CLUBS,
	}

class CardRank:
	"""  """

	ONE = 0x0
	TWO = 0x1
	THREE = 0x2
	FOUR = 0x3
	FIVE = 0x4
	SIX = 0x5
	SEVEN = 0x6
	EIGHT = 0x7
	NINE = 0x8
	TEN = 0x9
	JACK = 0xa
	QUEEN = 0xb
	KING = 0xc
	ACE = 0xd

	NUM_RANKS = 14

	as_string = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace']
	as_symbol = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

	from_symbol = {
		'1': ONE,
		'2': TWO,
		'3': THREE,
		'4': FOUR,
		'5': FIVE,
		'6': SIX,
		'7': SEVEN,
		'8': EIGHT,
		'9': NINE,
		'T': TEN,
		'J': JACK,
		'Q': QUEEN,
		'K': KING,
		'A': ACE
	}