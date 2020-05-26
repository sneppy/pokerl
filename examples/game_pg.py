import sys
import time
import logging
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
from pokerl import Game
from pokerl.envs import PokerGameEnv, PokerEnv
from pokerl.judger import eval_hand
from pokerl.enums import PokerMoves

# Avoids `probabilities do not sum to 1` error
tf.keras.backend.set_floatx("float64")

#logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def random_agent(state: Game.StateView) -> int:
	"""  """

	actions = state.valid_action_indices
	return np.random.choice(list(actions))

env = PokerGameEnv([random_agent, random_agent, random_agent], num_players=4)
eval_env = PokerGameEnv([random_agent, random_agent, random_agent], num_players=4)
num_features = 5
num_actions = PokerMoves.NUM_MOVES

def get_state(state: Game.StateView) -> tuple:
	"""  """

	s = np.zeros((num_features,))
	h = state.player_hand
	r, _ = eval_hand(h)
	
	s[0] = r * 0.1
	s[1] = state.credit
	s[2] = state.bets[state.player]
	s[3] = state.high_bet
	s[4] = state.pot

	return s, state.valid_actions

def create_net():
	"""  """

	state = keras.layers.Input((num_features,))
	valid = keras.layers.Input((num_actions,))

	hidden = keras.layers.Dense(64, activation="tanh")(state)
	hidden = keras.layers.Dense(64, activation="tanh")(state)
	hidden = keras.layers.Dense(64, activation="tanh")(hidden)

	logits = keras.layers.Dense(num_actions)(hidden)

	values = keras.layers.Softmax()(logits)
	values = keras.layers.Multiply()([values, valid])
	values = keras.layers.Lambda(lambda x: x / keras.backend.sum(x))(values)
	
	return keras.Model(inputs=(state, valid), outputs=values)

def probs(pi, s, v):
	"""  """

	s = tf.convert_to_tensor(s)
	v = tf.convert_to_tensor(v)

	if keras.backend.ndim(s) == 1:
		s = tf.reshape(s, (1, -1))
		v = tf.reshape(v, (1, -1))
		p = pi((s, v))
		return tf.reshape(p, (-1,))
	else:
		return pi((s, v))

def policy_gradient(pi, opt, trajectories, gamma, step=0):
	"""  """

	num_trajectories = tf.constant(len(trajectories), dtype=tf.float64)

	with tf.GradientTape(watch_accessed_variables=False) as tape:
		tape.watch(pi.trainable_variables)
		J = 0

		# s : states
		# v : valid actions
		# u : actions
		# r : rewards
		for s, v, u, r, in trajectories:
			# Compute return values
			discount = tf.constant(gamma, dtype=tf.float64) ** tf.range(len(s), dtype=tf.float64)
			values = tf.cumsum(tf.reverse(r * discount, (0,)))
			values = tf.reverse(values, (0,))
			
			p = probs(pi, s, v)
			J += -tf.reduce_sum(tf.gather(p, u, axis=1, batch_dims=1) * values)
		
		J /= num_trajectories
	
	# Compute gradients
	grads = tape.gradient(J, pi.trainable_variables)
	opt.apply_gradients(zip(grads, pi.trainable_variables))

def evaluate(env: PokerEnv, agent, num_episodes: int=100):
	"""  """

	h = np.zeros((num_episodes,))
	for episode in range(num_episodes):
		R = []
		s = env.reset()
		done = False
		while not done:
			u = agent(s)
			s, r, done = env.step(u)
			R.append(r)
		
		score = np.mean(R)
		h[episode] = score
	
	return np.mean(h), h

timestamp = int(time.time())
test_logger = tf.summary.create_file_writer(f'.logs/game/pg/{timestamp}')

num_steps = 1000000
update_after = 10000
eval_after = 1000
eval_n = 50

s, v = get_state(env.reset())
pi = create_net()
pi.summary()
opt = keras.optimizers.Adam(learning_rate=0.01)
gamma = 1.0
trajectories = []
trajectory = []

for step in range(num_steps):

	# Draw action
	p = probs(pi, s, v)
	u = np.random.choice(len(p), p=p)

	# Step
	ns, r, done = env.step(u)
	trajectory.append((s, v, u, r))

	# PG update
	if step > 0 and step % update_after == 0:
		policy_gradient(pi, opt, trajectories, gamma, step)
		trajectories = []

	# Evaluate
	if step > 0 and step % eval_after == 0:
		score, _ = evaluate(eval_env, lambda s: np.random.choice(num_actions, p=probs(pi, *get_state(s))), num_episodes=eval_n)
		print("score: ", score)

		with test_logger.as_default(): tf.summary.scalar('score', score, step=step)
	
	if done:
		trajectory = [np.array([t[i] for t in trajectory]) for i in range(4)]
		trajectories.append(trajectory)
		trajectory = []
		s, v = get_state(env.reset())
	else: s, v = get_state(ns)