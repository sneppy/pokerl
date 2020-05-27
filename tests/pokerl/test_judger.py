import unittest
from pokerl.cards import Card
from pokerl.judger import eval_hand, compare_hands
from pokerl.enums import CardRank, CardSuit, HandRanking

def create_hand(*symbols):
	"""  """

	return [Card(sym) for sym in symbols]

class TestJudger(unittest.TestCase):

	def test_eval_hand(self):
		""" Test hand evaluation """
		
		out = eval_hand(create_hand("2C", "3C", "4C", "5C", "6C", "7C", "8C"))
		self.assertEqual(out, (HandRanking.STRAIGHT_FLUSH, [CardRank.EIGHT]))

		out = eval_hand(create_hand("1D", "2D", "3D", "4D", "5D", "6C", "7C"))
		self.assertEqual(out, (HandRanking.STRAIGHT_FLUSH, [CardRank.FIVE]))

		out = eval_hand(create_hand("1D", "2D", "3D", "4D", "8D", "6C", "7C"))
		self.assertEqual(out, (HandRanking.FLUSH, [CardRank.ACE, CardRank.EIGHT, CardRank.FOUR, CardRank.THREE, CardRank.TWO]))

		out = eval_hand(create_hand("1D", "3D", "5H", "7H", "7S", "9S", "JS"))
		self.assertEqual(out, (HandRanking.PAIR, [CardRank.SEVEN, CardRank.ACE, CardRank.JACK, CardRank.NINE]))

		out = eval_hand(create_hand("1D", "3D", "5H", "8H", "7S", "9S", "1S"))
		self.assertEqual(out, (HandRanking.PAIR, [CardRank.ACE, CardRank.NINE, CardRank.EIGHT, CardRank.SEVEN]))

		out = eval_hand(create_hand("1D", "1C", "5H", "6H", "6H", "TS", "TS"))
		self.assertEqual(out, (HandRanking.TWO_PAIR, [CardRank.ACE, CardRank.TEN, CardRank.SIX]))

		out = eval_hand(create_hand("KD", "QC", "JH", "TH", "9H", "9S", "9D"))
		self.assertEqual(out, (HandRanking.STRAIGHT, [CardRank.KING]))

		out = eval_hand(create_hand("KD", "QC", "JH", "TH", "9H", "5S", "9D"))
		self.assertEqual(out, (HandRanking.STRAIGHT, [CardRank.KING]))

		out = eval_hand(create_hand("KD", "QC", "JH", "TH", "9H", "5S", "7D"))
		self.assertEqual(out, (HandRanking.STRAIGHT, [CardRank.KING]))

		out = eval_hand(create_hand("8D", "9C", "7H", "6H", "9H", "5S", "7D"))
		self.assertEqual(out, (HandRanking.STRAIGHT, [CardRank.NINE]))

		out = eval_hand(create_hand("2H", "3C", "4H", "5H", "6H", "7H", "8D"))
		self.assertEqual(out, (HandRanking.FLUSH, [CardRank.SEVEN, CardRank.SIX, CardRank.FIVE, CardRank.FOUR, CardRank.TWO]))

		out = eval_hand(create_hand("8D", "8C", "8H", "5H", "5S", "5D", "3D"))
		self.assertEqual(out, (HandRanking.FULL, [CardRank.EIGHT, CardRank.FIVE]))

		out = eval_hand(create_hand("8D", "8C", "8H", "5H", "5S", "4D", "3D"))
		self.assertEqual(out, (HandRanking.FULL, [CardRank.EIGHT, CardRank.FIVE]))

		out = eval_hand(create_hand("1D", "1C", "1H", "5H", "5S", "5D", "5C"))
		self.assertEqual(out, (HandRanking.POKER, [CardRank.FIVE, CardRank.ACE]))

		out = eval_hand(create_hand("1D", "1C", "1H", "1S", "KS", "KD", "KC"))
		self.assertEqual(out, (HandRanking.POKER, [CardRank.ACE, CardRank.KING]))

		out = eval_hand(create_hand("2D", "3D", "4D", "5D", "7D", "6C", "KC"))
		self.assertEqual(out, (HandRanking.FLUSH, [CardRank.SEVEN, CardRank.FIVE, CardRank.FOUR, CardRank.THREE, CardRank.TWO]))

		out = eval_hand(create_hand("2D", "3C", "4D", "5D", "8D", "JC", "KC"))
		self.assertEqual(out, (HandRanking.HIGH, [CardRank.KING, CardRank.JACK, CardRank.EIGHT, CardRank.FIVE, CardRank.FOUR]))

		out = eval_hand(create_hand("2D", "2C", "3D", "3D", "JD", "JC", "KC"))
		self.assertEqual(out, (HandRanking.TWO_PAIR, [CardRank.JACK, CardRank.THREE, CardRank.KING]))

		out = eval_hand(create_hand("2D", "2C", "3D", "3D", "JD", "JC", "JC"))
		self.assertEqual(out, (HandRanking.FULL, [CardRank.JACK, CardRank.THREE]))

		out = eval_hand(create_hand("2D", "2C", "3D", "3D", "3D", "JC", "JC"))
		self.assertEqual(out, (HandRanking.FULL, [CardRank.THREE, CardRank.JACK]))

		out = eval_hand(create_hand("KC", "QC", "JC", "TC", "9C", "AD", "4D"))
		self.assertEqual(out, (HandRanking.STRAIGHT_FLUSH, [CardRank.KING]))

		out = eval_hand(create_hand("9D", "8C", "4D", "5D", "6D", "JD", "KC"))
		self.assertEqual(out, (HandRanking.FLUSH, [CardRank.JACK, CardRank.NINE, CardRank.SIX, CardRank.FIVE, CardRank.FOUR]))

	def test_compare_hands(self):
		""" Test the hand compare function """

		h1 = create_hand("1D", "1C", "1H", "5H", "6H",  "1S", "KS")
		h2 = create_hand("1D", "1C", "1H", "5H", "6H",  "QS", "JS")
		out = compare_hands([h1, h2])
		self.assertEqual(out[0], [1, 0])

		h1 = create_hand("1D", "1C", "1H", "5H", "6H", "1S", "KS")
		h2 = create_hand("1D", "1C", "1H", "5H", "6H", "QH", "JH")
		out = compare_hands([h1, h2])
		self.assertEqual(out[0], [1, 0])

		h1 = create_hand("1D", "1C", "1H", "2H", "3H", "1S", "KS")
		h2 = create_hand("1D", "1C", "1H", "2H", "3H", "4H", "5H")
		out = compare_hands([h1, h2])
		self.assertEqual(out[0], [0, 1])

		h1 = create_hand("1D", "3C", "5H", "7H", "9H", "KS", "JS")
		h2 = create_hand("1D", "3C", "5H", "7H", "9H", "QS", "TS")
		out = compare_hands([h1, h2])
		self.assertEqual(out[0], [1, 0])

		h1 = create_hand("1D", "3C", "5H", "7H", "9H", "KS", "JS")
		h2 = create_hand("1D", "3C", "5H", "7H", "9H", "QS", "TS")
		out = compare_hands([h1, h2])
		self.assertEqual(out[0], [1, 0])

		h1 = create_hand("1D", "3C", "5H", "7H", "9H", "KS", "JS")
		h2 = create_hand("1D", "3C", "5H", "7H", "9H", "3S", "TS")
		out = compare_hands([h1, h2])
		self.assertEqual(out[0], [0, 1])

		h1 = create_hand("1D", "3C", "5H", "7H", "9H", "1S", "9D")
		h2 = create_hand("1D", "3C", "5H", "7H", "9H", "7S", "7S")
		h3 = create_hand("1D", "3C", "5H", "7H", "9H", "9S", "9S")
		out = compare_hands([h1, h2, h3])
		self.assertEqual(out[0], [0, 0, 1])

if __name__ == '__main__':
	# Run tests
	unittest.main()