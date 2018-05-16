from turtle import *
from math import sin, cos, pi, radians


# set color mode is rgb
colormode(255)


class Turtle(Turtle):
    '''
    turtle-plus

    Public attributes:
    - ellipse: Draw a ellipse.
    - save: Save the window as png.
    '''

    def __init__(self):
        super().__init__()
        self.shape('turtle')

    def ellipse(self, x_radius: int, y_radius: int, rads=360, steps=60):
        '''
        Draw a ellipse with long axis and short axis

        :param x_radius: short axis
        :param y_radius: long axis
        :param rads:
        :param steps:
        '''

        heading_radians = radians(self.heading())
        theta_radians = -pi / 2
        extent_radians = 2 * pi
        step_radians = extent_radians / steps
        extent_radians += theta_radians
        x_center, y_start = self.position()
        y_center = y_start + y_radius

        cos_heading, sin_heading = cos(
            heading_radians), sin(heading_radians)

        # 60 is circle
        count = 0
        while True:
            x, y = x_center + cos(theta_radians) * \
                x_radius, y_center + sin(theta_radians) * y_radius
            # original heading of the turtle
            x, y = x - x_center, y - y_start
            x, y = x * cos_heading - y * sin_heading, x * sin_heading + y * cos_heading
            x, y = x + x_center, y + y_start

            # turtle faces direction in which ellipse is drawn
            self.setheading(self.towards(x, y))
            self.goto(x, y)

            # theta_radians >> extent_radians
            if theta_radians == extent_radians:
                break
            # control count
            if count * 6 >= rads:
                break

            # don't overshoot our starting point
            theta_radians = min(
                theta_radians + step_radians,
                extent_radians)

            count += 1

        # set correct heading for the next thing we draw
        self.setheading(self.towards(x_center, y_start))

    def save(self, filename: str):
        '''
        Save the window as png.

        :param filename: filename
        TODO: Cannot save background color for a while.
        '''
        import canvasvg
        import cairosvg

        screen = self.getscreen().getcanvas()
        svgname = ''.join([filename, '.svg'])
        pngname = ''.join([filename, '.png'])
        canvasvg.saveall(svgname, screen)
        cairosvg.svg2png(url=svgname, write_to=pngname)


Pen = Turtle