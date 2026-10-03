"""``maximal_convex_polygons`` -- research code for the study of maximal convex
position subsets of planar point sets."""

from __future__ import annotations

__version__ = "0.1.0"

from .exactgeom import (  # noqa: F401
    Configuration,
    as_configuration,
    as_point,
    chirotope,
    distinct,
    in_general_position,
    is_left,
    orient,
)
from .convexposition import (  # noqa: F401
    convex_hull_vertices,
    convex_position_subsets,
    count_maximal_convex,
    in_convex_position,
    maximal_convex_subsets,
)