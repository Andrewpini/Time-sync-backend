import random


class CurveObj:

    def __init__(self, curve):
        self.curve = curve
        self.buffer_x = list()
        self.buffer_y = list()

    def add_single_sample(self, x_sample, y_sample):
        self.buffer_x.append(x_sample)
        self.buffer_y.append(y_sample)

    def add_multiple_samples(self, x_samples, y_samples):
        self.buffer_x += x_samples
        self.buffer_y += y_samples


def create_semi_random_color(low_limit, high_limit, alpha):
    color_tuple = (low_limit, high_limit, random.randint(low_limit, high_limit))
    color_tuple = random.sample(color_tuple, len(color_tuple))
    color_tuple += (alpha,)
    return color_tuple


def add_new_curve(pl_obj, name):
    color = create_semi_random_color(94, 255, 255)
    return CurveObj(pl_obj.plot(pen=color, name=name))

