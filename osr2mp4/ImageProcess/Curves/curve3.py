import bisect
import math
from itertools import accumulate

import numpy as np
from scipy.special import comb
from toolz import sliding_window
try:
    from .abec import ABCMeta, abstractmethod
    from .position import Position
    from .utils import lazyval
except:
	from abec import ABCMeta, abstractmethod
	from position import Position
	from utils import lazyval


class Curve(metaclass=ABCMeta):
    """Curves are functions that define the path that a slider takes from start
    to stop.

    Parameters
    ----------
    points : list[Position]
        The positions of the control points.
    req_length : float
        The pixel length of the curve.
    """
    def __init__(self, points, req_length):
        self.points = points
        self.req_length = req_length

    @classmethod
    def from_kind_and_points(cls, kind, points, req_length):
        if kind == 'B':
            return MultiBezier(points, req_length)
        if kind == 'L':
            return LinearB(points, req_length)
        if kind == 'C':
            return Catmull(points, req_length)
        if kind == 'P':
            if len(points) != 3:
                # it seems osu! uses the bezier curve if there are more than 3
                # points
                # https://github.com/ppy/osu/blob/7fbbe74b65e7e399072c198604e9db09fb729626/osu.Game/Rulesets/Objects/SliderCurve.cs#L32  # noqa
                return MultiBezier(points, req_length)

            try:
                center = get_center(*points)
            except ValueError:
                # we cannot use a perfect curve function for collinear points;
                # osu! also falls back to a bezier here
                return MultiBezier(points, req_length)

            return PerfectB(points, req_length, _center=center)

        raise ValueError(f'unknown curve kind: {kind!r}')

    @abstractmethod
    def __call__(self, t):
        """Compute the position of the curve at time ``t``.

        Parameters
        ----------
        t : float
            The time along the distance of the curve in the range [0, 1]

        Returns
        -------
        position : Position
            The position of the curve.
        """
        raise NotImplementedError('__call__')

    @lazyval
    def hard_rock(self):
        """This curve when played with hard rock.
        """
        return type(self)(
            [Position(p.x, 384 - p.y) for p in self.points],
            self.req_length,
        )


class Bezier(Curve):
    """Bezier curves of degree ``len(points)``.

    Parameters
    ----------
    points : list[Position]
        The positions of the control points.
    req_length : float
        The pixel length of the curve.
    """
    def __init__(self, points, req_length):
        super().__init__(points, req_length)
        self._coordinates = np.array(points).T

    def __call__(self, t):
        coordinates = self.at(t * (self.req_length / self.length))
        return Position(coordinates[0, 0], coordinates[0, 1])

    def at(self, t):
        """Compute the positions of the bezier curve for a sequence of times
        from 0 to 1.

        Parameters
        ----------
        t : np.ndarray
            The times to compute for.

        Returns
        -------
        coordinates : np.ndarray
            A two dimensional array of shape (len(t), 2) where the first column
            holds the x coordinate at time t and the second column holds the y
            coordinate at time t.
        """
        t = np.asarray(t).reshape(-1, 1)

        points = self.points

        n = len(points) - 1
        ixs = np.arange(n + 1)
        return np.sum(
            (
                comb(n, ixs) *
                (1 - t) ** (n - ixs) *
                t ** ixs
            )[:, np.newaxis] *
            self._coordinates,
            axis=-1,
        )

    @lazyval
    def length(self):
        """Approximates length as piecewise linear function.
        """
        # NOTE: if the error is high, try increasing the samples
        points = self.at(np.linspace(0, 1, 50))
        return np.sum(
            np.sqrt(
                np.sum(
                    np.square(
                        np.diff(points, axis=0),
                    ),
                    axis=1,
                ),
            ),
        )


class _MetaCurveMixin:
    """Mixin for defining curves which are collections of other curves.

    Implementers must provide a ``_curves`` attribute which is the collection
    of curves.
    """
    @lazyval
    def _ts(self):
        lengths = [c.length for c in self._curves]
        length = sum(lengths)
        out = []
        for i, j in enumerate(accumulate(lengths[:-1])):
            self._curves[i].req_length = lengths[i]
            out.append(j / length)
        self._curves[-1].req_length = max(
            0,
            lengths[-1] - (length - self.req_length),
        )
        out.append(1)
        return out

    def __call__(self, t):
        ts = self._ts
        if len(self._curves) == 1:
            # Special case where we only have one curve
            return self._curves[0](t)

        bi = bisect.bisect_left(ts, t)
        if bi == 0:
            pre_t = 0
        else:
            pre_t = ts[bi - 1]

        post_t = ts[bi]

        return self._curves[bi]((t - pre_t) / (post_t - pre_t))


class MultiBezier(_MetaCurveMixin, Curve):
    """MultiBezier is a collection of `:class:~slider.curve.Bezier` curves
    stitched together at the ends.

    Parameters
    ----------
    points : list[Position]
        The positions of the control points.
    req_length : float
        The pixel length of the curve.
    """
    def __init__(self, points, req_length):
        super().__init__(points, req_length)

        self._curves = [
            Bezier(subpoints, None)
            for subpoints in self._split_at_dupes(points)
        ]

    @staticmethod
    def _split_at_dupes(input_):
        """Split a sequence of points on duplicates.

        Parameters
        ----------
        inp : list[any]
            The input sequence to split.

        Yields
        ------
        group : list[any]
            The groups split on duplicates.
        """
        old_ix = 0
        for n, (a, b) in enumerate(sliding_window(2, input_), 1):
            if a == b:
                yield input_[old_ix:n]
                old_ix = n

        tail = input_[old_ix:]
        if tail:
            yield tail


class LinearB(_MetaCurveMixin, Curve):
    """Linear curves traverse the line segments between the given points.

    Parameters
    ----------
    points : list[Position]
        The positions of the control points.
    req_length : float
        The pixel length of the curve.
    """
    def __init__(self, points, req_length):
        super().__init__(points, req_length)

        self._curves = [
            Bezier(subpoints, None) for subpoints in sliding_window(2, points)
        ]


class PerfectB(Curve):
    """Perfect curves traverse the circumference of the circle that passes
    through the given points.

    Parameters
    ----------
    points : list[Position]
        The positions of the control points.
    req_length : float
        The pixel length of the curve.
    """
    def __init__(self, points, req_length, *, _center=None):
        # NOTE: _center exists as an optimization to not recompute the center
        # of the circle when calling ``Curve.from_kind_and_points``.
        self.points = points
        self.req_length = req_length

        if _center is None:
            _center = get_center(*points)

        self._center = _center

        coordinates = np.array(points) - _center

        # angles of 3 points to center
        start_angle, end_angle = np.arctan2(
            coordinates[::2, 1],
            coordinates[::2, 0],
        )

        # normalize so that self._angle is positive
        if end_angle < start_angle:
            end_angle += 2 * math.pi

        # angle of arc sector that describes slider
        self._angle = end_angle - start_angle

        # switch angle direction if necessary
        a_to_c = coordinates[2] - coordinates[0]
        ortho_a_to_c = np.array((a_to_c[1], -a_to_c[0]))
        if np.dot(ortho_a_to_c, coordinates[1] - coordinates[0]) < 0:
            self._angle = -(2 * math.pi - self._angle)

        length = abs(
            self._angle *
            math.sqrt(coordinates[0][0] ** 2 + coordinates[0][1] ** 2),
        )
        if length > req_length:
            self._angle *= req_length / length

    def __call__(self, t):
        return rotate(self.points[0], self._center, self._angle * t)


class Catmull(Curve):
    """Catmull curves implement the Catmull-Rom spline algorithm for defining
    the path.
    """
    def __call__(self, t):
        raise NotImplementedError('catmull positions not supported yet')


def get_center(a, b, c):
    """Returns the Position of the center of the circle described by the 3
    points

    Parameters
    ----------
    a, b, c : Position
        The three positions.

    Returns
    -------
    center : Position
        The center of the three points.

    Notes
    -----
    This uses the same algorithm as osu!
    https://github.com/ppy/osu/blob/7fbbe74b65e7e399072c198604e9db09fb729626/osu.Game/Rulesets/Objects/CircularArcApproximator.cs#L23  # noqa
    """
    a, b, c = np.array([a, b, c], dtype=np.float64)

    a_squared = np.sum(np.square(b - c))
    b_squared = np.sum(np.square(a - c))
    c_squared = np.sum(np.square(a - b))

    if np.isclose([a_squared, b_squared, c_squared], 0).any():
        raise ValueError(f'gfiven points are collinear: {a}, {b}, {c}')

    s = a_squared * (b_squared + c_squared - a_squared)
    t = b_squared * (a_squared + c_squared - b_squared)
    u = c_squared * (a_squared + b_squared - c_squared)

    sum_ = s + t + u

    if np.isclose(sum_, 0):
        raise ValueError(f'givenf points are collinear: {a}, {b}, {c}')

    return Position(*(s * a + t * b + u * c) / sum_)


def rotate(position, center, radians):
    """Returns a Position rotated r radians around centre c from p
    Parameters
    ----------
    position : Position
        The position to rotate.
    center : Position
        The point to rotate about.
    radians : float
        The number of radians to rotate ``position`` by.
    """
    p_x, p_y = position
    c_x, c_y = center

    x_dist = p_x - c_x
    y_dist = p_y - c_y

    return Position(
        (x_dist * math.cos(radians) - y_dist * math.sin(radians)) + c_x,
        (x_dist * math.sin(radians) + y_dist * math.cos(radians)) + c_y,
    )
