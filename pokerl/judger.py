from typing import List, Tuple
from itertools import islice
from functools import reduce
from .cards import Card
from .enums import HandRanking, CardRank, CardSuit

def eval_hand(hand: List[Card]) -> Tuple[int, List[int]]:
	""" Evaluate hand of cards

	Params
	------
	hand : list of cards
		Up to seven cards to evaluate
		as a poker hand.
	
	Returns
	-------
	tuple
		A tuple where the first item
		is the hand ranking, as in
		HandRanking enum, and the second
		is a list of kickers used to
		break ties. The number of kickers
		depends on the type of hand; for
		instance, only one kicker is
		returned for a straight, and five
		are returned for a flush.
	"""

	if not hand: return HandRanking.NONE, []
	elif len(hand) == 1: return HandRanking.HIGH, [hand[0].rank]
	elif len(hand) == 2:
		first, second = hand
		if first.rank == second.rank: return HandRanking.PAIR, [first.rank]
		else: return HandRanking.HIGH, [max(first.rank, second.rank), min(first.rank, second.rank)]
	else:
		# Sort by rank
		rank_sorted = sorted(hand, key=lambda c: c.rank, reverse=True)
		suit_sorted = sorted(hand, key=lambda c: (c.suit << 4) | c.rank, reverse=True)

		idx = 0
		flush = CardSuit.NUM_SUITS
		both = CardSuit.NUM_SUITS
		kind = 0
		straight = 0
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
			elif (flush >> 8) < 5: both = flush = 0x100 | (suit.rank << 4) | suit.suit; flush_start = idx
			
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
			
			idx += 1
		
		# Check last kind
		numakind = kind >> 4
		if numakind == 2: twoakind.append(kind & 0xf)
		elif numakind == 3: threeakind.append(kind & 0xf)
		elif numakind == 4: fourakind.append(kind & 0xf)

		# Handle special case of 5-A straight
		if (both >> 8) == 4 and (both >> 4 & 0xf) == CardRank.FIVE:
			ace = next((True for c in hand if c.rank == CardRank.ACE and c.suit == (both & 0xf)), False)
			if ace: return HandRanking.STRAIGHT_FLUSH, [CardRank.FIVE]
		elif (straight >> 4) == 4 and (straight & 0xf) == CardRank.FIVE:
			ace = next((True for c in hand if c.rank == CardRank.ACE), False)
			if ace: return HandRanking.STRAIGHT, [CardRank.FIVE]
		
		if (both >> 8) >= 5: return HandRanking.STRAIGHT_FLUSH, [both >> 4 & 0xf]
		elif fourakind: return HandRanking.POKER, [fourakind[0], *islice((c.rank for c in rank_sorted if c.rank != fourakind[0]), 1)]
		elif len(threeakind) > 1: return HandRanking.FULL, [threeakind[0], threeakind[1]]
		elif threeakind and twoakind: return HandRanking.FULL, [threeakind[0], twoakind[0]]
		elif (flush >> 8) >= 5: return HandRanking.FLUSH, [c.rank for c in suit_sorted[flush_start:flush_start + 5]]
		elif (straight >> 4) >= 5: return HandRanking.STRAIGHT, [straight & 0xf]
		elif threeakind: return HandRanking.TRIS, [threeakind[0], *islice((c.rank for c in rank_sorted if c.rank != threeakind[0]), 2)]
		elif len(twoakind) > 1: return HandRanking.TWO_PAIR, [twoakind[0], twoakind[1], *islice((c.rank for c in rank_sorted if c.rank != twoakind[0] and c.rank != twoakind[1]), 1)]
		elif twoakind: return HandRanking.PAIR, [twoakind[0], *islice((c.rank for c in rank_sorted if c.rank != twoakind[0]), 3)]
		else: return HandRanking.HIGH, [c.rank for c in rank_sorted[:5]]

def get_kickers_value(kickers) -> int:
	""" Returns the kickers value as a bit-packed integer
	
	For instance, the kickers `[9, 8, 3]`
	are returned as `(9 << 8) | (8 << 4)
	| 3`
	"""

	return reduce(lambda value, kicker: value | (kicker[1] << (kicker[0] << 2)), enumerate(reversed(kickers)), 0)

def compare_rankings(rankings: List[Tuple[int, List[int]]]) -> Tuple[List[int], List[int], Tuple[int, List[int]]]:
	""" Compares multiple hands
	
	Returns the winner and the
	rankings of each hand

	Params
	------
	`rankings` : list of hand rankings
		A list of hand rankings with
		kickers, as output by `eval_hand`
	
	Returns
	-------
	tuple
		Returns a tuple where:
		- the first element is a one-hot
			encoded array of the winners;
		- the second element is a list
			with the indices of the winner.
	"""

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

	onehot = [int(idx in winners) for idx, _ in enumerate(rankings)]
	return onehot, winners

def compare_hands(hands: List[List[Card]]) -> Tuple[List[int], List[int], Tuple[int, List[int]]]:
	""" Compares multiple hands
	
	Returns the winner and the
	rankings of each hand

	Params
	------
	`hand` : list of hands
		A list of lists of cards, one for
		each player to compare. Ideally they
		should all have the same number of
		cards
	
	Returns
	-------
	tuple
		Returns a tuple where:
		- the first element is a one-hot
			encoded array of the winners;
		- the second element is a list
			with the indices of the winner;
		- the last element is a list of
			hand rankings, as output by
			the `eval_hand` function, one
			for each hand.
	"""

	rankings = [eval_hand(hand) for hand in hands]
	return compare_rankings(rankings) + (rankings,)