import numpy as np
from pokerl import Game, eval_hand
from pokerl.envs import PokerGameEnv
from pokerl.agents import RandomAgent
from pokerl.enums import PokerMoves, HandRanking

# Set numpy print options
np.set_printoptions(precision=3, suppress=True, linewidth=np.inf)

# Define the softmax function
def softmax(x: np.ndarray) -> np.ndarray:
	""" Computes the softmax of `x` """

	exp = np.exp(x)
	return exp / np.sum(exp)

# Train against random agents
num_opponents = 3
env = PokerGameEnv(agents=[RandomAgent() for _ in range(num_opponents)], num_players=num_opponents + 1)
eval_env = PokerGameEnv(agents=[RandomAgent() for _ in range(num_opponents)], num_players=num_opponents + 1)

# Very simple Q-learning; uses hand
# ranking as feature and Q softmax
# probabilities for exploration
num_states = HandRanking.NONE
num_actions = PokerMoves.NUM_MOVES
Q = np.zeros((num_states, num_actions), dtype=np.float64)

def get_state(state: Game.StateView) -> int:
	""" Extract agent state from game state """

	ranking, _ = eval_hand(state.player_hand)
	return ranking, list(state.valid_action_indices)

def predict(Q: np.ndarray, s: np.ndarray, v: np.ndarray) -> int:
	""" Predict an action for the given state """

	# Extract state and compute probabilities
	# of valid actions
	p = softmax(Q[s, v])
	return np.random.choice(v, p=p)

def eval_agent(env: PokerGameEnv, agent, num_games=10):
	""" Simple script to evaluate the agent """

	h = np.zeros((num_games,))
	for game in range(num_games):
		R = []
		s = env.reset()
		done = False
		while not done:
			# Predict and perform action
			u = agent(s)
			s, r, done, _ = env.step(u)
			R.append(r)
		
		# Compute game score
		h[game] = np.sum(R)
	
	return np.mean(h), h

# Learning parameters
num_steps = 100000
gamma = 1.0
alpha = 0.01
eval_after = 10000
eps = lambda step: 1 - (step / num_steps) ** 2

s, v = get_state(env.reset())
for step in range(num_steps):
	# Evaluate agent
	if step % eval_after == 0:
		#print('fold', Q[:, PokerMoves.FOLD])
		#print('all-in', Q[:, PokerMoves.ALL_IN])
		print('high-card', Q[HandRanking.HIGH, :])
		print('two-pair', Q[HandRanking.TWO_PAIR, :])
		print('full', Q[HandRanking.FULL, :])
		score, _ = eval_agent(eval_env, lambda s: predict(Q, *get_state(s)), num_games=200)
		print('score', score)

	# Predict action, observe new state and reward
	if np.random.uniform() < eps(step): u = np.random.choice(v)
	else: u = predict(Q, s, v)
	ns, r, done, hand = env.step(u)
	ns, nv = get_state(ns)

	# Update Q values
	td_target = r + (1 - hand) * gamma * np.max(Q[ns, nv])
	Q[s, u] += alpha * (td_target - Q[s, u])

	# Reset env if done
	if done: s, v = get_state(env.reset())
	else: s, v = ns, nv

# Final evaluation
score, _ = eval_agent(eval_env, lambda s: predict(Q, *get_state(s)), num_games=500)
print('final score', score)