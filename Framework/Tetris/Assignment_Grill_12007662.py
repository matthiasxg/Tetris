# Tetris - DYOA Advanced at TU Graz WS 2020
# Name:       Matthias Grill
# Student ID: 12007662

import pygame
import time, random
import threading

from framework import BaseGame


# Recommended Start: init function of Block Class
class Block:
    blocknames = ['clevelandZ', 'rhodeIslandZ', 'blueRicky', 'smashBoy', 'orangeRicky', 'teewee', 'hero']

    def __init__(self, game, block_name):
        self.name = block_name  # set name / Can be 'hero', 'teewee', ...
        self.rotation = random.randint(0, len(game.block_list[
                                                  self.name]) - 1)  # randomize rotation (e.g. 0, 1, 2, 3; Hint: different number of rotations per block)
        self.set_shape(game.block_list[self.name][self.rotation])
        self.x = int(game.board_width / 2) - int(self.width / 2)
        self.y = 0
        self.color = game.block_colors[
            self.name]  # Set Color correctly / Can be 'red', 'green', ... (see self.blockColors)

    def set_shape(self, shape):
        self.shape = shape
        self.width = len(shape[0])
        self.height = len(shape)

    def right_rotation(self, rotation_options):
        # TODO rotate block once clockwise
        pass

    def left_rotation(self, rotation_options):
        # TODO rotate block once counter-clockwise
        pass

class Game(BaseGame):
    def run_game(self):
        self.board = self.get_empty_board()
        fall_time = time.time()

        current_block = self.get_new_block()
        next_block = self.get_new_block()

        # TODO Fill in the score dictionary
        #  Maps "lines removed" to "raw points gained"
        #  0 lines: 0 points; 1 line: 40 points; 2 lines: 100 points; 3 lines: 300 points; 4 lines: 1200 points
        self.score_dictionary = {
            0: 0,
            1: 40,
            2: 100,
            3: 300,
            4: 1200
        }

        worker = threading.Thread(target=self.block_down_thread, args=(self.speed, current_block))
        worker.start()

        # GameLoop
        while True:
            self.test_quit_game()
            # TODO Game Logic: implement key events & move blocks (Hint: check if move is valid/block is on the Board)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        if self.is_block_on_valid_position(current_block, x_change=1):
                            current_block.x += 1
                    elif event.key == pygame.K_LEFT:
                        if self.is_block_on_valid_position(current_block, x_change=-1):
                            current_block.x -= 1
                    elif event.key == pygame.K_DOWN:
                        if self.is_block_on_valid_position(current_block, y_change=1):
                            current_block.y += 1
                        if self.check_block_done(current_block):
                            self.add_block_to_board(current_block)
                            current_block = next_block
                            next_block = self.get_new_block()
                            worker = threading.Thread(target=self.block_down_thread, args=(self.speed, current_block))
                            worker.start()


            # Draw after game logic
            self.display.fill(self.background)
            self.draw_game_board()
            self.draw_score()
            self.draw_next_block(next_block)
            if current_block != None:
                self.draw_block(current_block)
            pygame.display.update()
            self.set_game_speed(self.speed)
            self.clock.tick(self.speed)

    def check_block_done(self, block):
        if block.y == self.board_height - block.height:
            return True

        x = block.x
        y = block.y
        for i in range(0, block.height):
            for j in range(0, block.width):
                if block.shape[i][j] == "x":
                    if self.board[y + 1][x] == "x":
                        return True
                x += 1
            x = block.x
            y += 1

        return False

    def block_down_thread(self, speed, block):
        print("Start thread")
        while True:
            time.sleep(5/speed)
            if self.is_block_on_valid_position(block, y_change=1):
                block.y += 1
            else:
                break
        print("Stopped Thread")

    # Check if Coordinate given is on board (returns True/False)
    def is_coordinate_on_board(self, x, y):
        # check if coordinate is on playingboard (in boundary of self.boardWidth and self.boardHeight)
        if 0 <= x <= self.board_width and 0 <= y <= self.board_height:
            return True
        return False

    # Parameters block, x_change (any movement done in X direction), yChange (movement in Y direction)
    # Returns True if no part of the block is outside the Board or collides with another Block
    def is_block_on_valid_position(self, block, x_change=0, y_change=0):
        # check if block is on valid position after change in x or y direction
        x = block.x + x_change
        y = block.y + y_change
        if 0 <= x <= self.board_width - self.get_real_blockwidth(block):
            if y <= self.board_height - block.height:
                for i in range(0, block.height):
                    for j in range(0, block.width):
                        if block.shape[i][j] == "x":
                            if self.board[y][x] == "x":
                                return False
                        x += 1
                    x = block.x
                    y += 1
                return True
        return False

    # Checks for empty lines at the beginning and ending of a block
    # Returns the real width of a block
    def get_real_blockwidth(self, block):
        width = block.width
        pre = ""
        post = ""
        for i in range(0, len(block.shape)):
            pre += block.shape[i][0]
            post += block.shape[i][len(block.shape[i]) - 1]

        flag = False
        for char in pre:
            if char == "x":
                flag = True

        if not flag:
            width -= 1

        flag = False
        for char in post:
            if char == "x":
                flag = True

        if not flag:
            width -= 1

        return width

    # Check if the line on y Coordinate is complete
    # Returns True if the line is complete
    def check_line_complete(self, y_coord):
        # TODO check if line on yCoord is complete and can be removed
        return False

    # Go over all lines and remove those, which are complete
    # Returns Number of complete lines removed
    def remove_complete_line(self):
        # TODO go over all lines and check if one can be removed
        return 0

    # Create a new random block
    # Returns the newly created Block Class
    def get_new_block(self):
        # make block choice random! (Use random.choice out of the list of blocks) see blocknames array
        blockname = random.choice(Block.blocknames)
        block = Block(self, blockname)
        return block

    def add_block_to_board(self, block):
        # once block is not falling, place it on the gameboard
        #  add Block to the designated Location on the board once it stopped moving
        x = block.x
        y = block.y
        for i in range(0, block.height):
            for j in range(0, block.width):
                if block.shape[i][j] == "x":
                    self.board[y][x] = "x"
                    self.gameboard[y][x] = block.color
                x += 1
            x = block.x
            y += 1

    # calculate new Score after a line has been removed
    def calculate_new_score(self, lines_removed, level):
        # TODO calculate new score
        # Points gained: Points per line removed at once times the level modifier!
        # Points per lines removed corresponds to the score_directory
        # The level modifier is 1 higher than the current level.
        pass

    # calculate new Level after the score has changed
    # TODO calculate new level
    def calculate_new_level(self, score):
        # The level generally corresponds to the score divided by 300 points.
        # 300 -> level 1; 600 -> level 2; 900 -> level 3
        # TODO increase gamespeed by 1 on level up only
        pass

    # set the current game speed
    def set_game_speed(self, speed):
        # TODO set the correct game speed!
        # It starts as defined in base.py and should increase by 1 after a level up.
        pass


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
