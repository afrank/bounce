import pygame
import sys
import random as rand
import logging

from bounce import Ball, Action, colors

def mainLoop(
    player_count=3,
    player_colors=[],
    debug=False,
    CREATE_BALLS_MANUALLY=False,
    MAX_BALLS_IN_PLAY=300,
    CREATE_BALLS_COOLDOWN=30,
    BALLS_LEFT_TO_WIN=0,
    tick_speed=100,
):
    selected_colors = []

    logging.basicConfig(
        format="%(asctime)s | %(message)s",
        level=(logging.DEBUG if debug else logging.INFO),
    )

    win_size = width, height = 1600, 1000

    window = pygame.display.set_mode(win_size)

    pygame.display.set_caption("bounce.v01")
    clock = pygame.time.Clock()

    balls = {}
    player_balls = {}

    tick = 0
    most_recent_event = 0
    game_round = 1
    total_balls = 50 * game_round
    balls_to_drop = total_balls
    winner = ""
    round_tally = {}
    winnable = False
    cooldown_count = 0
    max_cooldowns = game_round

    CREATE_BALLS = True

    if CREATE_BALLS_MANUALLY:
        CREATE_BALLS = False

    for x in range(player_count):
        if player_colors and len(player_colors) - 1 >= x:
            color = player_colors[x]
        else:
            color = rand.choice([x for x in colors.keys() if x not in selected_colors])
        new_ball = Ball(
            *(800, 50),
            win_height=height,
            win_width=width,
            vel_x=rand.uniform(-5, 5),
            ball_radius=rand.triangular(10, 20, 50),
            player_ball=True,
            color=color,
        )
        player_balls[new_ball.id] = new_ball

    logging.info(f"Beginning of round {game_round}. Dropping {total_balls} balls")
    while True:
        tick += 1
        add_balls, del_balls = [], []
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                pygame.quit()
                logging.info("Exiting")
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and (
                CREATE_BALLS or CREATE_BALLS_MANUALLY
            ):
                add_balls += [pygame.mouse.get_pos()]

        # if tick - 100 > most_recent_event:
        #    logging.debug("no recent events, adding a ball")
        #    add_balls += [ (0,0) ]

        if len(balls) >= MAX_BALLS_IN_PLAY:
            logging.debug(f"Creation Throttle reached: {len(balls)}")
            CREATE_BALLS = False
            winnable = True

        if (
            not CREATE_BALLS
            and len(balls) <= CREATE_BALLS_COOLDOWN
            and cooldown_count < max_cooldowns
        ):
            logging.debug(f"Cooldown reached, re-enabling explosions")
            CREATE_BALLS = True
            cooldown_count += 1

        if winnable and len(balls.keys()) <= BALLS_LEFT_TO_WIN:
            logging.info(f"Round Over. Player stats:")
            for x in player_balls:
                # if balls[x].player_ball:
                logging.info(
                    f"Player {x}: {tick} ticks, {player_balls[x].win_count} wins, {player_balls[x].loss_count} losses, {player_balls[x].ball_radius} size, Kills: {player_balls[x].kill_count}"
                )
                if (
                    not winner
                    or player_balls[x].kill_count > player_balls[winner].kill_count
                ):
                    winner = x
            if winner not in round_tally:
                round_tally[winner] = 0
            round_tally[winner] += 1
            logging.info(
                f"Leader: {player_balls[winner]} -- Total Round Won: {round_tally}"
            )
            # kills = [ [str(balls[x]),balls[x].kill_count] for x in balls.keys() if balls[x].player_ball ]
            kills = [
                [str(player_balls[x]), player_balls[x].kill_count]
                for x in player_balls.keys()
            ]
            logging.info(f"Kills Total: {kills}")
            most_recent_event = tick
            CREATE_BALLS = True
            game_round += 1
            total_balls = 50 * game_round
            logging.info(
                f"Beginning of round {game_round}. Dropping {total_balls} balls"
            )
            balls_to_drop = total_balls
            winnable = False
            max_cooldowns = game_round
            cooldown_count = 0
            for x in player_balls.keys():
                player_balls[x].ball_radius = 20
                player_balls[x].win_count = 0
                player_balls[x].loss_count = 0

        window.fill(pygame.Color(150, 200, 255))  # light pastel blue
        if tick % (7 * tick_speed) == 0:
            logging.debug(f"Total Balls in play: {len(balls.keys())}")

        xballs = balls.copy()
        xballs.update(player_balls)

        for k in balls.keys():
            ball = balls[k]
            action, collide_pos = ball.update(tick, window, xballs)
            if action == Action.CREATE:
                add_balls += [collide_pos]
            elif action == Action.DESTROY and not ball.player_ball:
                del_balls += [k]

        for k in player_balls.keys():
            player_balls[k].update(tick, window, xballs)

        if del_balls:
            for k in del_balls:
                if not balls[k].player_ball:
                    del balls[k]
                most_recent_event = tick
            del del_balls

        if add_balls and CREATE_BALLS:
            for pos in add_balls:
                # print(f"Creating a new ball at {pos}")
                new_ball = Ball(
                    *pos,
                    win_height=height,
                    win_width=width,
                    vel_x=rand.uniform(-5, 5),
                    ball_radius=rand.triangular(10, 20, 50),
                )
                balls[new_ball.id] = new_ball
                most_recent_event = tick
            del add_balls

        if balls_to_drop > 0 and tick % int(50 / game_round) == 0:
            logging.debug(f"Balls to drop {balls_to_drop} so dropping a ball")
            _pos = (0, 0)
            if balls_to_drop % 2 == 0:
                _pos = (1600, 0)
            new_ball = Ball(
                *_pos,
                win_height=height,
                win_width=width,
                vel_x=rand.uniform(-5, 5),
                ball_radius=rand.triangular(10, 20, 50),
            )
            balls[new_ball.id] = new_ball
            balls_to_drop -= 1

        pygame.display.update()

        clock.tick(int(tick_speed))
