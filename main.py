import sys
import logging

from bounce import main

if __name__ == "__main__":
    player_colors = []
    if len(sys.argv) > 1:
        player_colors = sys.argv[1:]

    player_count = 1
    if player_colors:
        player_count = len(player_colors)

    sys.exit(
        main(
            player_count=player_count,
            player_colors=player_colors,
            tick_speed=100,
            CREATE_BALLS_MANUALLY=False,
            debug=False,
        )
    )
