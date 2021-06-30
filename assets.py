import pygame as pg
import pymunk as pm
import math

from enum import Enum
from itertools import cycle
from collections import deque
from os.path import join

_large_asteroid_path = join("assets", "asteroids", "large")
_medium_asteroid_path = join("assets", "asteroids", "medium")
_small_asteroid_path = join("assets", "asteroids", "small")

_spaceship_path = join("assets", "spaceship", "nightraiderfixed.png")
_light_bullet_path = join("assets", "bullets", "light_bullet.png")


class TypeImage(Enum):
    LARGE = 0,
    MEDIUM = 1,
    SMALL = 2


class _Sprite(pg.sprite.Sprite):

    def __init__(self, image):
        pg.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.body = pm.Body(mass=10,
                            moment=pm.moment_for_circle(mass=10, inner_radius=0, outer_radius=self.rect.h))
        self.body.position = self.rect.x, self.rect.y

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y


class Asteroid(_Sprite):

    def __init__(self, type_image):

        self.type_image = type_image

        r = range(10000, 10016)
        self.index = cycle(range(0, len(r)))
        self.large_images = []
        self.medium_images = []
        self.small_images = []

        if self.type_image == TypeImage.LARGE:
            self.large_images = self.\
                load_images(
                    [join(_large_asteroid_path, f"a{img}.png") for img in r])

        elif self.type_image == TypeImage.MEDIUM:
            self.medium_images = self.\
                load_images(
                    [join(_medium_asteroid_path, f"a{img}.png") for img in r])

        else:
            self.small_images = self.\
                load_images(
                    [join(_small_asteroid_path, f"a{img}.png") for img in r])

        super().__init__(self.get_list_images()[next(self.index)])

    def spin(self):
        self.image = self.get_list_images()[next(self.index)]

    def get_list_images(self):
        return {TypeImage.LARGE: self.large_images,
                TypeImage.MEDIUM: self.medium_images,
                TypeImage.SMALL: self.small_images}.get(self.type_image)

    @property
    def type_image(self):
        return self.__type_image

    @type_image.setter
    def type_image(self, value):
        assert type(value) == TypeImage
        self.__type_image = value

    def load_images(self, images):
        return [pg.image.load(img) for img in images]

    def set_position(self, x, y):
        self.body.position = x, y
        super().set_position(x, y)


class SpaceShip(_Sprite):

    def __init__(self):

        image = pg.transform.scale(pg.image.load(_spaceship_path), (100, 100))
        self.rotate_image = image
        self.angle = deque(range(0, 370, 10))
        super().__init__(image)

    def rotate(self, speed):

        self.angle.rotate(speed)
        orig_rect = self.image.get_rect()
        rot_image = pg.transform.rotate(self.rotate_image, self.angle[0])
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        self.image = rot_image.subsurface(rot_rect).copy()

    def get_distance_to_apply_force(self, *, speed):

        x = self.body.position[0] + \
            math.cos(math.radians(360 - self.angle[0])) * speed
        dist_x = (x - self.body.position[0])
        y = self.body.position[0] + \
            math.sin(math.radians(360 - self.angle[0])) * speed
        dist_y = (y - self.body.position[1])

        return dist_x, dist_y

    def set_position(self, x=None, y=None):

        x = x if x else self.body.position[0]
        y = y if y else self.body.position[1]

        self.body.position = x, y
        super().set_position(x, y)


class Bullet(_Sprite):

    def __init__(self):
        image = pg.transform.scale(pg.image.load(_light_bullet_path), (20, 20))
        self.did_collide = False
        super().__init__(image)

    def shoot(self, spaceship):

        dist_x, dist_y = spaceship.get_distance_to_apply_force(speed=150000)
        self.body.apply_force_at_local_point((dist_x, dist_y), (0, 0))

    def set_position(self, x, y):
        self.body.position = x, y
        super().set_position(x, y)
