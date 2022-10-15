import pygame 
import random
import numpy as np
import sys

pygame.init()

# Preset Colors
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
white = pygame.Color(255, 255, 255)
black = pygame.Color(0, 0, 0)
cyan = pygame.Color(0, 100, 100)

# Preset Measurements
game_pace = 160000000000000
unit_size = 20

class Snake:
    def __init__(self, width, height):
        # game variables
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.gameOver = False
        self.font = pygame.font.SysFont('verdana', 20)

        # initialize display
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game")

        self.recalibrate(width, height)
        

    def recalibrate(self, width, height):
        # setting snake position and orientation
        self.head = (width/2, height/2)
        self.body = [self.head, (self.head[0] - unit_size, self.head[1]), (self.head[0] - (2*unit_size), self.head[1])]

        self.direction = "RIGHT"
        self.game_step = 0

        # scoring and food
        self.score = 0
        self.foodSpawned = True
        self.food = [self.head[0] + (4*unit_size), self.head[1]]

    def spawnFood(self):
        self.food = [random.randint(0, (self.width - unit_size) // unit_size) * unit_size, random.randint(0, (self.height - unit_size) // unit_size) * unit_size]
        self.foodSpawned = True

        for block in self.body:
            if self.food[0] == block[0] and self.food[1] == block[1]:
                self.spawnFood()

        if self.food in self.body:
            self.spawnFood()
    
    def step(self, action):
        # action has form [straight, left, right]
        
        # quantify direction:
        if self.direction == "RIGHT":
            dir = 0
        elif self.direction == "LEFT":
            dir = 2
        elif self.direction == "UP":
            dir = 3
        elif self.direction == "DOWN":
            dir = 1

        # execute one game step
        if action[1] == 1:  # left turn
            if dir == 0:
                dir = 3
            else:
                dir -= 1
        elif action[2] == 1:    # right turn
            if dir == 3:
                dir = 0
            else:
                dir += 1

        if dir == 0:
            self.direction = "RIGHT"
        elif dir == 1:
            self.direction = "DOWN"
        elif dir == 2: 
            self.direction = "LEFT"
        else:
            self.direction = "UP"

        x = self.head[0]
        y = self.head[1]

        if self.direction == "RIGHT":
            x += unit_size
        elif self.direction == "LEFT":
            x -= unit_size
        elif self.direction == "UP":
            y -= unit_size
        elif self.direction == "DOWN":
            y += unit_size

        self.head = (x, y)

    def collide(self, danger_point):
        if danger_point == None:
            danger_point = self.head
        
        # check if snake goes out of bounds
        if danger_point[0] > (self.width - unit_size) or danger_point[0] < 0 or danger_point[1] > (self.height - unit_size) or danger_point[1] < 0:
            self.gameOver = True
            return True
        
        # check for self collision
        if danger_point in self.body[1:]:
            self.gameOver = True
            return True
        
        return False
    def game(self, action):
        self.game_step += 1
        # user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
       
        # Movement
        self.step(action)
        self.body.insert(0, self.head)

        reward = 0

        # CHECK FOR GAME OVER
        self.gameOver = self.collide(None)

        if self.gameOver == True or self.game_step > len(self.body) * 50:
            reward = -10
            return self.gameOver, self.score, reward
            

        # check if new food needs to be spawned
        if self.head[0] == self.food[0] and self.head[1] == self.food[1]:
            reward = 10
            self.score += 1
            self.spawnFood()
        else:
            self.body.pop()

        # update graphics/clock
        self.display.fill(black)

        # snake
        for block in self.body:
            pygame.draw.rect(self.display, green, pygame.Rect(block[0], block[1], unit_size, unit_size))
        
        # foods
        pygame.draw.rect(self.display, red, pygame.Rect(self.food[0], self.food[1], unit_size, unit_size))

        # score 
        self.display.blit(self.font.render("Score: " + str(self.score), True, cyan), [0, 0])
        pygame.display.flip()

        self.clock.tick(game_pace)

        return self.gameOver, self.score, reward

# game loop
# play = Snake(640, 480)

# while True:
#     finished, score, reward = play.game()

#     if finished == True:
#         break

# print("Final Score: " + str(score))
# pygame.quit()