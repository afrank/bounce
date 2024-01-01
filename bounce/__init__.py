import pygame
import random as rand
from pygame.math import Vector2
from enum import Enum
import uuid
import logging

colors = {
    "PINK": (289, 38, 98, 77),
    # "TEAL": (169, 62, 97, 22),
    "BLUE": (217, 83, 59, 22),
    "BROWN": (4, 28, 38, 52),
    "BLACK": (0, 0, 0, 0),
    "RED": (356, 86, 58, 46),
    "KHAKI": (90, 15, 53, 90),
    "GREEN": (104, 79, 82, 94),
    "ORANGE": (23, 68, 63, 5),
}

class Action(Enum):
    DONOTHING = 1
    DESTROY = 2
    CREATE = 3


def avg(lst):
    return sum(lst) / len(lst)


class Ball:
    def __init__(
        self,
        x,
        y,
        win_height,
        win_width,
        vel_x=1,
        vel_y=0,
        accel=(0, 0.3),
        ball_radius=20,
        player_ball=False,
        color=None,
    ):
        self.id = str(uuid.uuid4())
        self.pos = Vector2(x, y)
        self.vel = Vector2(vel_x, vel_y)
        self.acc = Vector2(accel)
        self.ball_radius = ball_radius
        self.fc = pygame.Color(200, 50, 50) # RED
        self.bc = pygame.Color(30, 30, 30) # GREY
        self.min_collisions = 5
        self.max_collisions = 10
        self.max_slow_collisions = 1000
        self.collision_count = 0
        self.slow_collision_count = 0
        self.win_count = 0
        self.loss_count = 0
        self.collision_velocity_threshold = (
            3  # vel. threshold to consider a collision a collision
        )
        self.player_ball = player_ball  # a player ball cannot be destroyed
        self.hsva = (0, 0, 0, 0)
        self.kill_count = 0
        self.win_height = win_height
        self.win_width = win_width

        if color:
            # h = rand.choice(range(0,360))
            # s = rand.choice(range(0,100))
            # v = rand.choice(range(0,100))
            # a = rand.choice(range(0,100))
            # self.hsva = (h,s,v,a)
            ##color = rand.choice([ x for x in colors.keys() if x not in selected_colors ])
            ##self.hsva = colors[color]
            self.id = color
            self.hsva = colors[color]
            logging.info(f"Creating ball with color {color}")

    def __str__(self):
        return str(self.id)

    def draw_ball(self, window):
        if self.player_ball:
            self.fc.hsva = self.hsva
        else:
            speed_color = self.vel.magnitude()
            speed_color *= 13
            if speed_color >= 359:
                speed_color = 359
            self.fc.hsva = (int(speed_color), 90, 100, 100)

        pygame.draw.circle(
            window, self.bc, (self.pos.x, self.pos.y), self.ball_radius
        )  # border
        pygame.draw.circle(
            window, self.fc, (self.pos.x, self.pos.y), self.ball_radius - 2
        )  # face

    def check_ball_collision(self, ball):
        distance = (self.pos - ball.pos).magnitude_squared()
        return distance < (self.ball_radius + ball.ball_radius) ** 2

    def calculate_ball_collision(self, ball):
        vel_diff = self.vel - ball.vel
        pos_diff = self.pos - ball.pos
        try:
            self.pos -= (
                0.5
                * (pos_diff.magnitude() - (self.ball_radius + ball.ball_radius))
                * pos_diff.normalize()
            )
            ball.pos += (
                0.5
                * (pos_diff.magnitude() - (self.ball_radius + ball.ball_radius))
                * pos_diff.normalize()
            )
            self.vel -= ((vel_diff).dot(pos_diff) / (pos_diff).magnitude_squared()) * (
                pos_diff
            )  # + self.acc
            ball.vel -= (
                (-vel_diff).dot(-pos_diff) / (-pos_diff).magnitude_squared()
            ) * (
                -pos_diff
            )  # + ball.acc
        except:
            pass

        # velocity lost from collisions
        self.vel *= 1
        ball.vel *= 1

        self_won = True
        if avg(ball.vel) * ball.ball_radius > avg(self.vel) * self.ball_radius:
            self_won = False

        return self_won

    def update(self, tick, window, xballs):
        collide_pos = []
        action = Action.DONOTHING

        # for k in list(balls.keys()) + list(player_balls.keys()):
        for k in xballs.keys():
            ball = xballs[k]
            if not ball:
                continue
            if ball is self:
                pass
            elif self.check_ball_collision(ball):
                # another ball has collided with our ball
                self_won = self.calculate_ball_collision(ball)
                velo = abs(avg(self.vel))
                if velo >= self.collision_velocity_threshold:
                    self.collision_count += 1
                    if self_won:
                        self.win_count += 1
                        self.vel *= 1.01
                        self.ball_radius += 5
                        if self.ball_radius > 150:
                            self.ball_radius = 150
                    else:
                        self.loss_count += 1
                        ball.vel *= 1.01
                        self.ball_radius -= 5
                        if self.ball_radius < 5:
                            self.ball_radius = 5
                        if (
                            self.slow_collision_count >= self.max_slow_collisions
                            or self.collision_count >= self.max_collisions
                        ):
                            ball.kill_count += 1

                    logging.debug(
                        f"Ball {self} now has {self.collision_count} collisions and radius {self.ball_radius} Wins: {self.win_count} Losses: {self.loss_count}"
                    )
                    if (
                        self.collision_count >= self.min_collisions
                        and self.collision_count < self.max_collisions
                    ):
                        collide_pos += [tuple([int(x) for x in self.pos])]
                else:
                    self.slow_collision_count += 1
                    logging.debug(
                        f"Ball {self} now has {self.slow_collision_count} SLOW collisions"
                    )
        if (
            self.slow_collision_count >= self.max_slow_collisions
            or self.collision_count >= self.max_collisions
        ):
            action = Action.DESTROY
        elif collide_pos and rand.choice(range(3)) == 0:
            collide_pos = collide_pos[0]
            action = Action.CREATE
        self.check_border_collision()
        self.vel += self.acc
        self.pos += self.vel
        self.draw_ball(window)
        return action, collide_pos

    def check_border_collision(self):
        if (
            self.pos.y >= self.win_height - self.ball_radius and self.vel.y > 0
        ):  # check bottom border
            self.vel.y = -self.vel.y - 0.5 * self.acc.y
            self.pos.y = self.win_height - self.ball_radius
        elif self.pos.y <= 0 + self.ball_radius and self.vel.y < 0:  # check top border
            self.vel.y = -self.vel.y - 0.5 * self.acc.y
            self.pos.y = self.ball_radius

        if (
            self.pos.x >= self.win_width - self.ball_radius and self.vel.x > 0
        ):  # check right border
            self.vel.x = -self.vel.x - 0.5 * self.acc.x
            self.pos.x = self.win_width - self.ball_radius
        elif self.pos.x <= 0 + self.ball_radius and self.vel.x < 0:  # check left border
            self.vel.x = -self.vel.x - 0.5 * self.acc.x
            self.pos.x = self.ball_radius
