# Tetris - DYOA Advanced at TU Graz WS 2020
# Name:       Matthias Grill
# Student ID: 12007662

import pygame
import time, random

from framework import BaseGame

class Block:
    blocknames = ['clevelandZ', 'rhodeIslandZ', 'blueRicky', 'smashBoy', 'orangeRicky', 'teewee', 'hero']

    def __init__(self, game, block_name):
        self.name = block_name
        self.rotation = random.randint(0, len(game.block_list[
                                                  self.name]) - 1)
        self.set_shape(game.block_list[self.name][self.rotation])
        self.x = int(game.board_width / 2) - int(self.width / 2)
        self.y = 0
        self.color = game.block_colors[
            self.name]

    def set_shape(self, shape):
        self.shape = shape
        self.width = len(shape[0])
        self.height = len(shape)

    def right_rotation(self, rotation_options):
        # rotate block once clockwise
        if self.rotation == len(rotation_options) - 1:
            self.set_shape(rotation_options[0])
            self.rotation = 0
        else:
            self.set_shape(rotation_options[self.rotation + 1])
            self.rotation += 1

    def left_rotation(self, rotation_options):
        # rotate block once counter-clockwise
        if self.rotation == 0:
            self.set_shape(rotation_options[len(rotation_options) - 1])
            self.rotation = len(rotation_options) - 1
        else:
            self.set_shape(rotation_options[self.rotation - 1])
            self.rotation -= 1


class Game(BaseGame):
    def run_game(self):

        self.level = 0

        current_block = self.get_new_block()
        next_block = self.get_new_block()

        #  Maps "lines removed" to "raw points gained"
        self.score_dictionary = {
            0: 0,
            1: 40,
            2: 100,
            3: 300,
            4: 1200
        }

        # GameLoop
        while True:
            self.test_quit_game()

            # game logic
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        if self.is_block_on_valid_position(current_block, x_change=1):
                            current_block.x += 1
                    elif event.key == pygame.K_LEFT:
                        if self.is_block_on_valid_position(current_block, x_change=-1):
                            current_block.x -= 1
                    elif event.key == pygame.K_DOWN:
                        while self.is_block_on_valid_position(current_block, y_change=1):
                            current_block.y += 1
                    elif event.key == pygame.K_q:
                        current_block.left_rotation(self.block_list[current_block.name])
                    elif event.key == pygame.K_e:
                        current_block.right_rotation(self.block_list[current_block.name])
                    elif event.key == pygame.K_p:
                        self.pause_game()

            if self.is_block_on_valid_position(current_block, y_change=1):
                current_block.y += 1

            if self.check_block_done(current_block):
                self.add_block_to_board(current_block)
                current_block = next_block
                next_block = self.get_new_block()

                # check game over
                if not self.is_block_on_valid_position(current_block):
                    return False

                removed_lines = self.remove_complete_line()
                new_score = self.calculate_new_score(removed_lines, self.level)
                self.calculate_new_level(new_score)
                self.score = new_score


            # Draw after game logic
            self.display.fill(self.background)
            self.draw_game_board()
            self.draw_score()
            self.draw_level()
            self.draw_next_block(next_block)
            if current_block != None:
                self.draw_block(current_block)
            pygame.display.update()
            self.set_game_speed(self.speed)
            self.clock.tick(self.speed)

    def pause_game(self):
        self.show_text("Paused")
        while True:
            wait_event = pygame.event.wait()
            if wait_event.type == pygame.KEYDOWN:
                if wait_event.key == pygame.K_p:
                    break

    def check_block_done(self, block):
        if block.y == self.board_height - block.height:
            return True

        x = block.x
        y = block.y
        for i in range(0, block.height):
            for j in range(0, block.width):
                if block.shape[i][j] == "x":
                    if self.gameboard[y + 1][x] != self.blank_color:
                        return True
                x += 1
            x = block.x
            y += 1

        return False

    # Check if Coordinate given is on board (returns True/False)
    def is_coordinate_on_board(self, x, y):
        # check if coordinate is on playingboard (in boundary of self.boardWidth and self.boardHeight)
        if 0 <= x < self.board_width and 0 <= y < self.board_height:
            return True
        return False

    # Parameters block, x_change (any movement done in X direction), yChange (movement in Y direction)
    # Returns True if no part of the block is outside the Board or collides with another Block
    def is_block_on_valid_position(self, block, x_change=0, y_change=0):
        # check if block is on valid position after change in x or y direction
        x = block.x + x_change
        y = block.y + y_change

        if 0 <= x <= self.board_width - block.width:
            if y <= self.board_height - block.height:
                for i in range(0, block.height):
                    for j in range(0, block.width):
                        if block.shape[i][j] == "x":
                            if self.gameboard[y][x] != self.blank_color:
                                return False
                        x += 1
                    x = block.x + x_change
                    y += 1
                return True

        return False

    # Check if the line on y Coordinate is complete
    # Returns True if the line is complete
    def check_line_complete(self, y_coord):
        # check if line on yCoord is complete and can be removed
        for char in self.gameboard[y_coord]:
            if char == self.blank_color:
                return False
        return True

    # Go over all lines and remove those, which are complete
    # Returns Number of complete lines removed
    def remove_complete_line(self):
        # go over all lines and check if one can be removed
        count = 0
        for line_index in range(0, len(self.gameboard)):
            if self.check_line_complete(line_index):
                for replace_index in range(line_index, 1, -1):
                    self.gameboard[replace_index] = self.gameboard[replace_index - 1][:]
                for first_row_index in range(0, len(self.gameboard[0])):
                    self.gameboard[0][first_row_index] = self.blank_color
                count += 1

        return count

    # Create a new random block
    # Returns the newly created Block Class
    def get_new_block(self):
        # make block choice random! (Use random.choice out of the list of blocks) see blocknames array
        block_name = random.choice(Block.blocknames)
        block = Block(self, block_name)
        return block

    def add_block_to_board(self, block):
        # once block is not falling, place it on the gameboard
        # add Block to the designated Location on the board once it stopped moving
        x = block.x
        y = block.y
        for row in range(0, block.height):
            for column in range(0, block.width):
                if block.shape[row][column] == 'x':
                    self.gameboard[y][x] = block.color
                x += 1
            x = block.x
            y += 1

    # calculate new Score after a line has been removed
    def calculate_new_score(self, lines_removed, level):
        # Points gained: Points per line removed at once times the level modifier!
        # Points per lines removed corresponds to the score_directory
        # The level modifier is 1 higher than the current level.
        if lines_removed == 0:
            return self.score
        return self.score + self.score_dictionary[lines_removed] * (level + 1)

    # calculate new Level after the score has changed
    def calculate_new_level(self, score):
        # The level generally corresponds to the score divided by 300 points.
        # 300 -> level 1; 600 -> level 2; 900 -> level 3
        old_level = self.score // 300
        self.level = score // 300
        if self.level > old_level:
            self.set_game_speed(self.speed + 1)

    # set the current game speed
    def set_game_speed(self, speed):
        # It starts as defined in base.py and should increase by 1 after a level up.
        self.speed = speed

# -------------------------------------------------------------------------------------
# Do not modify the code below, your implementation should be done above
# -------------------------------------------------------------------------------------
def main():
    pygame.init()
    game = Game()

    game.display = pygame.display.set_mode((game.window_width, game.window_height))
    game.clock = pygame.time.Clock()
    pygame.display.set_caption('Tetris')

    game.show_text('Tetris')

    game.run_game()
    game.show_text('Game Over')


if __name__ == '__main__':
    main()
