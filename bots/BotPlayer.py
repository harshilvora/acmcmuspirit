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

    miningrobots = {}

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
                                    if tile.mining > max_mine : #and tuple(tile) not in self.miningrobots
                                        # location of maximum mineable tile
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
            if rob.type.value == "Miner":
                numberOfMiners += 1

        # Spawn a miner in Early game to get most metal
        if max_mine_count > 0 and len(mining_tile) > numberOfMiners and curr_metal > 100:  # and turn < EARLY
            close_tile = self.closest_point(deploy_bot, max_mine_tile[0])
            if game_state.can_spawn_robot(RobotType.MINER, close_tile.row, close_tile.col):
                createdBot = game_state.spawn_robot(RobotType.MINER, close_tile.row, close_tile.col)
                # remove created mining bot
                deploy_bot.remove(close_tile)
                self.miningrobots[tuple(max_mine_tile)] = createdBot.name

        if len(deploy_bot) > 0:

            # Explorer Location
            location = self.find_corners_of_tiles(rows, cols, deploy_bot)

            explorer_location = random.choice(location)
            if game_state.can_spawn_robot(RobotType.EXPLORER, explorer_location.row, explorer_location.col):
                game_state.spawn_robot(RobotType.EXPLORER, explorer_location.row, explorer_location.col)
                deploy_bot.remove(explorer_location)
            # Terraformer deployed to closest mine first
            if max_mine_count > 0 :
                close_tile = self.closest_point(deploy_bot, max_mine_tile[0])
                if game_state.can_spawn_robot(RobotType.TERRAFORMER, close_tile.row, close_tile.col):
                    game_state.spawn_robot(RobotType.TERRAFORMER, close_tile.row, close_tile.col)
                    deploy_bot.remove(close_tile)
            else:
                explorer_location = random.choice(location)
                if game_state.can_spawn_robot(RobotType.TERRAFORMER, explorer_location.row, explorer_location.col):
                    game_state.spawn_robot(RobotType.TERRAFORMER, explorer_location.row, explorer_location.col)
                    deploy_bot.remove(explorer_location)



        for rname, rob in robots.items():
            print(f"Robot {rname} at {rob.row, rob.col}")

            # randomly move if possible
            if rob.type.value == "Miner":
                dir, moves = game_state.optimal_path(rob.row, rob.col, max_mine_tile[0].row, max_mine_tile[0].col)
                self.movepath(game_state, rname, dir, rob)

            elif rob.type.value == "Explorer":
                all_dirs = [dir for dir in Direction]
                move_dir = random.choice(all_dirs)
                self.movepath(game_state, rname, move_dir, rob)

            elif rob.type.value == "Terraformer":
                all_dirs = [dir for dir in Direction]
                move_dir = random.choice(all_dirs)
                self.movepath(game_state, rname, move_dir, rob)

            # check if we can move in this direction
            # if game_state.can_move_robot(rname, move_dir):
            #     # try to not collide into robots from our team
            #     dest_loc = (rob.row + move_dir.value[0], rob.col + move_dir.value[1])
            #     dest_tile = game_state.get_map()[dest_loc[0]][dest_loc[1]]
            #
            #     if dest_tile.robot is None or dest_tile.robot.team != self.team:
            #         game_state.move_robot(rname, move_dir)
            #
            # # action if possible
            # if game_state.can_robot_action(rname):
            #     game_state.robot_action(rname)

        return

    def movepath(self, game_state, rname, move_dir, rob):
        if game_state.can_move_robot(rname, move_dir):
            # try to not collide into robots from our team
            dest_loc = (rob.row + move_dir.value[0], rob.col + move_dir.value[1])
            dest_tile = game_state.get_map()[dest_loc[0]][dest_loc[1]]

            if dest_tile.robot is None or dest_tile.robot.team != self.team:
                game_state.move_robot(rname, move_dir)

        if game_state.can_robot_action(rname):
            game_state.robot_action(rname)

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
                top_left = t

        # Find top-right corner
        for t in coords:
            row = t.row
            col = t.col
            if not top_right or row - col < top_right[0] - top_right[1]:
                top_right = t

        # Find bottom-left corner
        for t in coords:
            row = t.row
            col = t.col
            if not bottom_left or col - row < bottom_left[1] - bottom_left[0]:
                bottom_left = t

        # Find bottom-right corner
        for t in coords:
            row = t.row
            col = t.col
            if not bottom_right or row + col > bottom_right[0] + bottom_right[1]:
                bottom_right = t

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
