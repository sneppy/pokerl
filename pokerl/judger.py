from itertools import islice
from functools import reduce
from .enums import HandRanking, CardRank, CardSuit

def eval_hand(hand) -> int:
	"""  """

	if len(hand) == 1: return HandRanking.HIGH, [hand[0].rank]
	else:
		# Sort by rank
		rank_sorted = sorted(hand, key=lambda c: c.rank, reverse=True)
		suit_sorted = sorted(hand, key=lambda c: (c.suit << 4) | c.rank, reverse=True)

		# TODO: Here's the special case where
		# the ace is actually the lowest
		# card in a straight, e.g. 5, 4,
		# 3, 2, 1

		#print(rank_sorted)
		#print(suit_sorted)

		flush = CardSuit.NUM_SUITS
		both = CardSuit.NUM_SUITS
		kind = CardRank.NUM_RANKS
		straight = CardRank.NUM_RANKS
		fourakind = []
		threeakind = []
		twoakind = []
		for rank, suit in zip(rank_sorted, suit_sorted):			
			# This block checks flush and straight flush
			if suit.suit == (flush & 0xf):
				flush += 0x100

				# Check straigth flush
				if suit.rank + (both >> 8) == (both >> 4 & 0xf): both += 0x100
				else: both = 0x100 | (suit.rank << 4) | suit.suit
			elif (flush >> 8) < 5: both = flush = 0x100 | (suit.rank << 4) | suit.suit
			
			# This block checks N of a kind and straights
			if rank.rank == (kind & 0xf): kind += 0x10
			else:
				# Save as pair, tris or poker
				numakind = kind >> 4
				if numakind == 2: twoakind.append(kind & 0xf)
				elif numakind == 3: threeakind.append(kind & 0xf)
				elif numakind == 4: fourakind.append(kind & 0xf)

				# Reset kind and check straight
				kind = 0x10 | rank.rank
				if rank.rank + (straight >> 4) == (straight & 0xf): straight += 0x10
				elif (straight >> 4) < 5: straight = 0x10 | rank.rank
		
		# Check last kind
		numakind = kind >> 4
		if numakind == 2: twoakind.append(kind & 0xf)
		elif numakind == 3: threeakind.append(kind & 0xf)
		elif numakind == 4: fourakind.append(kind & 0xf)

		if (both >> 8) >= 5: return HandRanking.STRAIGHT_FLUSH, [both >> 4 & 0xf]
		elif fourakind: return HandRanking.POKER, [fourakind[0], next(c.rank for c in rank_sorted if c.rank != fourakind[0])]
		elif threeakind and twoakind: return HandRanking.FULL, [threeakind[0], twoakind[0]]
		elif (flush >> 8) >= 5: return HandRanking.FLUSH, [flush >> 4 & 0xf]
		elif (straight >> 8) >= 5: return HandRanking.STRAIGHT, [straight & 0xf]
		elif threeakind: return HandRanking.TRIS, [threeakind[0], *islice((c.rank for c in rank_sorted if c.rank != threeakind[0]), 2)]
		elif len(twoakind) > 1: return HandRanking.TWO_PAIR, [twoakind[0], twoakind[1], next(c.rank for c in rank_sorted if c.rank != twoakind[0] and c.rank != twoakind[1])]
		elif twoakind: return HandRanking.PAIR, [twoakind[0], *islice((c.rank for c in rank_sorted if c.rank != twoakind[0]), 3)]
		else: return HandRanking.HIGH, [c.rank for c in rank_sorted[:5]]

def compare_hands(hands) -> list:
	"""  """

	def get_kickers_value(kickers):
		"""  """

		return reduce(lambda value, kicker: value | (kicker[1] << (kicker[0] << 2)), enumerate(reversed(kickers)), 0)

	rankings = [eval_hand(hand) for hand in hands]

	winners = []
	best_rank = HandRanking.NONE
	best_kicker = 0
	idx = 0

	for rank, kickers in rankings:
		kicker = get_kickers_value(kickers)
		if rank < best_rank:
			# Flush winners
			best_rank = rank
			best_kicker = kicker
			winners = [idx]
		elif rank == best_rank:
			if kicker > best_kicker:
				# Flush winners
				kicker = best_kicker
				winners = [idx]
			elif kicker == best_kicker:
				# Add winner
				winners.append(idx)
		
		# Next hand
		idx += 1

	onehot = [int(idx in winners) for idx in range(len(hands))]
	return onehot, winners, rankings