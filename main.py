import sys
import logging

from bounce.loop import mainLoop

if __name__ == '__main__':
    player_colors = []
    if len(sys.argv) > 1:
        player_colors = sys.argv[1:]

    sys.exit(mainLoop(player_count=3, player_colors=player_colors))
