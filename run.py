from pokerl.game import Game, PokerMoves

game = Game(start_credits=100, num_players=4)
game.reset()
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

# No winner ...