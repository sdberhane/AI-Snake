from os import stat
from typing_extensions import Self
import numpy as np
import torch as t
import random
import snake
from collections import deque
import model
import matplotlib.pyplot as plt
import IPython as ip

def train():
    game = snake.Snake(640, 480)
    agent = Agent()

    total = 0

    scores = []
    averages = []

    while True:
        # find new state from old state and recommended action
        curr_state = agent.state(game)
        action = agent.act(curr_state)
        game_over, score, reward = game.game(action)
        new_state = agent.state(game)

        # learn
        agent.train_partially(curr_state, new_state, action, reward, game_over)
        agent.collect(curr_state, new_state, action, reward, game_over)

        if game_over:
            agent.game_numnber += 1
            game.recalibrate(640, 480)
            agent.train_rigourously()

            total += score
            avg = total / agent.game_numnber


            scores.append(score)
            averages.append(avg)

            plot(scores, averages)
            
            print("Game #" + str(agent.game_numnber) + ", Score: " + str(score) + ", Average Score: " + str(avg))


def plot(scores, averages):
    ip.display.clear_output(wait=True)
    ip.display.display(plt.gcf())
    plt.clf()
    plt.title('AI Progress')
    plt.xlabel('Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(averages)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(averages)-1, averages[-1], str(averages[-1]))
    plt.show(block=False)
    plt.pause(.1)



class Agent:
    def __init__(self):
        self.game_numnber = 0
        self.randomization = 0
        self.discount_rate = .9
        self.learning_rate = .001

        self.log = deque(maxlen=500000)

        self.model = model.Q(11, 256, 3)
        self.trainer = model.QTrainer(self.model, self.discount_rate, self.learning_rate)

    def state(self, snake):
        head = snake.head

        # check current direction
        left = snake.direction == "LEFT"
        right = snake.direction == "RIGHT"
        up = snake.direction == "UP"
        down = snake.direction == "DOWN"

        # danger points
        left_point = (head[0] - 20, head[1])
        right_point = (head[0] + 20, head[1])
        up_point = (head[0], head[1] - 20)
        down_point = (head[0], head[1] + 20)

        # check proximity threats
        straight_threat = (left and snake.collide(left_point)) or \
        (right and snake.collide(right_point)) or \
        (up and snake.collide(up_point)) or \
        (down and snake.collide(down_point))

        left_threat = (left and snake.collide(down_point)) or \
        (right and snake.collide(up_point)) or \
        (up and snake.collide(left_point)) or \
        (down and snake.collide(right_point))

        right_threat = (left and snake.collide(up_point)) or \
        (right and snake.collide(down_point)) or \
        (up and snake.collide(right_point)) or \
        (down and snake.collide(left_point))

        # check food direction
        food_left = snake.food[0] < head[0]
        food_right = snake.food[0] > head[0]
        food_up = snake.food[0] < head[1]
        food_down = snake.food[1] > head[1]
        
        result = [
            straight_threat, right_threat, left_threat,
            left, right, up, down,
            food_left, food_right, food_up, food_down
            ]
        
        return np.array(result, dtype=int)

    def act(self, state):
        self.randomization = 80 - self.game_numnber
        move = [0, 0, 0]

        if self.randomization > random.randint(0, 200):
            move[random.randint(0, 2)] = 1
        else:
            predict = self.model(t.tensor(state, dtype=t.float))
            move[t.argmax(predict).item()] = 1
        
        return move

    def collect(self, curr_state, new_state, action, reward, game_over):
        # removes item in the case of overflow
        self.log.append((curr_state, new_state, action, reward, game_over))

    def train_partially(self, curr_state, new_state, action, reward, game_over):
        self.trainer.train(curr_state, new_state, action, reward, game_over)

    def train_rigourously(self):
        if len(self.log) < 1000:
            sample = self.log
        else:
            sample = random.sample(self.log, 1000) 

        curr_state, new_state, action, reward, game_over = zip(*sample)
        self.trainer.train(curr_state, new_state, action, reward, game_over)


if __name__ == '__main__':
    train()