import sys
import logging
from pokerl.game import Game, PokerMoves

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

game = Game(start_credits=100, num_players=4)

game.reset()

for hand in range(5):
	game.step(PokerMoves.RAISE_QUARTER)
	game.step(PokerMoves.CALL)
	game.step(PokerMoves.FOLD)
	game.step(PokerMoves.CALL)

	game.step(PokerMoves.CALL)
	game.step(PokerMoves.CALL)
	game.step(PokerMoves.RAISE_TEN)
	game.step(PokerMoves.CALL)
	game.step(PokerMoves.FOLD)

	game.step(PokerMoves.CALL)
	game.step(PokerMoves.RAISE_TEN)
	game.step(PokerMoves.CALL)

	game.step(PokerMoves.CALL)
	game.step(PokerMoves.CALL)

# No winner ...