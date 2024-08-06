
import math, numpy, env


def frange(begin, end, step):
    """
    Makes float range generator

    :param begin: float: value to begin with
    :param end: value to end with
    :param step: value to increase with
    :type begin: float
    :type end: float
    :type step: float
    :return: generator
    """
    while begin < end:
        yield begin
        begin += step


def intersects(line1, line2):
    ax, ay, bx, by = line1[0][0], line1[0][1], line1[1][0], line1[1][1]
    cx, cy, dx, dy = line2[0][0], line2[0][1], line2[1][0], line2[1][1]

    if env.DEBUG_SHOW_POINTS:
        env.DEBUG_POINTS.append((ax, ay))
        env.DEBUG_POINTS.append((bx, by))
        env.DEBUG_POINTS.append((cx, cy))
        env.DEBUG_POINTS.append((dx, dy))

    u = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
    if u == 0.0:
        return False
    else:
        r = ((ay - cy) * (dx - cx) - (ax - cx) * (dy - cy)) / u
        s = ((ay - cy) * (bx - ax) - (ax - cx) * (by - ay)) / u
        return 0.0 < r < 1.0 and 0.0 < s < 1.0


def mass_intersects(lines1, lines2):
    for line1 in lines1:
        for line2 in lines2:
            if intersects(line1, line2):
                return True
    return False


def transform_point(point, ang, pos=(0, 0), scale=1.0):
    """
    Rotate, move and scale given point

    :param point: Point as tuple or list with 0 for x and 1 for y
    :param ang:
    :param pos:
    :param scale:
    :return:
    """
    cosa = math.cos(ang)
    sina = math.sin(ang)
    return (
        pos[0] + (point[0] * cosa - point[1] * sina) * scale,
        pos[1] + (point[0] * sina + point[1] * cosa) * scale
    )


def transform_points(points, ang, pos=(0, 0), scale=1.0):
    """
    Rotate, move and scale given list of points. Return a new list.

    :param points:
    :param ang:
    :param pos:
    :param scale:
    :return:
    """
    cosa = math.cos(ang)
    sina = math.sin(ang)
    transformed_points = list()
    for point in points:
        transformed_points.append((
            pos[0] + (point[0] * cosa - point[1] * sina) * scale,
            pos[1] + (point[0] * sina + point[1] * cosa) * scale
        ))
    return transformed_points


def circle_points(radius, amount):
    points = list()
    for a in frange(0, 2 * math.pi, 2 * math.pi / amount):
        points.append((radius * math.cos(a), radius * math.sin(a)))
    return points
