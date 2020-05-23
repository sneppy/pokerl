from itertools import islice
from .enums import HandRanking

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

		straight = 0
		flush = 0
		both = 0
		kind = 0
		fourakind = []
		threeakind = []
		twoakind = []
		for rank, suit in zip(rank_sorted, suit_sorted):			
			# This block checks flush and straight flush
			if suit.suit == (flush & 0xf):
				flush += 0x100
				if suit.rank + (flush >> 4 & 0xf) == (flush >> 8): both += 0x100
			elif (flush >> 8) < 5:
				flush = 0x100 | (suit.rank << 4) | suit.suit
				both = flush
			
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
		else: return HandRanking.HIGH, (c.rank for c in rank_sorted[:5])

def compare_hands(hands) -> list:
	"""  """
	
	hand_rankings = [eval_hand(hand) for hand in hands]	
	return hand_rankings