#!/usr/bin/env python

####

import pygame as pyg
import random as rand
import math

####

DELTA = 1024
DELTA2 = DELTA // 2
PI2 = math.pi * 2

####

def make_alpha_complex(delta=DELTA):

    steps = PI2 / delta

    def atc(alpha):

        return complex(math.cos(alpha * steps), math.sin(alpha * steps))

    return atc

####

alpha_to_complex = make_alpha_complex()

####

def get_angle(pos, alpha, goal_pos):

    zang = alpha_to_complex(alpha)
    zgoal = complex(goal_pos[0] - pos[0], goal_pos[1] - pos[1])

    # fuer atan2() muss zgoal nicht normiert werden
    try:
        zgoal = (zgoal / zang)   # / abs(zgoal)) / zang
    except ZeroDivisionError:
        return 0

    angle = math.atan2(zgoal.imag, zgoal.real)
    if angle < 0:
        angle = PI2 - angle

    return int(DELTA * angle / PI2)

####

def norm2(x, y):

    return math.sqrt(x*x + y*y)

####

def dirvec2(p0, p1):

    vx, vy = p1
    wx, wy = p0
    x = vx - wx
    y = vy - wy

    denom = norm2(x, y)
    return x / denom, y / denom

####

def distance2(p0, p1):

    return norm2(p1[0] - p0[0], p1[1] - p0[1])

####

class PygView(object):


    def __init__(self, controller, width, height, fps, backcol=(250, 250, 250)):

        self.controller = controller
        self.width = width
        self.height = height
        self.backcol = backcol
        self.fps = fps
        self.quit_keys = pyg.K_ESCAPE, pyg.K_q

        pyg.init()
        self.canvas = pyg.display.set_mode((width, height), pyg.DOUBLEBUF)
        pyg.display.set_caption("Press Esc to exit")
        self.clock = pyg.time.Clock()


    @property
    def frame_duration_secs(self):

        return 0.001 * self.clock.get_time()


    def run(self):

        running = True
        while running:
            self.clock.tick_busy_loop(self.fps)
            running = self.dispatch_events()
            self.controller.process()
            self.flip()
        else:
            self.quit()


    def dispatch_events(self):

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

    __slots__ = ['coords', 'act_coords', 'color', 'pos', 'alpha']

    def __init__(self, coords, color):

        self.coords = coords
        self.act_coords = list(coords[:])
        self.color = color
        self.pos = (0.0, 0.0)
        self.alpha = 0.0


    def translate_abs(self, tx, ty):

        self.pos = tx, ty


    def translate_rel(self, tx, ty):

        x, y = self.pos
        self.pos = x + tx, y + ty


    def rotate_abs(self, alpha):

        self.alpha = alpha


    def rotate_rel(self, alpha):

        self.alpha += alpha


    def draw(self, device, color=None):

        alpha_z = alpha_to_complex(self.alpha)
        rot_pts = [complex(*pt) * alpha_z for pt in self.coords]
        tx, ty = self.pos
        coords = [(x + tx, y + ty) for x, y in [(z.real, z.imag) for z in rot_pts]]

        device.set_color((color, self.color)[not color])
        device.shape(coords)

####

class Goal(Shape):


    def random_trans(self, min_width, min_height, max_width, max_height):

        tx, ty = rand.randint(min_width, max_width), rand.randint(min_height, max_height)
        self.translate_abs(tx, ty)

####

class Robot(Shape):

    __slots__ = ['state', 'ang_step', 'ang_eps', 'move_step', 'move_eps', 'dx', 'dy']

    def __init__(self, coords, color, speed,
                 ang_step=2, ang_eps=2, move_step=1, move_eps=1):

        Shape.__init__(self, coords, color)
        self.state = 'orientating'
        self.ang_step = ang_step * speed
        self.ang_eps = ang_eps * (speed * dt + 1)
        self.move_step = move_step * speed
        self.move_eps = move_eps * (speed * dt + 1)


    def reset(self):

        self.state = 'orientating'


    def orientate(self, dt, goal_pos):

        if self.state in ('goal reached', 'moving'):
            return

        if self.state == 'orientating':
            ang = get_angle(self.pos, self.alpha, goal_pos)
            if abs(ang) < self.ang_eps:
                self.state = 'orientation ok'
            else:
                # hier ist der Knackpunkt!
                self.rotate_rel((-dt * self.ang_step, dt * self.ang_step)[ang < DELTA2])


    def move(self, dt, goal_pos):

        if self.state in ('goal reached', 'orientating'):
            return

        if self.state == 'orientation ok':
            self.state = 'moving'
            x, y = dirvec2(self.pos, goal_pos)
            self.dx, self.dy = dt * x * self.move_step, dt * y * self.move_step

        if self.state == 'moving':
            self.translate_rel(self.dx, self.dy)
            if distance2(goal_pos, self.pos) < self.move_eps:
                self.state = 'goal reached'

####

class Controller(object):


    def __init__(self, view, width, height, dt, speed, fps=200):

        self.width = width
        self.height = height
        self.areal = map(int, (width * 0.1, height * 0.1, width * 0.9, height * 0.9))
        self.view = view(self, width, height, fps)
        self.goal = Goal(((10, 0), (0, 10), (-10, 0), (0, -10)), (255, 0, 0))
        self.robot = Robot(((20, 0), (-20, 20), (0, 0), (-20, -20)), (0, 99, 199), speed)

        self.goal.random_trans(*self.areal)
        self.robot.translate_abs(width // 2, height // 2)

        self.dtimer = DeltaTimer(dt)
        #self.fps = fps
        #self.dt = dt


    def process(self):

        if self.robot.state == 'goal reached':
            self.goal.random_trans(*self.areal)
            self.robot.reset()

        self.goal.draw(self.view)
        self.dtimer += self.view.frame_duration_secs
        self.dtimer.integrate(self.transform, self.goal.pos)
        self.robot.draw(self.view)


    def transform(self, dt, pos):

        self.robot.orientate(dt, pos)
        self.robot.move(dt, pos)


    def run(self):

        self.view.run()

####

class DeltaTimer(object):


    def __init__(self, dt):

        self.dt = dt
        self.accu = 0.0


    def __iadd__(self, delta):

        self.accu += delta
        return self


    def integrate(self, func, *args):

        while self.accu >= self.dt:
            func(self.dt, *args)
            self.accu -= self.dt

####

if __name__ == '__main__':

    # how often a sample of the simulation is rendered
    FPS = 600
    # the robot's speedfactor
    SPEED = 200
    # step for mathematical calculation of movement
    dt = 0.002
    Controller(PygView, 800, 600, dt, SPEED, FPS).run()
