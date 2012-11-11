#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A Robot orientating and moving towards a goal."""

####

import pygame as pyg
import random as rand
import math

####

DELTA = 1024
DELTA2 = DELTA // 2
PI2 = math.pi * 2

####

def make_alpha_z(delta=DELTA):
    """Setup function for converting angle in DELTA space to complex number."""
    steps = PI2 / delta

    def atz(alpha):
        """
        Args:
            alpha: 0 < alpha < DELTA
        Returns:
            Normalized complex number
        """
        return complex(math.cos(alpha * steps), math.sin(alpha * steps))

    return atz

####

alpha_to_z = make_alpha_z()

####

def get_delta_angle(pos, alpha, goal_pos):
    """Calculate angle between robot and goal.

    Args:
        pos: Position of robot in window space.
        alpha: Robot orientation.
        goal_position: <=

    Returns:
       Angle difference in Delta space.
    """

    alpha_direct = alpha_to_z(alpha)
    goal_direct = complex(goal_pos[0] - pos[0], goal_pos[1] - pos[1])

    # no need to normalize for atan2()
    try:
        zturn = (goal_direct / alpha_direct)
    except ZeroDivisionError:
        return 0

    # in pi space
    angle = math.atan2(zturn.imag, zturn.real)
    if angle < 0:
        angle = PI2 + angle

    # in DELTA space
    return int(DELTA * angle / PI2)

####

def norm2(x, y):
    """2D norm"""
    return math.sqrt(x*x + y*y)

####

def dirvec2(p0, p1):
    """Vector from p0 to p1."""
    vx, vy = p1
    wx, wy = p0
    x = vx - wx
    y = vy - wy

    denom = norm2(x, y)
    return x / denom, y / denom

####

def distance2(p0, p1):
    """Normalized direction vector from p0 to p1."""
    return norm2(p1[0] - p0[0], p1[1] - p0[1])

####

class PygView(object):
    """Pygame Output"""

    def __init__(self, controller, conf):
        """Setup Pygame window."""

        self.controller = controller
        self.width = conf['width']
        self.height = conf['height']
        self.backcol = conf['backcol']
        self.fps = conf['fps']
        self.quit_keys = pyg.K_ESCAPE, pyg.K_q

        pyg.init()
        self.canvas = pyg.display.set_mode((self.width, self.height), pyg.DOUBLEBUF)
        pyg.display.set_caption("Press ESC to exit.")
        self.clock = pyg.time.Clock()


    @property
    def frame_duration_secs(self):
        """Get frame seconds.

        (get_time() returns milliseconds)
        """
        return 0.001 * self.clock.get_time()


    def run(self):
        """Mainloop"""
        running = True
        while running:
            self.clock.tick_busy_loop(self.fps)
            running = self.dispatch_events()
            self.controller.process()
            self.flip()
        else:
            self.quit()


    def dispatch_events(self):
        """Check user input

        If user quits return False else True.
        """
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                return False
            if event.type == pyg.KEYDOWN:
                if event.key in self.quit_keys:
                    return False
        else:
            return True


    def set_color(self, rgb):

        self.act_color = rgb


    def shape(self, pts):

        pyg.draw.polygon(self.canvas, self.act_color,
                         [(int(x+0.5), int(y+0.5)) for x, y in pts])


    def flip(self):

        pyg.display.flip()
        self.canvas.fill(self.backcol)


    def quit(self):

        pyg.quit()

####

class Shape(object):
    """Drawing Information for a polygonal object."""

    def __init__(self, coords, color):

        self.coords = coords
        self.act_coords = list(coords[:])
        self.color = color
        self.pos = 0.0, 0.0
        self.alpha = 0
        self.dxy = 0.0, 0.0


    def translate_abs(self, tx, ty):

        self.pos = tx, ty


    def translate_rel(self, tx, ty):

        x, y = self.pos
        self.pos = x + tx, y + ty


    def rotate_rel(self, alpha):

        self.alpha = (int(self.alpha + alpha + 0.5)) % DELTA


    def draw(self, device, color=None):
        """Tranform and draw."""

        # Get complex number as rotation vector
        alpha_z = alpha_to_z(self.alpha)
        # Rotate points which are specified in definition space.
        rot_pts = [complex(*pt) * alpha_z for pt in self.coords]
        # Translate
        tx, ty = self.pos
        coords = [(x + tx, y + ty) for x, y in [(z.real, z.imag) for z in rot_pts]]

        # Draw
        device.set_color((color, self.color)[not color])
        device.shape(coords)

####

class Goal(Shape):
    """An object that transforms to a new location if reached."""

    def __init__(self, coords, conf):

        super(Goal, self).__init__(coords, conf['goal_col'])


    def random_trans(self, min_width, min_height, max_width, max_height):

        tx, ty = rand.randint(min_width, max_width), rand.randint(min_height, max_height)
        self.translate_abs(tx, ty)

####

class Robot(Shape):
    """The Goal Chaser"""

    def __init__(self, coords, conf):

        super(Robot, self).__init__(coords, conf['robot_col'])
        self.state = 'orientating'
        speed = conf['speed']
        dt = conf['dt']

        self.ang_step = conf['ang_step'] * speed
        self.ang_eps = conf['ang_eps'] * (speed * dt + 1)
        self.move_step = conf['move_step'] * speed
        self.move_eps = conf['move_eps'] * (speed * dt + 1)


    def reset(self):

        self.state = 'orientating'


    def orientate(self, dt, goal_pos):
        """Align robot towards goal in dt steps."""
        if self.state in ('goal', 'moving'):
            return

        if self.state == 'orientating':
            ang = get_delta_angle(self.pos, self.alpha, goal_pos)
            ang_eps = self.ang_eps
            if ang < ang_eps or (DELTA - ang) < ang_eps:
                self.state = 'orientated'
            else:
                # !!!
                if ang < DELTA2:
                    turn = dt * self.ang_step
                else:
                    turn = -dt * self.ang_step
                self.rotate_rel(turn)


    def move(self, dt, goal_pos):
        """Move robot to goal in dt steps."""
        if self.state in ('goal', 'orientating'):
            return

        if self.state == 'orientated':
            self.state = 'moving'
            self.old_distance = distance2(self.pos, goal_pos)
            zdirect = alpha_to_z(self.alpha)
            x, y = zdirect.real, zdirect.imag
            self.dxy = dt * x * self.move_step, dt * y * self.move_step

        if self.state == 'moving':
            self.translate_rel(*self.dxy)
            dist = distance2(self.pos, goal_pos)
            if dist < self.move_eps:
                self.state = 'goal'
            elif dist > self.old_distance:
                self.state = 'orientating'
            else:
                self.old_distance = dist


    def __repr__(self):

        return "{0} {1} {2}".format(self.pos, self.alpha, self.state)

####

class Simulation(object):
    """Model and Controller as one Class"""

    def __init__(self, view, conf):
        """Setup all stuff."""


        self.width = conf['width']
        self.height = conf['height']
        self.view = view(self, conf)
        # use a smaller area to place the goal
        self.area = map(int, (self.width * 0.1, self.height * 0.1,
                               self.width * 0.9, self.height * 0.9))

        self.goal = Goal(((10, 0), (0, 10), (-10, 0), (0, -10)), conf)
        self.robot = Robot(((20, 0), (-20, 20), (0, 0), (-20, -20)), conf)
        self.goal.random_trans(*self.area)
        self.robot.translate_abs(self.width // 2, self.height // 2)
        self.dtimer = IntegrationTimer(conf['dt'])


    def process(self):
        """Making all calculations here."""
        if self.robot.state == 'goal':
            self.goal.random_trans(*self.area)
            self.robot.reset()

        self.dtimer += self.view.frame_duration_secs
        self.dtimer.integrate(self.transform, self.goal.pos)
        self.goal.draw(self.view)
        self.robot.draw(self.view)
        #print self.robot


    def transform(self, dt, pos):
        """Calculate robot transformation per dt."""
        self.robot.orientate(dt, pos)
        self.robot.move(dt, pos)


    def run(self):

        self.view.run()

####

class IntegrationTimer(object):


    def __init__(self, dt):
        """Set calculation step per second."""
        self.dt = dt
        self.accu = 0.0


    def __iadd__(self, delta):
        """Update with elapsed time."""
        self.accu += delta
        return self


    def integrate(self, func, *args):
        """Execute func in accumulated time with step dt."""
        while self.accu >= self.dt:
            func(self.dt, *args)
            self.accu -= self.dt

####

CONFIG = {'width': 800,
          'height': 600,
          'backcol': (250, 250, 250),
          'robot_col': (0, 99, 199),
          'goal_col': (255, 0, 0),
          'fps': 200,     # Pygame clock ticks
          'speed': 200,   # the robot's speedfactor
          'dt': 0.001,    # samples per second
          'ang_step': 8,  # DELTA space
          'ang_eps': 4,   # DELTA space (start orientation)
          'move_step': 4, # screen space
          'move_eps': 8}  # screen space (goal proximity)

####

if __name__ == '__main__':

    Simulation(PygView, CONFIG).run()
