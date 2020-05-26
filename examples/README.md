# Examples

In this folder there are a few examples that show how to use the pokerl library to train and test RL agents.

To run a test, make sure to set the project directory in `PYTHONPATH`, so that the interpreter can find the `pokerl` package.

`random_game.py`
-------------

In this example, 4 random agents play a single poker game.

`q_learning.py`
---------------

Example usage of the `pokerl.envs.PokerGameEnv`.

The RL algorithm used to train the agent is a stochastic flavour of Q-learning, that uses a numpy array to represent the Q-function and a softmax over the Q-values to represent the probability distribution of the policy.

The state consists only of the value of the player hand, i.e. a value in the range `[1, 9]` that indicates if the player has pair, straight, flush and so on.

`play_online.py`
----------------

This file contains both a server and a client implementation.

To launch the server, invoke the script with no argument:

```console
agent@pokerl:~$ python examples/play_online.py [--bind <host=localhost>[:<port=25560>]] [--num-players <N=4>]
```

To launch the client, pass at least the host of the server:

```console
agent@pokerl:~$ python examples/play_online.py <host>[:<port=25560>] [--agent <agent class or function>]
```

The `--agent` argument must point to a valid agent class or function. If not provided it defaults to `pokerl.agents.RandomAgent`. The agent `pokerl.agents.CLIAgent` can be used to play as a human.