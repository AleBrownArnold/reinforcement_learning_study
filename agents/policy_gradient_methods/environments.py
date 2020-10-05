from pathlib import Path
from typing import List

import gym
import numpy as np


class Episode(object):
    """A single episode of an environment.

    Attributes:
        states: A list with all the states that occurred in the episode
        rewards: A list with all the rewards obtained in the episode
        actions: A list with all the actions taken in the episode
        total_reward: The total reward obtained in the episode
    """
    def __init__(self, states: list, actions: list, rewards: list):
        """Creates a new episode.

        Args:
            states: A list with all the states that occurred in the episode
            rewards: A list with all the rewards obtained in the episode
            actions: A list with all the actions taken in the episode
        """
        assert len(states) == len(rewards) == len(actions)
        self.states = np.array(states, dtype=np.float32)
        self.rewards = np.array(rewards, dtype=np.float32)
        self.actions = np.array(actions, dtype=np.int32)
        self.total_reward = np.sum(self.rewards)

    def __len__(self) -> int:
        """
        Returns:
            The length of the episode.
        """
        return len(self.states)


class EpisodesBatch(object):
    """
    A collection of episodes.
    """
    def __init__(self, max_size: int):
        """
        Creates an empty episodes batch.
        :param max_size: The max number of stored steps.
        """
        self.episodes = []
        self.max_size = max_size
        self.current_size = 0

    def __len__(self) -> int:
        """
        :return the total number of stored steps
        """
        return self.current_size

    def __iter__(self):
        """
        Iterate over the stored episodes and yield one at the time
        :return: An Episode object
        """
        for episode in self.episodes:
            yield episode

    def add_episode(self, episode: Episode):
        """
        Add and episode to the batch. Update number of stored steps.
        :param episode: An Episode object
        :raises ValueError if the episodes batch is full (max number of steps stored)
        """
        if not self.is_full():
            self.episodes.append(episode)
            self.current_size += len(episode)
        else:
            raise ValueError(f"The batch is full! max_size: {self.max_size} -"
                             f" current_size: {self.current_size}")

    def is_full(self) -> bool:
        """
        :return: True if the number of stored steps is more than or equal to the max batch size.
        """
        return self.current_size >= self.max_size


class Environment(object):
    """Base class to create environments that can be used to train a
    policy gradient algorithm. All methods need to be implemented.
    """
    def __init__(self, env, action_space_n: int, state_space_n: int,
                 actions: List[str]):
        """Create a new Environment object.

        Args:
            env: An object with the environment implementation.
            action_space_n: The number of possible actions
            state_space_n: The length of the state vector representation
            actions: A list with the actions names
        """
        self.env = env
        self.action_space_n = action_space_n
        self.state_space_n = state_space_n
        self.actions = actions

    def reset_environment(self):
        """Reset the environment to start a new episode."""
        raise NotImplementedError

    def get_environment_state(self) -> np.array:
        """Get the current state of the environment. Must be ready to feed to
        the neural network.

        Returns:
            The current state (np.array)
        """
        raise NotImplementedError

    def environment_step(self, action: int) -> (np.array, float, bool):
        """Make a move in the environment with given action.

        Args:
            action: The action index

        Returns:
            next_environment_state (np.array), reward (float), terminated_environment (bool)
        """
        raise NotImplementedError

    def get_possible_states(self) -> np.array:
        """Returns a list of every possible environment state, or a sample of them.

        Returns:
            List of states ready to be feed into de neural network (np.array)
        """
        raise NotImplementedError

    def policy_values_plot(self, save_fig: Path=None, show_plot: bool=False):
        """
        TODO: Change name and usage (policy_values_info)
        """
        raise NotImplementedError

    def render_environment(self):
        """Render the environment."""
        raise NotImplementedError

    @staticmethod
    def win_condition(episode: Episode):
        raise NotImplementedError


class CartPoleEnvironment(Environment):

    def __init__(self):
        env = gym.make("CartPole-v0")
        action_space = env.action_space.n
        state_space = env.observation_space.shape[0]
        actions = ["left", "right"]

        Environment.__init__(self, env, action_space, state_space, actions)

    def reset_environment(self):
        self.env.reset()

    def get_environment_state(self) -> np.array:
        return self.env.state

    def environment_step(self, action: int) -> (np.array, float, bool):
        next_state, reward, done, _ = self.env.step(int(action))
        return next_state, reward, done

    def get_possible_states(self) -> np.array:
        return None

    def policy_values_plot(self, save_fig: Path = None, show_plot: bool = False):
        return None, None

    def render_environment(self):
        self.env.render()

    @staticmethod
    def win_condition(episode: Episode):
        return episode.total_reward >= 200


class AcrobotEnvironment(Environment):

    def __init__(self):
        env = gym.make("Acrobot-v1")
        action_space = env.action_space.n
        state_space = env.observation_space.shape[0]
        actions = ["left", "null", "right"]

        Environment.__init__(self, env, action_space, state_space, actions)

    def reset_environment(self):
        self.env.reset()

    def get_environment_state(self) -> np.array:
        s = self.env.state
        return np.array([np.cos(s[0]), np.sin(s[0]), np.cos(s[1]), np.sin(s[1]), s[2], s[3]])

    def environment_step(self, action: int) -> (np.array, float, bool):
        next_state, reward, done, _ = self.env.step(int(action))
        return next_state, reward, done

    def get_possible_states(self) -> np.array:
        return None

    def policy_values_plot(self, save_fig: Path = None, show_plot: bool = False):
        return None, None

    def render_environment(self):
        self.env.render()

    @staticmethod
    def win_condition(episode: Episode):
        return episode.total_reward >= 200
