from typing import Union, List, Tuple
from pokerl.enums import CardRank, CardSuit

class Card:
	""" A playing card """

	@property
	def rank(self) -> int:
		""" Returns the rank of the card
		
		The rank of an ace is 13 and not 0
		"""

		return (self.value & 0xf) or 13 # Make ace highest rank
	
	@property
	def suit(self) -> int:
		""" Returns the suit of the card """

		return self.value >> 4
	
	@property
	def id(self) -> int:
		""" Return a unique id in the range [0, 52) """

		return (self.value & 0xf) + (self.value >> 4) * 13
	
	def __init__(self, value: Union[int, str, Tuple[int]]):
		""" Constructs a new card
		
		Params
		------
		value : int, str or tuple of ints
			If `value` has type `int`, it is
			interpreted as `(suit << 4) |
			rank`;
			if `value` is a string, the first
			character is a rank symbol (e.g.
			'A', '2', '6', 'K', 'T', etc.)
			and the second character is a suit
			symbol (i.e. 'S', 'H', 'D' and 'C');
			If `value` is a tuple, the first
			value is the rank and the second
			value is the suit.
		"""
		
		if isinstance(value, tuple):
			# From (suit, rank) tuple
			rank, suit = value
			if rank == CardRank.ACE: rank = CardRank.ONE
			value = (suit << 4) | rank
		elif isinstance(value, str):
			# From 'RS' string
			rank, suit = CardRank.from_symbol[value[0]], CardSuit.from_symbol[value[1]]
			if rank == CardRank.ACE: rank = CardRank.ONE
			value = (suit << 4) | rank

		assert (value & 0xf) < CardRank.NUM_RANKS, 'Invalid card rank'
		assert (value >> 4) < CardSuit.NUM_SUITS, 'Invalid card suit'

		# Set value
		self.value = value
	
	def __repr__(self) -> str:
		""" Returns the unicode representation of the card
		
		See https://en.wikipedia.org/wiki/Playing_cards_in_Unicode#Playing_cards_deck
		"""
		
		if (self.value & 0xf) > CardRank.JACK:
			return chr(0x1f0a2 + self.value)
		else: return chr(0x1f0a1 + self.value)

def create_default_deck() -> List[Card]:
	"""  """

	return [Card((rank, suit)) for rank in range(CardRank.NUM_RANKS) for suit in range(CardSuit.NUM_SUITS)]