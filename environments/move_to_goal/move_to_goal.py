from typing import Tuple

import cv2
import numpy as np
from PIL import Image


class MoveToGoal(object):

    def __init__(self, board_x: int, board_y: int, goal_reward: int, move_reward: int, game_end: int):

        self.board_x = board_x
        self.board_y = board_y
        self.goal_reward = goal_reward
        self.move_reward = move_reward
        self.game_end = game_end
        self.board = None
        self.steps_played = 0
        self.positions = {"player": None, "goal": None}
        self.colors = {"player": (255, 150, 0),
                       "goal": (0, 255, 0)}
        self.actions = ["up", "right", "down", "left"]

    def get_board_size(self):
        return self.board_x, self.board_y

    def generate_board(self):
        self.board = np.zeros((self.board_x, self.board_y, 3), dtype=np.uint8)
        self.board[self.positions["player"]] = self.colors["player"]
        self.board[self.positions["goal"]] = self.colors["goal"]

    def prepare_game(self, player_pos: Tuple[int, int]=None, goal_pos: Tuple[int, int]=None):

        if player_pos is None:
            player_pos = (np.random.randint(0, self.board_x), np.random.randint(0, self.board_y))

        if goal_pos is None:
            goal_pos = (np.random.randint(0, self.board_x), np.random.randint(0, self.board_y))
            while goal_pos == player_pos:
                goal_pos = (np.random.randint(0, self.board_x), np.random.randint(0, self.board_y))

        self.positions["player"] = player_pos
        self.positions["goal"] = goal_pos
        self.steps_played = 0

        self.generate_board()

    def display_game(self):
        board_image = np.flip(np.transpose(self.board, (1, 0, 2)), 0)

        img = Image.fromarray(board_image, 'RGB')
        img = img.resize((self.board_x * 20, self.board_y * 20), cv2.INTER_AREA)
        cv2.imshow("image", np.array(img))

    def execute_player_action(self, action: int):
        action = self.actions[action]
        player_x = self.positions["player"][0]
        player_y = self.positions["player"][1]

        if action == "up":
            if player_y < self.board_y - 1:
                player_y += 1
        elif action == "right":
            if player_x < self.board_x - 1:
                player_x += 1
        elif action == "down":
            if player_y > 0:
                player_y -= 1
        elif action == "left":
            if player_x > 0:
                player_x -= 1
        else:
            raise ValueError(f"Wrong action: {action}")

        self.positions["player"] = (player_x, player_y)

        self.generate_board()

    def get_state(self):
        return self.positions["player"], self.positions["goal"]

    def step(self, action: int) -> (Tuple[Tuple[int, int], Tuple[int, int]], float, bool):

        self.execute_player_action(action)

        if self.positions["player"] == self.positions["goal"]:
            reward = self.goal_reward
            done = True
        else:
            reward = self.move_reward
            done = False

        self.steps_played += 1
        if self.steps_played >= self.game_end:
            done = True

        state = self.get_state()

        return state, reward, done
