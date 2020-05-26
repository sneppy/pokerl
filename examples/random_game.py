import sys
import logging
import numpy as np
from pokerl import Game

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

random_agent = lambda s: np.random.choice(list(s.valid_action_indices))
game = Game(num_players=4, start_credits=1000)
game.reset()

done = False
while not done: done, *_ = game.step(random_agent(game.active_state))