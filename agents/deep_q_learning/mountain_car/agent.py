import time
import random
import logging
import sys
import os
from pathlib import Path
from collections import deque

SCRIPT_DIR = Path(os.path.abspath(sys.argv[0]))
sys.path.append(str(SCRIPT_DIR.parent.parent.parent.parent))

import gym
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.layers import Dense


logger = logging.getLogger()
logging.getLogger("tensorflow").setLevel(logging.ERROR)


class DQNModel(Model):

    def __init__(self, layer_size: int, output_size: int, learning_rate: float):
        super(DQNModel, self).__init__()
        self.layer_size = layer_size
        self.output_size = output_size
        self.learning_rate = learning_rate
        self.d1 = Dense(layer_size, activation='relu')
        self.d2 = Dense(layer_size, activation='relu')
        self.output_layer = Dense(output_size, activation=None)
        self.loss_object = tf.keras.losses.MeanSquaredError()
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

    @tf.function
    def call(self, inputs, training=None, mask=None):
        x = self.d1(inputs)
        x = self.d2(x)
        x = self.output_layer(x)
        return x

    def get_config(self):
        return {"layer_size": self.layer_size,
                "output_size": self.output_size,
                "learning_rate": self.learning_rate}

    @tf.function
    def train_step(self, inputs, labels):
        # logger.info("Training function")
        with tf.GradientTape() as tape:
            predictions = self(inputs)
            loss = self.loss_object(labels, predictions)
        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))


class MountainCarAgent(object):

    def __init__(self, replay_memory_size: int, layer_size: int,
                 min_replay_memory_size: int, learning_rate: float,
                 batch_size: int, update_target_every: int):

        self.env = gym.make("MountainCar-v0")
        self.env.reset()
        self.action_space = self.env.action_space.n
        self.state_space = self.env.observation_space.shape[0]

        self.model = DQNModel(layer_size=layer_size, output_size=self.action_space,
                              learning_rate=learning_rate)
        self.model.build((None, self.state_space))
        self.model.summary(print_fn=lambda x: logger.info(x))
        self.target_model = DQNModel(layer_size=layer_size, output_size=self.action_space,
                                     learning_rate=learning_rate)
        self.target_model.build((None, self.state_space))
        self.target_model.set_weights(self.model.get_weights())

        self.replay_memory = deque(maxlen=replay_memory_size)
        self.min_replay_memory_size = min_replay_memory_size
        self.batch_size = batch_size
        self.target_update_counter = 0
        self.update_target_every = update_target_every

    def produce_action(self, state: tuple):
        q_values = self.get_q_values(state)
        action = np.argmax(q_values)
        return action

    def get_q_values(self, state: tuple):
        return self.model(np.array([state]))

    # Adds step's data to a memory replay array
    # (state, action, reward, new_state, done)
    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    def train_agent(self, episodes: int=25000, epsilon: float=1, plot_game: bool=False,
                    show_every: int=None, save_model: Path=None, discount: float=0.95,
                    cycles: int=1):

        episodes_counter = 0
        episodes_wins = []
        episodes_rewards = []
        epsilon_min = 0.01
        epsilon_decay_value = 0.01
        if show_every is None:
            show_every = episodes

        logger.info("#### Starting training ####")
        start_time = time.time()
        for cycle in range(cycles):
            current_epsilon = epsilon
            for episode in range(episodes):
                self.env.reset()
                done = False
                show = False
                episode_reward = 0
                current_epsilon = max(epsilon_min, current_epsilon)

                if episode + (cycle * episodes) > 0:
                    if not (episode + (cycle * episodes)) % show_every:
                        logger.info(f"Showing episode N° {episode} of cycle {cycle}")
                        logger.info(f"Batch time = {time.time() - start_time} sec")
                        logger.info(f"Epsilon is {current_epsilon}")
                        logger.info(f"Last {show_every} episodes reward mean: "
                                    f"{np.mean(episodes_rewards[-show_every:])}")
                        batch_wins = np.sum(episodes_wins[-show_every:])
                        logger.info(f"Wins in last {show_every} episodes = {batch_wins}")
                        show = True
                        start_time = time.time()
                    else:
                        show = False

                while not done:

                    if show and plot_game:
                        self.env.render()

                    state = self.env.state
                    if np.random.random() > current_epsilon:
                        action = self.produce_action(state)
                    else:
                        action = np.random.randint(0, self.env.action_space.n)
                    new_state, reward, done, _ = self.env.step(action)

                    # Every step we update replay memory and train main network
                    self.update_replay_memory((state, action, reward, new_state, done))
                    self.training_step(discount)

                    if done:
                        if new_state[0] >= self.env.goal_position:
                            episodes_wins.append(True)
                        else:
                            episodes_wins.append(False)
                        self.target_update_counter += 1

                    # If counter reaches set value, update target network with weights of main network
                    if self.target_update_counter % self.update_target_every == 0 and self.target_update_counter > 0:
                        self.target_model.set_weights(self.model.get_weights())
                        self.target_update_counter = 0

                    episode_reward += reward

                current_epsilon -= epsilon_decay_value

                episodes_rewards.append(episode_reward)
                episodes_counter += 1

        moving_avg = np.convolve(episodes_rewards, np.ones((show_every,)) / show_every, mode='valid')

        if save_model is not None:
            self.save_agent(save_model)
            self.plot_training_info(moving_avg, save_model)

    def training_step(self, discount):

        # Start training only if certain number of samples is already saved
        if len(self.replay_memory) < self.min_replay_memory_size:
            return

        # Get a minibatch of random samples from memory replay table
        minibatch = random.sample(self.replay_memory, self.batch_size)

        # Get current states from minibatch, then query NN model for Q values
        current_states = np.array([transition[0] for transition in minibatch])
        current_qs_list = self.model.predict(current_states)

        # Get future states from minibatch, then query NN model for Q values
        # When using target network, query it, otherwise main network should be queried
        new_current_states = np.array([transition[3] for transition in minibatch])
        future_qs_list = self.target_model.predict(new_current_states)

        # Fill the NN inputs
        states_input = []
        target_q_values = []

        # Now we need to enumerate our batches
        for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):

            # If not a terminal state, get new q from future states, otherwise set it to 0
            # almost like with Q Learning, but we use just part of equation here
            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + discount * max_future_q
            else:
                new_q = reward

            # Get target Q value for given state
            # We only change the Q value of the taken action
            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            # And append to our training data
            states_input.append(current_state)
            target_q_values.append(current_qs)

        # Fit on all samples as one batch, log only on terminal state
        self.model.train_step(np.array(states_input), np.array(target_q_values))

    def save_agent(self, output_dir: Path):
        logger.info(f"Saving trained model to {output_dir}")
        self.model.save(Path(output_dir, "model"))

    @staticmethod
    def plot_training_info(moving_avg: np.array, agent_folder: Path=None):
        plt.figure(figsize=(5, 5))

        # Moving average plot
        plt.plot([i for i in range(len(moving_avg))], moving_avg)
        plt.ylabel(f"Reward")
        plt.xlabel("Episode #")
        plt.title("Reward moving average")

        if agent_folder is not None:
            plt.savefig(Path(agent_folder, "reward_moving_average.png"))

    def load_model(self, model_dir: Path):
        self.model = tf.keras.models.load_model(model_dir)

    def play_game(self, plot_game: bool=False):
        self.env.reset()
        starting_state = self.env.state
        done = False
        while not done:
            if plot_game:
                self.env.render()

            state = self.env.state
            action = self.produce_action(state)

            new_state, reward, done, _ = self.env.step(action)

        win = self.env.state[0] >= self.env.goal_position

        self.env.reset()

        return starting_state, win
