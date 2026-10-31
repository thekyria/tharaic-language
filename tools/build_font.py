#!/usr/bin/env python3
"""Build Tharaic Stele, Wedge and Ledger, three typefaces for the Tharaic alphabet.

Every letter is drawn as a centreline skeleton of straight cuts, as a chisel
makes them: curves are broken into facets every 60 degrees. The skeleton is
stroked with one even width, widened into a straight wedge at its free ends,
clipped flat at the baseline and the top line, and merged into outlines.
Capitals are full height; lowercase letters are drawn as small capitals, as in
an inscription, so ordinary text works.

Tharaic Wedge draws the same skeletons as if pressed into clay: every straight
cut becomes a cuneiform wedge, a triangular head where the stylus went in and a
tail that thins away from it.

Tharaic Ledger writes them with a reed pen, as in the merchants' ledgers and
the cursive of Aramaic and Phoenician scribes: a broad nib held so that level
strokes are thick and upright ones thin, corners rounded off, a forward slant,
and long downstrokes below the line in a few letters.

Writes font/TharaicStele.*, font/TharaicWedge.* and font/TharaicLedger.* (.ttf
and .woff2), and their specimens in docs/.
Unlike the other tools this one needs three packages:

    pip install fonttools skia-pathops brotli
    python3 tools/build_font.py
"""
import math
from pathlib import Path

import pathops
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.timeTools import timestampFromString
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = Path(__file__).resolve().parent.parent
VERSION = "0.11"
BUILD_DATE = "Fri Oct 30 00:00:00 2026"

UPM = 1000
CAP, CAP_STROKE = 700, 84        # capitals
SMALL, SMALL_STROKE = 510, 76    # small capitals (lowercase letters) and digits
OVERSHOOT = 0                    # faceted letters sit flat on the lines, like straight ones
FACET = 60                       # degrees of curve per straight cut
PHASE = 90                       # a facet always lies flat along the top (and bottom)
MITER_LIMIT = 3.0

# Side bearings, in units at cap height: straight side, round side, open side, diagonal side
SIDES = {"S": 70, "R": 50, "O": 40, "D": 24}


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

class Shape:
    """One glyph's strokes at a given height and stroke width."""

    def __init__(self, height, stroke, width_unit):
        self.H, self.s = height, stroke
        self.T = height - stroke / 2    # centreline of a bar on the top line
        self.B = stroke / 2             # centreline of a bar on the baseline
        self.M = height / 2
        self.u = width_unit
        self.wedge = False              # drawn for Tharaic Wedge, which allows at most MAX_WEDGES cuts
        self.ledger = False             # drawn for Tharaic Ledger
        self.foot = 0                   # where long stems end: below the line in Ledger
        self.strokes = []               # Stroke objects
        self.fills = []                 # filled pathops.Path (dots)

    def W(self, ratio):
        return ratio * self.u

    def line(self, *points, closed=False, clip=True, flared=True):
        b = self.path(clip, flared).move(*points[0])
        for pt in points[1:]:
            b.to(*pt)
        b.done(closed)

    def path(self, clip=None, flared=True):
        """Start a path of lines and elliptical arcs; call .done() to add it."""
        return PathBuilder(self, clip, flared)

    def ellipse(self, cx, cy, rx, ry):
        self.path().move(cx + rx, cy).arc(cx, cy, rx, ry, 0, 360).done(closed=True)

    def dot(self, x, y, d=None):
        d = d or self.s * 1.2
        p = pathops.Path()
        pts = facets(x, y, d / 2, d / 2, 0, 360)
        p.moveTo(*pts[0])
        for pt in pts[1:]:
            p.lineTo(*pt)
        p.close()
        self.fills.append(p)

    def diamond(self, cx, cy, half_w, half_h):
        """A diamond of four cuts whose sharp (mitred) points reach half_w and half_h from
        its centre. Returns the half-width and half-height of its centreline."""
        b, a = half_w, half_h
        for _ in range(20):   # the mitred points reach past the centreline corners: solve for those
            side = math.hypot(a, b)
            a, b = half_h - self.s / 2 * side / b, half_w - self.s / 2 * side / a
        self.line((cx, cy + a), (cx + b, cy), (cx, cy - a), (cx - b, cy), closed=True, clip=None)
        return b, a

    def bowl(self, x0, top, bottom, right):
        """A pointed bowl from a stem at x0, as in archaic Β, Ρ, Ϸ: two cuts meeting at a point,
        with short flats along the top and bottom (none in Wedge, to save cuts)."""
        mid = (top + bottom) / 2
        if self.wedge:
            self.line((x0, top), (right, mid), (x0, bottom), clip=None)
            return
        flat = x0 + .35 * (right - x0)
        self.line((x0, top), (flat, top), (right, mid), (flat, bottom), (x0, bottom), clip=None)


# An "ellipse" here is a polygon whose sides touch the true ellipse at PHASE and
# every FACET degrees from it: with 60, a hexagon with a flat top and bottom and
# pointed sides, its corners at 0, 60, 120... degrees.

def on_ellipse(cx, cy, rx, ry, angle):
    """The point of the faceted ellipse in the direction of angle (degrees)."""
    def touch(a):
        return PHASE + round((a - PHASE) / FACET) * FACET
    k = 1 / math.cos(math.radians(angle - touch(angle)))
    narrow = math.cos(math.radians(touch(0)))   # pull pointed sides back to the width rx
    t = math.radians(angle)
    return cx + rx * narrow * k * math.cos(t), cy + ry * k * math.sin(t)


def facets(cx, cy, rx, ry, a0, a1):
    """The points of the faceted arc from angle a0 to a1 (degrees), corners included."""
    step = FACET if a1 > a0 else -FACET
    first = PHASE + FACET / 2       # corners lie halfway between the touching points
    k = (a0 - first) / FACET
    corner = first + (math.floor(k) + 1 if step > 0 else math.ceil(k) - 1) * FACET
    points = [on_ellipse(cx, cy, rx, ry, a0)]
    while (a1 - corner) * step > 1e-9:
        # a corner very near an end would leave a sliver of a cut: run straight past it
        if min(abs(corner - a0), abs(corner - a1)) >= 10 or abs(a1 - a0) >= 360:
            points.append(on_ellipse(cx, cy, rx, ry, corner))
        corner += step
    points.append(on_ellipse(cx, cy, rx, ry, a1))
    return points


class Stroke:
    """A skeleton path, with its centreline as points (for the flares) and its clip range."""

    def __init__(self, path, points, closed, clip, flared):
        self.path, self.points, self.closed, self.clip = path, points, closed, clip
        self.flared = flared and not closed


class PathBuilder:
    def __init__(self, shape, clip, flared):
        self.shape, self.clip, self.flared = shape, clip, flared
        self.p, self.points = pathops.Path(), []

    def move(self, x, y):
        self.p.moveTo(x, y)
        self.points.append((x, y))
        return self

    def to(self, x, y):
        self.p.lineTo(x, y)
        self.points.append((x, y))
        return self

    def arc(self, cx, cy, rx, ry, a0, a1):
        for pt in facets(cx, cy, rx, ry, a0, a1)[1:]:
            self.to(*pt)
        return self

    def done(self, closed=False):
        if closed:
            self.p.close()
        clip = (0, self.shape.H) if self.clip is True else self.clip
        self.shape.strokes.append(Stroke(self.p, self.points, closed, clip, self.flared))


# Flares: a free stroke end widens by FLARE_WIDTH (times the stroke, on each side)
# over the last FLARE_LENGTH strokes, in a straight wedge, as a chisel leaves it.
FLARE_WIDTH, FLARE_LENGTH = .30, 2.0


def flare(points, s, extend):
    """A polygon that widens a stroke towards its end at points[0]."""
    # never past the end of the first cut, so a flare cannot wrap round a corner
    length = min(FLARE_LENGTH * s, .9 * math.dist(points[0], points[1]))
    # Walk inwards from the end, sampling every length/16
    samples, walked, i = [points[0]], 0.0, 0
    step, target = length / 16, length / 16
    while i < len(points) - 1 and walked < length:
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        seg = math.hypot(x1 - x0, y1 - y0)
        while seg and walked + seg >= target and target <= length:
            f = (target - walked) / seg
            samples.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
            target += step
        walked += seg
        i += 1
    if len(samples) < 3:
        return None
    left, right = [], []
    for k, (x, y) in enumerate(samples):
        a = samples[max(k - 1, 0)]
        b = samples[min(k + 1, len(samples) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty)
        nx, ny = -ty / n, tx / n
        t = 1 - k / (len(samples) - 1)
        hw = s / 2 + FLARE_WIDTH * s * t
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    if extend:   # carry the full width past the end, to be cut flat by the clip
        (x0, y0), (x1, y1) = samples[0], samples[1]
        d = math.hypot(x0 - x1, y0 - y1)
        ox, oy = (x0 - x1) / d * s, (y0 - y1) / d * s
        left.insert(0, (left[0][0] + ox, left[0][1] + oy))
        right.insert(0, (right[0][0] + ox, right[0][1] + oy))
    p = pathops.Path()
    p.moveTo(*left[0])
    for pt in left[1:] + right[::-1]:
        p.lineTo(*pt)
    p.close()
    return p


def outline(shape):
    """Stroke, flare, clip and merge a shape's skeleton into one filled path."""
    bodies = []
    for st in shape.strokes:
        p = pathops.Path()
        p.addPath(st.path)
        p.stroke(shape.s, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, MITER_LIMIT)
        bodies.append(p)
    parts = []
    for i, st in enumerate(shape.strokes):
        p = bodies[i]
        if st.flared:
            others = [b for j, b in enumerate(bodies) if j != i] + shape.fills
            for pts in (st.points, st.points[::-1]):
                if any(o.contains(pts[0]) for o in others):
                    continue   # the end joins another stroke
                on_line = st.clip and any(abs(pts[0][1] - y) < 1 for y in st.clip)
                f = flare(pts, shape.s, on_line)
                if f is not None:
                    p = pathops.op(p, f, pathops.PathOp.UNION)
        if st.clip:
            p = pathops.op(p, clip_box(*st.clip), pathops.PathOp.INTERSECTION)
        parts.append(p)
    parts.extend(shape.fills)
    return union(parts)


def union(parts):
    result = pathops.Path()
    for p in parts:
        result = pathops.op(result, p, pathops.PathOp.UNION)
    return result


def clip_box(lo, hi):
    box = pathops.Path()
    box.moveTo(-5000, lo); box.lineTo(5000, lo); box.lineTo(5000, hi); box.lineTo(-5000, hi); box.close()
    return box


def polygon(points):
    p = pathops.Path()
    p.moveTo(*points[0])
    for pt in points[1:]:
        p.lineTo(*pt)
    p.close()
    return p


# Wedges, in strokes: the half-width and length of the head, the half-width of the tail
# where it leaves the head, and how much of that it keeps at its far end. A cut shorter
# than WEDGE_MIN gets no head of its own (the short facets of S and the digits).
WEDGE_HEAD_W, WEDGE_HEAD_L, WEDGE_TAIL_W, WEDGE_TAIL_END, WEDGE_MIN = .80, 1.3, .36, .45, 2.5


def wedge(p0, p1, s, heads):
    """One cut as a cuneiform wedge, its head at the upper end (the left, if nearly level)."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    if (abs(dy) > .3 * abs(dx) and y1 > y0) or (abs(dy) <= .3 * abs(dx) and x1 < x0):
        (x0, y0), (x1, y1), dx, dy = (x1, y1), (x0, y0), -dx, -dy
    n = math.hypot(dx, dy)
    if n < 1:
        return None
    ux, uy = dx / n, dy / n
    nx, ny = -uy, ux
    hw, hl, tw = WEDGE_HEAD_W * s, min(WEDGE_HEAD_L * s, .7 * n), WEDGE_TAIL_W * s
    # one head per meeting point: a second cut from the same point starts without one
    te = tw * WEDGE_TAIL_END
    if n < WEDGE_MIN * s:   # a short facet: an even cut, so a run of them joins up
        hw = te = tw
    elif any(math.hypot(x0 - hx, y0 - hy) < 1.2 * s for hx, hy in heads):
        hw = tw
    else:
        heads.append((x0, y0))
    hx, hy = x0 + ux * hl, y0 + uy * hl
    return polygon([(x0 + nx * hw, y0 + ny * hw), (hx + nx * tw, hy + ny * tw), (x1 + nx * te, y1 + ny * te),
                    (x1 - nx * te, y1 - ny * te), (hx - nx * tw, hy - ny * tw), (x0 - nx * hw, y0 - ny * hw)])


MAX_WEDGES = 4   # per glyph, in Tharaic Wedge


def outline_wedge(shape):
    """Press a shape's skeleton into clay: every straight cut a wedge, every dot a corner wedge."""
    parts, heads, count = [], [], len(shape.fills)
    for st in shape.strokes:
        pts = st.points + ([st.points[0]] if st.closed else [])
        wedges = [w for w in (wedge(a, b, shape.s, heads) for a, b in zip(pts, pts[1:])) if w is not None]
        count += len(wedges)
        p = union(wedges)
        if st.clip:
            p = pathops.op(p, clip_box(*st.clip), pathops.PathOp.INTERSECTION)
        parts.append(p)
    for f in shape.fills:   # a dot is a corner wedge (Winkelhaken): a head with no tail
        x0, y0, x1, y1 = f.bounds
        cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2
        parts.append(polygon([(cx - r, cy + r), (cx + r, cy), (cx - r, cy - r)]))
    shape.wedge_count = count
    return union(parts)


# Ledger: the nib's angle from level (degrees), length and thickness (in strokes),
# the forward slant (degrees); corners of at least LEDGER_ROUND_MIN degrees are
# rounded, starting LEDGER_ROUND_CUT of the way along the shorter side.
LEDGER_NIB_ANGLE, LEDGER_NIB_LEN, LEDGER_NIB_THICK, LEDGER_SLANT = 70, 1.45, .30, 10
LEDGER_ROUND_MIN, LEDGER_ROUND_CUT = 75, .45
LEDGER_DESCENDER = .22   # how far long stems reach below the line, in heights


def hull(points):
    """The convex hull of some points, anticlockwise."""
    pts = sorted(set(points))
    def half(seq):
        out = []
        for q in seq:
            while len(out) > 1 and ((out[-1][0] - out[-2][0]) * (q[1] - out[-2][1])
                                    - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(q)
        return out
    lower, upper = half(pts), half(pts[::-1])
    return lower[:-1] + upper[:-1]


def round_off(points, closed):
    """Round off the open corners of a skeleton, as a pen turns them; sharp corners
    (under LEDGER_ROUND_MIN degrees, as in Δ Α Ν) stay sharp."""
    n = len(points)
    if n < 3:
        return points
    out = []
    for i, v in enumerate(points):
        if not closed and i in (0, n - 1):
            out.append(v)
            continue
        a, b = points[i - 1], points[(i + 1) % n]
        la, lb = math.dist(a, v), math.dist(b, v)
        if la < 1 or lb < 1:
            out.append(v)
            continue
        cos = ((a[0] - v[0]) * (b[0] - v[0]) + (a[1] - v[1]) * (b[1] - v[1])) / (la * lb)
        if math.degrees(math.acos(max(-1, min(1, cos)))) < LEDGER_ROUND_MIN:
            out.append(v)
            continue
        c = LEDGER_ROUND_CUT * min(la, lb)
        p0 = (v[0] + (a[0] - v[0]) * c / la, v[1] + (a[1] - v[1]) * c / la)
        p2 = (v[0] + (b[0] - v[0]) * c / lb, v[1] + (b[1] - v[1]) * c / lb)
        for k in range(9):   # a quadratic curve from p0 to p2, pulled towards the corner
            t = k / 8
            out.append(((1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * v[0] + t * t * p2[0],
                        (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * v[1] + t * t * p2[1]))
    return out


def nib_stroke(p0, p1, s):
    """The shape a broad nib leaves drawn from p0 to p1."""
    t = math.radians(LEDGER_NIB_ANGLE)
    ux, uy = math.cos(t) * LEDGER_NIB_LEN * s / 2, math.sin(t) * LEDGER_NIB_LEN * s / 2
    vx, vy = -math.sin(t) * LEDGER_NIB_THICK * s / 2, math.cos(t) * LEDGER_NIB_THICK * s / 2
    corners = [(ux + vx, uy + vy), (ux - vx, uy - vy), (-ux + vx, -uy + vy), (-ux - vx, -uy - vy)]
    return polygon(hull([(x + cx, y + cy) for x, y in (p0, p1) for cx, cy in corners]))


def outline_ledger(shape):
    """Write a shape's skeleton with a reed pen: rounded corners, a broad nib, a forward slant."""
    parts = []
    for st in shape.strokes:
        pts = round_off(list(st.points), st.closed)
        seq = pts + [pts[0]] if st.closed else pts
        parts += [nib_stroke(a, b, shape.s) for a, b in zip(seq, seq[1:])]
    for f in shape.fills:   # a dot is a short dab of the nib
        x0, y0, x1, y1 = f.bounds
        cx, cy, d = (x0 + x1) / 2, (y0 + y1) / 2, .2 * shape.s
        parts.append(nib_stroke((cx - d, cy - d), (cx + d, cy + d), shape.s))
    return union(parts).transform(1, 0, math.tan(math.radians(LEDGER_SLANT)), 1, 0, 0)


# ---------------------------------------------------------------------------
# Letters. Coordinates are centrelines: a stem at x=0 runs from -s/2 to s/2.
# Each function returns the side bearings (left, right) as keys of SIDES.
# ---------------------------------------------------------------------------

def circle_O(g, w, cy=None, top=None, bottom=None):
    top = g.H if top is None else top
    bottom = 0 if bottom is None else bottom
    ry = (top - bottom - g.s) / 2 + OVERSHOOT
    g.ellipse(w / 2, (top + bottom) / 2 if cy is None else cy, w / 2, ry)


def alpha(g):
    # Archaic: the crossbar slopes down to the right
    w = g.W(.80)
    g.line((0, 0), (w / 2, g.H), (w, 0))
    y0, y1 = .38 * g.H, .22 * g.H
    x0, x1 = w / 2 * y0 / g.H, w - w / 2 * y1 / g.H
    g.line((x0, y0), (x1, y1))
    return "DD"


def beta(g):
    if g.wedge:   # stem, upper bowl and a foot, like Phoenician bet: four wedges
        g.line((0, 0), (0, g.H))
        g.bowl(0, g.T, .44 * g.H, g.W(.50))
        g.line((0, g.B), (g.W(.52), g.B))
        return "SO"
    g.line((0, 0), (0, g.H))
    m = .53 * g.H
    g.bowl(0, g.T, m, g.W(.50))
    g.bowl(0, m, g.B, g.W(.58))
    return "SR"


def gamma(g):
    g.line((0, 0), (0, g.H))
    g.line((0, g.T), (g.W(.56), g.T))
    return "SO"


def delta(g):
    w = g.W(.80)
    g.line((0, g.B), (w / 2, g.H + g.s), (w, g.B), closed=True)
    return "DD"


def epsilon(g):
    # Archaic: the arms slope down from the stem, as in Phoenician he
    drop = .10 * g.H
    g.line((0, 0), (0, g.H))
    g.line((0, g.T), (g.W(.54), g.T - drop))
    g.line((0, g.M + drop / 2), (g.W(.46), g.M - drop / 2))
    g.line((0, g.B + drop), (g.W(.54), g.B))
    return "SO"


def zeta(g):
    # Archaic: two bars joined by a stem, as in Phoenician zayin
    w = g.W(.60)
    g.line((0, g.T), (w, g.T))
    g.line((0, g.B), (w, g.B))
    g.line((w / 2, 0), (w / 2, g.H))
    return "OO"


def latin_Z(g):
    w = g.W(.62)
    g.line((0, g.T), (w, g.T), (0, g.B), (w, g.B))
    return "OO"


def eta(g):
    w = g.W(.66)
    g.line((0, 0), (0, g.H))
    g.line((w, 0), (w, g.H))
    g.line((0, g.M), (w, g.M))
    return "SS"


def theta(g):
    if g.wedge:   # a dot in a downward triangle, to stay within four wedges
        w = g.W(.80)
        g.line((0, g.T), (w, g.T), (w / 2, 0), closed=True)
        g.dot(w / 2, .62 * g.H)
        return "DD"
    # Archaic: a cross in a diamond, full height so the four counters stay open
    half_w = g.W(.96) / 2 + g.s / 2
    cx = half_w
    b, a = g.diamond(cx, g.M, half_w, g.H / 2)
    if g.ledger:   # the pen rounds the diamond's points, so keep the cross inside it
        b, a = .72 * b, .72 * a
    g.line((cx - b, g.M), (cx + b, g.M), clip=None)
    g.line((cx, g.M - a), (cx, g.M + a), clip=None)
    return "RR"


def iota(g):
    g.line((0, 0), (0, g.H))
    return "SS"


def kappa(g):
    w = g.W(.62)
    g.line((0, 0), (0, g.H))
    g.line((w, g.H), (0, .36 * g.H))
    x = .32 * w
    g.line((x, .36 * g.H + x / w * .64 * g.H), (w, 0))
    return "SD"


def lamda(g):
    w = g.W(.78)
    g.line((0, 0), (w / 2, g.H), (w, 0))
    return "DD"


def mu(g):
    w = g.W(.92)
    g.line((0, 0), (.1 * w, g.H), (.5 * w, .16 * g.H), (.9 * w, g.H), (w, 0))
    return "DD"


def nu(g):
    w = g.W(.66)
    g.line((0, 0), (0, g.H), (w, 0), (w, g.H))
    return "SS"


def xi(g):
    # Archaic: a stem through the three bars
    w = g.W(.60)
    g.line((0, g.T), (w, g.T))
    g.line((.14 * w, g.M), (.86 * w, g.M))
    g.line((0, g.B), (w, g.B))
    g.line((w / 2, 0), (w / 2, g.H))
    return "OO"


def small_diamond(g):
    """The diamond of Ο, Θ and Q: smaller than the other letters, centred on the middle.
    Returns its centre x and centreline half-width and half-height."""
    half_w = g.W(.76) / 2 + g.s / 2
    b, a = g.diamond(half_w, g.M, half_w, g.H / 2 - .07 * g.H)
    return half_w, b, a


def omicron(g):
    # Archaic: a diamond of four cuts
    small_diamond(g)
    return "RR"


def pi(g):
    # Archaic: the right leg is short
    w = g.W(.60)
    g.line((0, 0), (0, g.H))
    g.line((w, .45 * g.H), (w, g.H))
    g.line((0, g.T), (w, g.T))
    return "SO"


def rho(g):
    g.line((0, g.foot), (0, g.H))
    g.bowl(0, g.T, .42 * g.H, g.W(.54))
    return "SR"


def sigma(g):
    # Splayed arms, as in Attic inscriptions
    w = g.W(.62)
    g.line((w, g.H), (0, g.T - .05 * g.H), (.48 * w, g.M), (0, g.B + .05 * g.H), (w, 0))
    return "OD"


def tau(g):
    w = g.W(.64)
    g.line((0, g.T), (w, g.T))
    g.line((w / 2, 0), (w / 2, g.H))
    return "DD"


def upsilon(g):
    w, y = g.W(.70), .44 * g.H
    g.line((0, g.H), (w / 2, y), (w, g.H))
    g.line((w / 2, 0), (w / 2, y))
    return "DD"


def phi(g):
    if g.wedge:   # a stem through an upward triangle
        w = g.W(.76)
        g.line((w / 2, 0), (w / 2, g.H))
        g.line((0, .20 * g.H), (w, .20 * g.H), (w / 2, .82 * g.H), closed=True, clip=None)
        return "DD"
    # A diamond on a stem that runs through it
    w = g.W(.84)
    g.line((w / 2, g.foot), (w / 2, g.H))
    g.diamond(w / 2, g.M, w / 2, .30 * g.H)
    return "RR"


def chi(g):
    w = g.W(.68)
    g.line((0, 0), (w, g.H))
    g.line((0, g.H), (w, 0))
    return "DD"


def psi(g):
    # Archaic: a trident, its arms straight cuts
    w, y = g.W(.74), .40 * g.H
    g.line((w / 2, g.foot), (w / 2, g.H))
    g.line((0, g.H), (w / 2, y), (w, g.H))
    return "DD"


def omega(g):
    if g.wedge:   # a downward triangle over a bar on the baseline
        w = g.W(.80)
        g.line((0, g.B), (w, g.B))
        g.line((.1 * w, g.T), (.9 * w, g.T), (w / 2, 1.6 * g.s), closed=True)
        return "OO"
    # A diamond standing over a bar on the baseline
    w = g.W(.80)
    g.line((0, g.B), (w, g.B))
    bottom, top = 1.6 * g.s, g.H - .07 * g.H
    g.diamond(w / 2, (top + bottom) / 2, g.W(.70) / 2, (top - bottom) / 2)
    return "OO"


def digamma(g):
    g.line((0, 0), (0, g.H))
    g.line((0, g.T), (g.W(.54), g.T))
    g.line((0, .52 * g.H), (g.W(.46), .52 * g.H))
    return "SO"


def heta(g):
    g.line((0, 0), (0, g.H))
    g.line((0, g.M), (g.W(.46), g.M))
    return "SO"


def yot(g):
    # An upside-down Λ with a short left leg: two cuts
    w = g.W(.50)
    g.line((w, g.H), (.62 * w, 0), (0, .38 * g.H))
    return "DD"


def sho(g):
    g.line((0, g.foot), (0, g.H))
    g.bowl(0, .76 * g.H, .26 * g.H, g.W(.54))
    return "SR"


def koppa(g):
    if g.wedge:   # a downward triangle on a short stem
        w = g.W(.62)
        g.line((0, g.T), (w, g.T), (w / 2, .32 * g.H), closed=True)
        g.line((w / 2, 0), (w / 2, .32 * g.H))
        return "DD"
    # A diamond on a short stem
    w = g.W(.66)
    bottom, top = .32 * g.H, g.H - .02 * g.H
    cy = (top + bottom) / 2
    b, a = g.diamond(w / 2, cy, w / 2, (top - bottom) / 2)
    g.line((w / 2, g.foot), (w / 2, cy - a))
    return "RR"


# Latin letters whose shapes the Greek ones do not already give

def latin_C(g):
    # A wide ⟨: two cuts about 100 degrees apart
    w = g.W(.42)
    g.line((w, g.H), (0, g.M), (w, 0))
    return "DO"


def latin_D(g):
    g.line((0, 0), (0, g.H))
    g.bowl(0, g.T, g.B, g.W(.74))
    return "SR"


def latin_G(g):
    # The C, with an upright spur at the end of the bottom
    w = g.W(.46)
    g.line((w, g.H), (0, g.M), (w, 0), (w, .40 * g.H))
    return "DS"


def latin_L(g):
    g.line((0, g.H), (0, 0))
    g.line((0, g.B), (g.W(.52), g.B))
    return "SO"


def latin_Q(g):
    if g.wedge:   # Q comes from koppa, and in Wedge it is drawn the same
        return koppa(g)
    # The diamond of O, with a tail from its lower right side
    cx, b, a = small_diamond(g)
    start = (cx + b / 2, g.M - a / 2)   # on the diamond, so only the tail end flares
    g.line(start, (cx + 1.1 * b, -.16 * g.H), clip=None)
    return "RR"


def latin_R(g):
    w = g.W(.60)
    g.line((0, 0), (0, g.H))
    g.bowl(0, g.T, .44 * g.H, g.W(.54))
    g.line((.34 * w, .44 * g.H), (w, 0))
    return "SD"


def latin_S(g):
    if g.wedge:   # a zigzag of three cuts, as in archaic inscriptions
        w = g.W(.56)
        g.line((w, g.T), (0, .62 * g.H), (w, .38 * g.H), (0, g.B))
        return "OO"
    w, m = g.W(.56), .53 * g.H
    r1 = (g.T - m) / 2 + OVERSHOOT / 2
    r2 = (m - g.B) / 2 + OVERSHOOT / 2
    rx1, rx2 = .46 * w, .5 * w
    (g.path().move(*on_ellipse(w / 2, m + r1, rx1, r1, 25))
     .arc(w / 2, m + r1, rx1, r1, 25, 270)
     .arc(w / 2, m - r2, rx2, r2, 90, -155).done())
    return "OO"


def latin_V(g):
    w = g.W(.78)
    g.line((0, g.H), (w / 2, 0), (w, g.H))
    return "DD"


def latin_W(g):
    w = g.W(1.16)
    g.line((0, g.H), (.24 * w, 0), (.5 * w, g.H), (.76 * w, 0), (w, g.H))
    return "DD"


LETTERS = [
    # (capital name, capital code, small name, small codes, function)
    ("Alpha", 0x391, "alpha", [0x3B1], alpha),
    ("Beta", 0x392, "beta", [0x3B2], beta),
    ("Gamma", 0x393, "gamma", [0x3B3], gamma),
    ("Delta", 0x394, "delta", [0x3B4], delta),
    ("Epsilon", 0x395, "epsilon", [0x3B5], epsilon),
    ("Zeta", 0x396, "zeta", [0x3B6], zeta),
    ("Eta", 0x397, "eta", [0x3B7], eta),
    ("Theta", 0x398, "theta", [0x3B8], theta),
    ("Iota", 0x399, "iota", [0x3B9], iota),
    ("Kappa", 0x39A, "kappa", [0x3BA], kappa),
    ("Lambda", 0x39B, "lambda", [0x3BB], lamda),
    ("Mu", 0x39C, "mu", [0x3BC], mu),
    ("Nu", 0x39D, "nu", [0x3BD], nu),
    ("Xi", 0x39E, "xi", [0x3BE], xi),
    ("Omicron", 0x39F, "omicron", [0x3BF], omicron),
    ("Pi", 0x3A0, "pi", [0x3C0], pi),
    ("Rho", 0x3A1, "rho", [0x3C1], rho),
    ("Sigma", 0x3A3, "sigma", [0x3C3, 0x3C2], sigma),   # final ς has the same form
    ("Tau", 0x3A4, "tau", [0x3C4], tau),
    ("Upsilon", 0x3A5, "upsilon", [0x3C5], upsilon),
    ("Phi", 0x3A6, "phi", [0x3C6], phi),
    ("Chi", 0x3A7, "chi", [0x3C7], chi),
    ("Psi", 0x3A8, "psi", [0x3C8], psi),
    ("Omega", 0x3A9, "omega", [0x3C9], omega),
    ("Digamma", 0x3DC, "digamma", [0x3DD], digamma),
    ("Heta", 0x370, "heta", [0x371], heta),
    ("Yot", 0x37F, "yot", [0x3F3], yot),
    ("Sho", 0x3F7, "sho", [0x3F8], sho),
    ("Koppa", 0x3D8, "koppa", [0x3D9], koppa),
    ("C", 0x43, "c", [0x63], latin_C),
    ("D", 0x44, "d", [0x64], latin_D),
    ("G", 0x47, "g", [0x67], latin_G),
    ("L", 0x4C, "l", [0x6C], latin_L),
    ("Q", 0x51, "q", [0x71], latin_Q),
    ("R", 0x52, "r", [0x72], latin_R),
    ("S", 0x53, "s", [0x73], latin_S),
    ("V", 0x56, "v", [0x76], latin_V),
    ("W", 0x57, "w", [0x77], latin_W),
    ("Z", 0x5A, "z", [0x7A], latin_Z),
]

# Latin letters drawn the same as a Greek one share its glyph
SAME_AS_GREEK = {
    "A": "Alpha", "B": "Beta", "E": "Epsilon", "F": "Digamma", "H": "Eta", "I": "Iota",
    "J": "Yot", "K": "Kappa", "M": "Mu", "N": "Nu", "O": "Omicron", "P": "Rho",
    "T": "Tau", "X": "Chi", "Y": "Upsilon",
}

# Letters written with another Latin letter, as in Roman inscriptions: U is V
LATIN_SAME = {
    "U": "V",
}

# Precomposed long vowels, Greek and romanized: (name, codes, base glyph)
MACRONS = [
    ("Alphamacron", [0x1FB9, 0x100], "Alpha"), ("alphamacron", [0x1FB1, 0x101], "alpha"),
    ("Upsilonmacron", [0x1FE9], "Upsilon"), ("upsilonmacron", [0x1FE1], "upsilon"),
    ("Epsilonmacron", [0x112], "Epsilon"), ("epsilonmacron", [0x113], "epsilon"),
    ("Iotamacron", [0x12A], "Iota"), ("iotamacron", [0x12B], "iota"),
    ("Omicronmacron", [0x14C], "Omicron"), ("omicronmacron", [0x14D], "omicron"),
    ("Vmacron", [0x16A], "V"), ("vmacron", [0x16B], "v"),   # ū: U is written V
]
MACRON_GAP = 56


# ---------------------------------------------------------------------------
# Digits (at small-capital height, to sit with running text) and punctuation
# ---------------------------------------------------------------------------

def d0(g):
    if g.wedge:   # a box, to tell it from the diamond O
        w = g.W(.46)
        g.line((0, g.B), (0, g.T), (w, g.T), (w, g.B), closed=True)
        return "SS"
    circle_O(g, g.W(.62))
    return "RR"


def d1(g):
    g.line((-g.W(.20), .78 * g.H), (0, g.H), (0, 0))
    return "SS"


def d2(g):
    if g.wedge:
        w = g.W(.58)
        g.line((0, .78 * g.H), (.45 * w, g.T), (w, .72 * g.H), (0, g.B), (w, g.B))
        return "OO"
    w = g.W(.60)
    ry = .28 * g.H
    cy = g.T - ry + OVERSHOOT
    (g.path(clip=True).move(*on_ellipse(w / 2, cy, w / 2, ry, 160))
     .arc(w / 2, cy, w / 2, ry, 160, -35).to(0, g.B).to(w, g.B).done())
    return "OO"


def d3(g):
    if g.wedge:
        w = g.W(.56)
        g.line((0, g.T), (w, g.T), (.3 * w, .55 * g.H), (w, .28 * g.H), (0, g.B))
        return "OR"
    w, m = g.W(.58), .55 * g.H
    r1 = (g.T - m) / 2 + OVERSHOOT / 2
    r2 = (m - g.B) / 2 + OVERSHOOT / 2
    rx1, rx2 = .44 * w, .5 * w
    (g.path(clip=None).move(*on_ellipse(w - rx1, m + r1, rx1, r1, 155))
     .arc(w - rx1, m + r1, rx1, r1, 155, -90).to(w / 2, m)
     .arc(w / 2, m - r2, rx2, r2, 90, -155).done())
    return "OR"


def d4(g):
    w = g.W(.64)
    g.line((.72 * w, 0), (.72 * w, g.H), (0, .30 * g.H), (w, .30 * g.H))
    return "DO"


def d5(g):
    if g.wedge:
        w = g.W(.56)
        g.line((w, g.T), (0, g.T), (0, .56 * g.H), (w, .36 * g.H), (0, g.B))
        return "OR"
    w = g.W(.58)
    ry = .32 * g.H
    cy = g.B + ry - OVERSHOOT
    start = on_ellipse(w / 2, cy, w / 2, ry, 135)
    g.line((w * .94, g.T), (w * .08, g.T), (start[0], .56 * g.H), clip=True)
    (g.path(clip=None).move(start[0], .56 * g.H).to(*start)
     .arc(w / 2, cy, w / 2, ry, 135, -150).done())
    return "OR"


def d6(g):
    if g.wedge:   # a stroke down into a triangle
        w = g.W(.58)
        g.line((.85 * w, g.T), (0, .32 * g.H), (.5 * w, g.B), (w, .32 * g.H), (0, .32 * g.H))
        return "RR"
    w = g.W(.60)
    ry = .32 * g.H
    cy = g.B + ry - OVERSHOOT
    g.ellipse(w / 2, cy, w / 2, ry)
    g.line((.80 * w, g.H), on_ellipse(w / 2, cy, w / 2, ry, 150))
    return "RR"


def d7(g):
    w = g.W(.58)
    g.line((0, g.T), (w, g.T), (.28 * w, 0))
    return "OD"


def d8(g):
    if g.wedge:   # an hourglass of four cuts
        w = g.W(.56)
        g.line((0, g.T), (w, g.T), (0, g.B), (w, g.B), closed=True)
        return "OO"
    w, m = g.W(.60), .56 * g.H
    r1 = (g.T - m) / 2 + OVERSHOOT / 2
    r2 = (m - g.B) / 2 + OVERSHOOT / 2
    g.ellipse(w / 2, m + r1, .42 * w, r1)
    g.ellipse(w / 2, m - r2, .5 * w, r2)
    return "RR"


def d9(g):
    if g.wedge:   # the 6 turned round
        w = g.W(.58)
        g.line((.15 * w, g.B), (w, .68 * g.H), (.5 * w, g.T), (0, .68 * g.H), (w, .68 * g.H))
        return "RR"
    w = g.W(.60)
    ry = .32 * g.H
    cy = g.T - ry + OVERSHOOT
    g.ellipse(w / 2, cy, w / 2, ry)
    g.line((.20 * w, 0), on_ellipse(w / 2, cy, w / 2, ry, -30))
    return "RR"


DIGITS = [(f"{n}", 0x30 + i, f) for i, (n, f) in enumerate(
    zip(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"],
        [d0, d1, d2, d3, d4, d5, d6, d7, d8, d9]))]

DOT_Y = .64 * SMALL      # raised dot, at the top of the small capitals


def period(g):
    g.dot(0, g.s * .6)
    return "RR"


def comma(g):
    g.dot(0, g.s * .6)
    g.line((g.s * .3, g.s * .6), (-g.s * .35, -g.s * 1.6), clip=None)
    return "RR"


def colon(g):
    g.dot(0, g.s * .6)
    g.dot(0, DOT_Y)
    return "RR"


def semicolon(g):
    comma(g)
    g.dot(0, DOT_Y)
    return "RR"


def middot(g):
    g.dot(0, DOT_Y)
    return "RR"


def tricolon(g):
    for y in (g.s * .6, DOT_Y / 2 + g.s * .3, DOT_Y):
        g.dot(0, y)
    return "RR"


def ellipsis(g):
    for x in (0, 2.2 * g.s, 4.4 * g.s):
        g.dot(x, g.s * .6)
    return "RR"


def exclam(g):
    g.line((0, .28 * g.H), (0, g.H))
    g.dot(0, g.s * .6)
    return "SS"


def question(g):
    if g.wedge:
        w = g.W(.50)
        g.line((0, .80 * g.H), (.5 * w, g.T), (w, .80 * g.H), (.5 * w, .30 * g.H))
        g.dot(.5 * w, g.s * .6)
        return "OO"
    w, ry = g.W(.50), .22 * g.H
    cy = g.T - ry
    (g.path(clip=(0, g.H + OVERSHOOT)).move(*on_ellipse(w / 2, cy, w / 2, ry, 160))
     .arc(w / 2, cy, w / 2, ry, 160, -90).to(w / 2, .28 * g.H).done())
    g.dot(w / 2, g.s * .6)
    return "OO"


def paren_left(g):
    g.path(clip=None).move(g.W(.30), 820).arc(g.W(.30), 300, g.W(.30), 520, 90, 270).done()
    return "RO"


def paren_right(g):
    g.path(clip=None).move(0, 820).arc(0, 300, g.W(.30), 520, 90, -90).done()
    return "OR"


def bracket_left(g):
    g.line((g.W(.22), 820), (0, 820), (0, -220), (g.W(.22), -220), clip=(-220 - g.s, 820 + g.s))
    return "SO"


def bracket_right(g):
    g.line((0, 820), (g.W(.22), 820), (g.W(.22), -220), (0, -220), clip=(-220 - g.s, 820 + g.s))
    return "OS"


def hyphen(g):
    g.line((0, .48 * SMALL), (g.W(.34), .48 * SMALL), clip=None)
    return "OO"


def endash(g):
    g.line((0, .48 * SMALL), (500 - 2 * SIDES["O"], .48 * SMALL), clip=None)
    return "OO"


def emdash(g):
    g.line((0, .48 * SMALL), (1000 - 2 * SIDES["O"], .48 * SMALL), clip=None)
    return "OO"


def chevrons(left, double):
    def draw(g):
        w, h, y = g.W(.24), .36 * SMALL, .48 * SMALL
        for dx in ((0, w * 1.15) if double else (0,)):
            if left:
                g.line((dx + w, y + h / 2), (dx, y), (dx + w, y - h / 2), clip=None)
            else:
                g.line((dx, y + h / 2), (dx + w, y), (dx, y - h / 2), clip=None)
        return "DD"
    return draw


def quotes(shape):
    """Straight ticks ('), or slanted marks opening (6) and closing (9)."""
    def draw(g):
        top, n, h = g.H, 2 if shape.endswith("2") else 1, .26 * g.H
        for i in range(n):
            x = i * g.s * 2.2
            if shape.startswith("straight"):
                g.line((x, top), (x, top - h))
            elif shape.startswith("open"):
                g.line((x + g.s * .7, top), (x, top - h), clip=None)
            else:
                g.line((x, top), (x - g.s * .7, top - h), clip=None)
        return "OO"
    return draw


PUNCTUATION = [
    # (name, codes, function)
    ("period", [0x2E], period),
    ("comma", [0x2C], comma),
    ("colon", [0x3A], colon),
    ("semicolon", [0x3B, 0x37E], semicolon),             # also the Greek question mark
    ("periodcentered", [0xB7, 0x387], middot),           # also the Greek ano teleia
    ("tricolon", [0x205D], tricolon),                    # inscriptional word divider
    ("ellipsis", [0x2026], ellipsis),
    ("exclam", [0x21], exclam),
    ("question", [0x3F], question),
    ("parenleft", [0x28], paren_left),
    ("parenright", [0x29], paren_right),
    ("bracketleft", [0x5B], bracket_left),
    ("bracketright", [0x5D], bracket_right),
    ("hyphen", [0x2D, 0x2010], hyphen),
    ("endash", [0x2013], endash),
    ("emdash", [0x2014], emdash),
    ("guillemetleft", [0xAB], chevrons(True, True)),
    ("guillemetright", [0xBB], chevrons(False, True)),
    ("quotesingle", [0x27], quotes("straight1")),
    ("quotedbl", [0x22], quotes("straight2")),
    ("quoteleft", [0x2018], quotes("open1")),
    ("quoteright", [0x2019], quotes("close1")),
    ("quotedblleft", [0x201C], quotes("open2")),
    ("quotedblright", [0x201D], quotes("close2")),
]

# Kerning between capitals, in units at cap height; scaled for small capitals.
# Each side is a group of letter names (capital names; small capitals follow).
KERN_GROUPS = {
    "DIAG_L": ["Alpha", "Lambda", "Delta"],          # left side slopes away at the top
    "DIAG_R": ["Alpha", "Lambda", "Delta"],
    "OPEN_TOP": ["Tau", "Upsilon", "Gamma", "Digamma", "V", "W"],
    "OPEN_BELOW_R": ["Gamma", "Digamma", "Rho", "Sho", "Heta", "Tau"],
    "ROUND": ["Omicron", "Theta", "Koppa", "Phi", "C", "G", "Q"],
    "X": ["Chi", "Kappa"],
}
KERN_PAIRS = [
    ("OPEN_TOP", "DIAG_L", -70),
    ("DIAG_R", "OPEN_TOP", -70),
    ("OPEN_BELOW_R", "DIAG_L", -40),
    ("DIAG_R", "ROUND", -20),
    ("ROUND", "DIAG_L", -20),
    ("Tau", "ROUND", -20),
    ("ROUND", "Tau", -20),
    ("X", "ROUND", -25),
    ("ROUND", "X", -25),
    ("Lambda", "Lambda", -10),
    ("L", "OPEN_TOP", -70),
]


# ---------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------

class Glyph:
    def __init__(self, path, lsb, rsb, scale):
        xmin = path.bounds[0] if len(path) else 0
        xmax = path.bounds[2] if len(path) else 0
        left, right = SIDES[lsb] * scale, SIDES[rsb] * scale
        self.dx = left - xmin
        self.advance = round(xmax - xmin + left + right)
        self.path = path


def make(fn, height, stroke, width_unit, outliner):
    g = Shape(height, stroke, width_unit)
    g.wedge = outliner is outline_wedge
    g.ledger = outliner is outline_ledger
    g.foot = -LEDGER_DESCENDER * height if g.ledger else 0
    sides = fn(g)
    scale = (height / CAP) ** .6
    path = outliner(g)
    if g.wedge and g.wedge_count > MAX_WEDGES:
        raise ValueError(f"{fn.__name__} uses {g.wedge_count} wedges; Tharaic Wedge allows {MAX_WEDGES}")
    return Glyph(path, sides[0], sides[1], scale)


def draw(glyph, pen):
    glyph.path.draw(TransformPen(pen, (1, 0, 0, 1, glyph.dx, 0)))


def add_macron(glyph, height, stroke, outliner):
    """Return a copy of a glyph with a macron bar centred above it."""
    g = Shape(height, stroke * .8, 1)
    y = height + MACRON_GAP + g.s / 2
    half = min(glyph.advance * .3, height * .3)
    c = glyph.advance / 2 - glyph.dx
    g.line((c - half, y), (c + half, y), clip=None)
    bar = outliner(g)
    merged = pathops.op(glyph.path, bar, pathops.PathOp.UNION)
    new = Glyph.__new__(Glyph)
    new.path, new.dx, new.advance = merged, glyph.dx, glyph.advance
    return new


def build_glyphs(outliner):
    glyphs, cmap = {}, {}
    for cap_name, cap_code, small_name, small_codes, fn in LETTERS:
        glyphs[cap_name] = make(fn, CAP, CAP_STROKE, CAP, outliner)
        cmap[cap_code] = cap_name
        glyphs[small_name] = make(fn, SMALL, SMALL_STROKE, SMALL * 1.06, outliner)
        for code in small_codes:
            cmap[code] = small_name
    for latin, other in {**SAME_AS_GREEK, **LATIN_SAME}.items():
        cmap[ord(latin)] = other
        cmap[ord(latin.lower())] = other.lower()
    for name, codes, base in MACRONS:
        small = base[0].islower()
        glyphs[name] = add_macron(glyphs[base], SMALL if small else CAP, SMALL_STROKE if small else CAP_STROKE,
                                  outliner)
        for code in codes:
            cmap[code] = name
    for name, code, fn in DIGITS:
        glyphs[name] = make(fn, SMALL, SMALL_STROKE, SMALL * 1.06, outliner)
        cmap[code] = name
    for name, codes, fn in PUNCTUATION:
        glyphs[name] = make(fn, CAP, SMALL_STROKE, CAP, outliner)
        for code in codes:
            cmap[code] = name
    # The combining macron, for text written with a separate U+0304
    g = Shape(SMALL, SMALL_STROKE * .8, 1)
    y = SMALL + MACRON_GAP + g.s / 2
    g.line((-.15 * SMALL, y), (.15 * SMALL, y), clip=None)
    mark = Glyph.__new__(Glyph)
    mark.path, mark.dx, mark.advance = outliner(g), 0, 0
    glyphs["macroncomb"] = mark
    cmap[0x304] = "macroncomb"
    return glyphs, cmap


def kerning():
    """Pair adjustments as {(left glyph, right glyph): value}."""
    def members(key):
        return KERN_GROUPS.get(key, [key])
    pairs = {}
    small = (SMALL / CAP)
    for left, right, value in KERN_PAIRS:
        for a in members(left):
            for b in members(right):
                pairs[(a, b)] = value
                pairs[(a.lower(), b.lower())] = round(value * small)
                pairs[(a, b.lower())] = round(value * (1 + small) / 2)
    return pairs


def features(glyphs):
    lines = ["languagesystem DFLT dflt;", "languagesystem grek dflt;", "", "feature kern {"]
    for (a, b), v in sorted(kerning().items()):
        lines.append(f"  pos {a} {b} {v};")
    lines += ["} kern;", "", "markClass macroncomb <anchor 0 0> @TOP;", "feature mark {"]
    for name, glyph in glyphs.items():
        if name == "macroncomb":
            continue
        height = SMALL if not name[0].isupper() else CAP
        lines.append(f"  pos base {name} <anchor {glyph.advance // 2} {height - SMALL}> mark @TOP;")
    lines.append("} mark;")
    return "\n".join(lines)


def notdef():
    g = Shape(CAP, 40, 1)
    g.line((0, g.B), (420, g.B), (420, g.T), (0, g.T), closed=True, clip=None)
    return Glyph(outline(g), "S", "S", 1)


# The two faces: (family, file name, specimen file, outliner, description, page colour, ink colour)
FACES = [
    ("Tharaic Stele", "TharaicStele", "font-specimen.svg", outline,
     "An inscriptional typeface for the Tharaic alphabet, as if cut in stone. Lowercase letters are small capitals.",
     "#f4efe6", "#2b2622"),
    ("Tharaic Wedge", "TharaicWedge", "font-specimen-wedge.svg", outline_wedge,
     "A typeface for the Tharaic alphabet in cuneiform wedges, as if pressed into clay. Lowercase letters are small capitals.",
     "#e8d6bd", "#3a2a1c"),
    ("Tharaic Ledger", "TharaicLedger", "font-specimen-ledger.svg", outline_ledger,
     "A cursive typeface for the Tharaic alphabet, as if written with a reed pen in a merchant's ledger. "
     "Lowercase letters are small capitals.",
     "#efe3c6", "#2e2216"),
]


def build(face):
    family, file_name, _, outliner, description, _, _ = face
    glyphs, cmap = build_glyphs(outliner)
    glyphs = {".notdef": notdef(), "space": None, **glyphs}
    cmap[0x20] = cmap[0xA0] = "space"
    order = list(glyphs)

    tt, metrics = {}, {}
    for name, glyph in glyphs.items():
        pen = TTGlyphPen(None)
        if glyph is None:
            metrics[name] = (round(CAP * .30), 0)
        else:
            draw(glyph, Cu2QuPen(pen, max_err=1, reverse_direction=True))
            metrics[name] = (glyph.advance, 0)
        tt[name] = pen.glyph()

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(tt)
    for name in order:   # left side bearings from the real outlines
        metrics[name] = (metrics[name][0], getattr(fb.font["glyf"][name], "xMin", 0))
    fb.setupHorizontalMetrics(metrics)
    lowest = min(getattr(fb.font["glyf"][n], "yMin", 0) for n in order)
    ascent, descent = 900, min(-260, math.floor(lowest / 10) * 10)   # room for Ledger's descenders
    fb.setupHorizontalHeader(ascent=ascent, descent=descent)
    fb.setupNameTable({
        "familyName": family,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{file_name}-Regular-{VERSION}",
        "fullName": f"{family} Regular",
        "psName": f"{file_name}-Regular",
        "version": f"Version {VERSION}",
        "description": description,
    })
    fb.setupOS2(sTypoAscender=ascent, sTypoDescender=descent, sTypoLineGap=0,
                usWinAscent=ascent, usWinDescent=-descent, sxHeight=SMALL, sCapHeight=CAP,
                achVendID="NONE", fsSelection=0x40 | 0x80, version=4)
    fb.setupPost()
    stamp = timestampFromString(BUILD_DATE)   # fixed, so rebuilding gives the same files
    fb.setupHead(unitsPerEm=UPM, fontRevision=float(VERSION), created=stamp, modified=stamp)
    addOpenTypeFeaturesFromString(fb.font, features({k: v for k, v in glyphs.items() if v is not None}))

    out = ROOT / "font"
    out.mkdir(exist_ok=True)
    fb.font.save(out / f"{file_name}.ttf")
    fb.font.flavor = "woff2"
    fb.font.save(out / f"{file_name}.woff2")
    fb.font.flavor = None
    return fb.font


# ---------------------------------------------------------------------------
# Specimen
# ---------------------------------------------------------------------------

SPECIMEN = [
    # (text, size, caption)
    ("ΘᾹΡΟΣ", 120, None),
    ("ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ ϜͰͿϷϘ ᾹῩ", 52, "Capitals"),
    ("αβγδεζηθικλμνξοπρστυφχψω ϝͱϳϸϙ ᾱῡ", 52, "Lowercase, drawn as small capitals"),
    ("ABCDEFGHIJKLMNOPQRSTUVWXYZ ĀĒĪŌŪ", 52, "Latin, for the romanization"),
    ("abcdefghijklmnopqrstuvwxyz āēīōū", 52, None),
    ("0123456789 . , : ; · ⁝ ! ? « » ( ) –", 52, "Digits and punctuation"),
    ("Δωει θᾱρος και λαμβανει θᾱρος.", 60, "“The sea gives and the sea takes.”"),
    ("Dōei thāros kai lambanei thāros.", 60, None),
    ("Ζε αβανον εβενε Χᾱριϸος βενιλ Αδενος", 44, "From the votive inscription in The Sacred Register"),
    ("Βαλιλ ϳαμοι, ͱοτι εϸεμεϙε κολονυ.", 44, None),
    ("Λυ βερεχει-υ!", 44, None),
]


def specimen(font, face):
    _, _, specimen_file, _, _, page, ink = face
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"]
    kern = kerning()
    margin, width, y = 60, 1600, 40
    body = []
    for text, size, caption in SPECIMEN:
        if caption:
            y += 34
            body.append(f'<text x="{margin}" y="{y}" class="cap">{caption}</text>')
            y += 12
        scale = size / UPM
        y += size * .9
        x = 0
        prev = None
        paths = []
        for ch in text:
            name = cmap.get(ord(ch))
            if name is None:
                continue
            if prev:
                x += kern.get((prev, name), 0)
            pen = SVGPathPen(glyph_set)
            glyph_set[name].draw(pen)
            d = pen.getCommands()
            if d:
                paths.append(f'<path transform="translate({x:.0f} 0)" d="{d}"/>')
            x += hmtx[name][0]
            prev = name
        body.append(f'<g transform="translate({margin} {y:.0f}) scale({scale:.4f} {-scale:.4f})">{"".join(paths)}</g>')
        y += size * .45
    y += 30
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {y:.0f}" width="{width // 2}">\n'
           f'<style>.cap{{font: 22px sans-serif; fill: #6b6155}}</style>\n'
           f'<rect width="100%" height="100%" fill="{page}"/>\n<g fill="{ink}">\n'
           + "\n".join(body) + "\n</g>\n</svg>\n")
    (ROOT / "docs" / specimen_file).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    for face in FACES:
        font = build(face)
        specimen(font, face)
        print(f"Built font/{face[1]}.ttf and .woff2 ({len(font.getGlyphOrder())} glyphs) and docs/{face[2]}")
