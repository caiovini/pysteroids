from constants import *

import pygame as pg
import pymunk as pm
import sys
import random

from assets import Asteroid, TypeImage, SpaceShip, Bullet
from os.path import join
from collections import deque
from enum import Enum

clock = pg.time.Clock()
space_step = 1/60


class SpawnSideAsteroid(Enum):
    LEFT = 0,
    RIGHT = 1


def main():

    font = pg.font.Font(join("fonts", "segoe-ui-symbol.ttf"), 20)
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption(TITLE)

    space = pm.Space()
    space.gravity = (0.0, 0.0)  # Define initial gravity

    random_type_images = (TypeImage.LARGE, TypeImage.MEDIUM, TypeImage.SMALL)
    generate_asteroid = ([False]*49)
    generate_asteroid.append(True)

    stars = [{"x": random.randint(0, SCREEN_WIDTH),
              "y": random.randint(0, SCREEN_HEIGHT),
              "radius": random.randint(1, 2), } for stars in range(RANGE_STARS)]

    spaceship = SpaceShip()
    spaceship.set_position(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

    space.add(spaceship.body)
    game_over, asteroids, bullets = False, [], deque()

    def add_bullet():

        bullet = Bullet()
        space.add(bullet.body)
        bullets.appendleft(bullet)  # Equip

    def process_asteroids_and_check_collisions(ast, bullets):

        nonlocal game_over

        screen.blit(ast.image, ast.body.position)
        ast.set_position(*ast.body.position)
        if not game_over:
            ast.spin()

        if spaceship.rect.colliderect(pg.Rect(ast.rect.x, ast.rect.y,
                                              ast.rect.w//2, ast.rect.h//2)):
            game_over = True
            label = font.render(
                "YOU LOST !!!", 1, YELLOW)
            screen.blit(label, (SCREEN_WIDTH // 2.5, SCREEN_HEIGHT // 2))

            return

        for bullet in list(bullets)[1:]:
            if bullet.rect.colliderect(ast.rect):
                bullet.did_collide = True
                return ast

    add_bullet()
    done = False
    while not done:

        if random.choice(generate_asteroid):
            asteroid = Asteroid(random.choice(random_type_images))
            impulse_x, impulse_y = 3000, 1000

            if random.choice([SpawnSideAsteroid.LEFT, SpawnSideAsteroid.RIGHT]) == SpawnSideAsteroid.LEFT:

                asteroid.set_position(-asteroid.rect.w,
                                      random.randint(0, SCREEN_HEIGHT))
                asteroid.body.apply_impulse_at_local_point(
                    (impulse_x, impulse_y), (0, 0))

            else:
                asteroid.set_position(
                    SCREEN_WIDTH+asteroid.rect.w, random.randint(0, SCREEN_HEIGHT))
                asteroid.body.apply_impulse_at_local_point(
                    (-impulse_x, -impulse_y), (0, 0))

            space.add(asteroid.body)
            asteroids.append(asteroid)

        screen.fill(BLACK)
        for star in stars:
            pg.draw.circle(
                screen, WHITE, (star["x"], star["y"]), star["radius"], width=0)

        for event in pg.event.get():

            if event.type == pg.QUIT:
                done = True

            if event.type == pg.KEYDOWN:

                if event.key == pg.K_ESCAPE:
                    done = True

                if event.key == pg.K_SPACE and not game_over:

                    bullets[0].shoot(spaceship)
                    add_bullet()

        if not game_over:
            keys = pg.key.get_pressed()
            if keys[pg.K_UP]:
                dist_x, dist_y = spaceship.get_distance_to_apply_force(
                    speed=10000)
                spaceship.body.apply_force_at_local_point(
                    (dist_x, dist_y), (0, 0))

            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT]:
                spaceship.rotate(-1)

            if keys[pg.K_RIGHT]:
                spaceship.rotate(1)

        if not(0 < spaceship.body.position[0] < SCREEN_WIDTH):

            if spaceship.body.position[0] > SCREEN_WIDTH:
                spaceship.set_position(x=-spaceship.rect.w)

            if spaceship.body.position[0] < (-spaceship.rect.w):
                spaceship.set_position(x=SCREEN_WIDTH)

        if not(0 < spaceship.body.position[1] < SCREEN_HEIGHT):

            if spaceship.body.position[1] < -spaceship.rect.h:
                spaceship.set_position(y=SCREEN_HEIGHT)

            if spaceship.body.position[1] > SCREEN_HEIGHT:
                spaceship.set_position(y=-spaceship.rect.h)

        bullets_for_exclusion = []
        for bullet in list(bullets)[1:]:  # Skip first bullet

            if not(0 < bullet.body.position[1] < SCREEN_HEIGHT) or \
                not(0 < bullet.body.position[0] < SCREEN_WIDTH) or \
                    bullet.did_collide:

                bullets_for_exclusion.append(bullet)
            else:
                screen.blit(bullet.image, bullet.body.position)
                bullet.set_position(*bullet.body.position)

        [bullets.remove(b) for b in bullets_for_exclusion]

        asteroids_for_exclusion = filter(lambda x: x,
                                         [process_asteroids_and_check_collisions(ast, bullets) for ast in asteroids])

        for a in asteroids_for_exclusion:

            if a.type_image == TypeImage.LARGE or \
                    a.type_image == TypeImage.MEDIUM:

                for i in range(1, -2, -2):
                    asteroid = Asteroid(TypeImage.MEDIUM
                                        if a.type_image == TypeImage.LARGE
                                        else TypeImage.SMALL)
                    asteroid.set_position(*a.body.position)
                    asteroid.body.apply_impulse_at_local_point(
                        (random.choice([-1500, 1500]), i*3000), (0, 0))
                    space.add(asteroid.body)
                    asteroids.append(asteroid)

            asteroids.remove(a)
            space.remove(a.body)

        screen.blit(spaceship.image, spaceship.body.position)

        if not game_over:
            space.step(space_step)
        spaceship.set_position(*spaceship.body.position)
        bullets[0].set_position(spaceship.body.position[0] + 40,
                                spaceship.body.position[1] + 40)

        del asteroids_for_exclusion
        del bullets_for_exclusion
        pg.display.flip()
        clock.tick(30)  # FPS


if __name__ == "__main__":
    pg.init()
    sys.exit(main())
