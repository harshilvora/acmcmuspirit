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

        height, width = len(game_state_info.map), len(game_state_info.map[0])

        # print info about the game
        print(f"Turn {game_state_info.turn}, team {game_state_info.team}")
        print("Map height", height)
        print("Map width", width)

        # find un-occupied ally tile
        ally_tiles = []
        for row in range(height):
            for col in range(width):
                # get the tile at (row, col)
                tile = game_state_info.map[row][col]
                # skip fogged tiles
                if tile is not None:  # ignore fogged tiles
                    if tile.robot is None:  # ignore occupied tiles
                        if tile.terraform > 0:  # ensure tile is ally-terraformed
                            ally_tiles += [tile]

        enemy = game_state.get_enemy_robots()

        turn = game_state.get_turn()
        curr_metal = game_state.get_metal()

        if len(ally_tiles) > 0:
            # pick a random one to spawn on
            spawn_loc = random.choice(ally_tiles)
            spawn_type = random.choice([RobotType.MINER, RobotType.EXPLORER, RobotType.TERRAFORMER])
            # spawn the robot
            print(f"Spawning robot at {spawn_loc.row, spawn_loc.col}")
            if turn == 1 and len(ally_tiles) > 3:
                type1 = RobotType.EXPLORER

                if game_state.can_spawn_robot(type1, spawn_loc.row, spawn_loc.col):
                    game_state.spawn_robot(spawn_type, spawn_loc.row, spawn_loc.col)
                type2 = RobotType.EXPLORER
                type3 = RobotType.TERRAFORMER
                type4 = RobotType.MINER


            # check if we can spawn here (checks if we can afford, tile is empty, and tile is ours)


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


