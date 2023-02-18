import itertools
import math

from src.game_constants import RobotType, Direction, Team, TileState
from src.game_state import GameState
from src.player import Player
from src.map import TileInfo, RobotInfo
import random


class BotPlayer(Player):
    """
    A child class that implements the play_turn method
    """

    def __init__(self, team: Team):
        Player.__init__(self, team)

    def play_turn(self, game_state: GameState) -> None:
        game_state_info = game_state.get_info()

        cols, rows = len(game_state_info.map), len(game_state_info.map[0])

        # print info about the game
        print(f"Turn {game_state_info.turn}, team {game_state_info.team}")
        print("Map height", cols)
        print("Map width", rows)

        # Early Stage

        # Medium Stage
        # find un-occupied ally tile
        ally_tiles = []
        terraform_counts = []
        mines_counts = []
        mining_tile = []
        max_mine_tile = []
        max_mine = 0
        quadrant_tiles = []
        explored_tiles = []
        for i in range(2):
            for j in range(2):
                row_start = i * rows // 2
                row_end = (i + 1) * rows // 2
                col_start = j * cols // 2
                col_end = (j + 1) * cols // 2
                count = 0
                mines = 0
                single_quadrant_tiles = []
                for row in range(row_start, row_end):
                    for col in range(col_start, col_end):
                        tile = game_state_info.map[row][col]
                        if tile is not None:  # ignore fogged tiles
                            explored_tiles += []
                            if tile.robot is None:  # ignore occupied tiles
                                if tile.terraform > 0:  # ensure tile is ally-terraformed
                                    count += 1
                                    ally_tiles += [tile]
                                    single_quadrant_tiles += [tile]
                                if tile.mining > 0:
                                    if tile.mining > max_mine:
                                        max_mine_tile = [tile]
                                    mines += tile.mining
                                    mining_tile += [tile]
                terraform_counts.append(count)
                mines_counts.append(mines)
                quadrant_tiles.append(single_quadrant_tiles)

        max_mine_count = max(mines_counts)
        if max_mine_count > 0:
            quadrant_mines = terraform_counts.index(max_mine_count)
            deploy_bot = quadrant_tiles[quadrant_mines]
        else:
            max_blue_count = max(terraform_counts)
            quadrant = terraform_counts.index(max_blue_count)
            deploy_bot = quadrant_tiles[quadrant]

        # enemy = game_state.get_enemy_robots()
        print(max_mine_tile)
        turn = game_state.get_turn()
        curr_metal = game_state.get_metal()
        robots = game_state.get_ally_robots()

        numberOfMiners = 0
        # Find number of each type of robot
        for rname, rob in robots.items():
            print(f"Robot {rname} at {rob.row, rob.col}")
            if rob.get_type() == "MINER":
                numberOfMiners += 1

        # Spawn a miner in Early game to get most metal
        if max_mine_count > 0 and len(mining_tile) > numberOfMiners and curr_metal > 100:  # and turn < EARLY
            close_tile = self.closest_point(deploy_bot, max_mine_tile)
            if game_state.can_spawn_robot(RobotType.MINER, close_tile.row, close_tile.col):
                game_state.spawn_robot(RobotType.MINER, close_tile.row, close_tile.col)
                deploy_bot.remove(close_tile)

        if len(deploy_bot) > 0:

            for t in deploy_bot:
                # pick a random one to spawn on
                location = self.find_corners_of_tiles(rows, cols, deploy_bot)

                explorer_location = random.choice(location)
                if game_state.can_spawn_robot(RobotType.EXPLORER, explorer_location[0], explorer_location[1]):
                    game_state.spawn_robot(RobotType.EXPLORER, explorer_location[0], explorer_location[1])

                    # self.find_closest_points(ally_tiles, height)
                    # check if we can spawn here (checks if we can afford, tile is empty, and tile is ours)
                    # if game_state.can_spawn_robot(type1, spawn_loc.row, spawn_loc.col):
                    #     game_state.spawn_robot(spawn_type, spawn_loc.row, spawn_loc.col)

        # move robots
        # robots = game_state.get_ally_robots()
        #
        # # iterate through dictionary of robots
        # for rname, rob in robots.items():
        #
        #
        # if len(ally_tiles) > 0:
        #     if(turn == 3):
        #         robotype = RobotType.EXPLORER

        return

    def find_corners_of_tiles(self, rows, cols, coords):
        # rows = len(grid)
        # cols = len(grid[0])
        top_left = None
        top_right = None
        bottom_left = None
        bottom_right = None

        # Find top-left corner
        for t in coords:
            row = t.row
            col = t.col
            if not top_left or row + col < top_left[0] + top_left[1]:
                top_left = (row, col)

        # Find top-right corner
        for t in coords:
            row = t.row
            col = t.col
            if not top_right or row - col < top_right[0] - top_right[1]:
                top_right = (row, col)

        # Find bottom-left corner
        for t in coords:
            row = t.row
            col = t.col
            if not bottom_left or col - row < bottom_left[1] - bottom_left[0]:
                bottom_left = (row, col)

        # Find bottom-right corner
        for t in coords:
            row = t.row
            col = t.col
            if not bottom_right or row + col > bottom_right[0] + bottom_right[1]:
                bottom_right = (row, col)

        return top_left, top_right, bottom_left, bottom_right

    def closest_point(self, points, reference_point):
        closest_point = None
        closest_distance = 0

        for point in points:
            distance = math.sqrt(sum([(point[i] - reference_point[i]) ** 2 for i in range(len(point))]))
            if distance < closest_distance:
                closest_distance = distance
                closest_point = point

        return closest_point
