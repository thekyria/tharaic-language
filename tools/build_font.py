#!/usr/bin/env python3
"""Build Tharaic Stele, an inscriptional typeface for the Tharaic alphabet.

Every letter is drawn as a centreline skeleton of straight cuts, as a chisel
makes them: curves are broken into facets every 45 degrees. The skeleton is
stroked with one even width, widened into a straight wedge at its free ends,
clipped flat at the baseline and the top line, and merged into outlines.
Capitals are full height; lowercase letters are drawn as small capitals, as in
an inscription, so ordinary text works.

Writes font/TharaicStele.ttf, font/TharaicStele.woff2 and docs/font-specimen.svg.
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
FAMILY = "Tharaic Stele"
VERSION = "0.4"
BUILD_DATE = "Fri Oct 30 00:00:00 2026"

UPM = 1000
CAP, CAP_STROKE = 700, 84        # capitals
SMALL, SMALL_STROKE = 510, 76    # small capitals (lowercase letters) and digits
OVERSHOOT = 0                    # faceted letters sit flat on the lines, like straight ones
FACET = 45                       # degrees of curve per straight cut
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

    def bowl(self, x0, top, bottom, right):
        """A pointed bowl from a stem at x0, as in archaic Β, Ρ, Ϸ: two cuts meeting at a point."""
        flat = x0 + .35 * (right - x0)
        mid = (top + bottom) / 2
        self.line((x0, top), (flat, top), (right, mid), (flat, bottom), (x0, bottom), clip=None)


# An "ellipse" here is a polygon whose sides touch the true ellipse at every
# multiple of FACET degrees, so it has flat sides at the top, bottom, left and
# right, and its corners at the angles between.

def on_ellipse(cx, cy, rx, ry, angle):
    """The point of the faceted ellipse in the direction of angle (degrees)."""
    nearest = round(angle / FACET) * FACET
    k = 1 / math.cos(math.radians(angle - nearest))
    t = math.radians(angle)
    return cx + rx * k * math.cos(t), cy + ry * k * math.sin(t)


def facets(cx, cy, rx, ry, a0, a1):
    """The points of the faceted arc from angle a0 to a1 (degrees), corners included."""
    step = FACET if a1 > a0 else -FACET
    corner = (math.floor((a0 - FACET / 2) / FACET) + (1 if step > 0 else 0)) * FACET + FACET / 2
    if (corner - a0) * step <= 1e-9:
        corner += step
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
    length = FLARE_LENGTH * s
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
            box = pathops.Path()
            lo, hi = st.clip
            box.moveTo(-5000, lo); box.lineTo(5000, lo); box.lineTo(5000, hi); box.lineTo(-5000, hi); box.close()
            p = pathops.op(p, box, pathops.PathOp.INTERSECTION)
        parts.append(p)
    parts.extend(shape.fills)
    result = pathops.Path()
    for p in parts:
        result = pathops.op(result, p, pathops.PathOp.UNION)
    return result


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
    # Archaic: a cross in the ring
    w = g.W(.88)
    circle_O(g, w)
    g.line((0, g.M), (w, g.M), clip=None)
    g.line((w / 2, 0), (w / 2, g.H))
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


def omicron(g):
    # Archaic: smaller than the other letters, centred on the middle
    inset = .07 * g.H
    circle_O(g, g.W(.76), top=g.H - inset, bottom=inset)
    return "RR"


def pi(g):
    # Archaic: the right leg is short
    w = g.W(.60)
    g.line((0, 0), (0, g.H))
    g.line((w, .45 * g.H), (w, g.H))
    g.line((0, g.T), (w, g.T))
    return "SO"


def rho(g):
    g.line((0, 0), (0, g.H))
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
    w = g.W(.84)
    g.line((w / 2, 0), (w / 2, g.H))
    g.ellipse(w / 2, g.M, w / 2, .27 * g.H)
    return "RR"


def chi(g):
    w = g.W(.68)
    g.line((0, 0), (w, g.H))
    g.line((0, g.H), (w, 0))
    return "DD"


def psi(g):
    # Archaic: a trident, its arms straight cuts
    w, y = g.W(.74), .40 * g.H
    g.line((w / 2, 0), (w / 2, g.H))
    g.line((0, g.H), (w / 2, y), (w, g.H))
    return "DD"


def omega(g):
    w = g.W(.88)
    ry = (g.T - g.B) / (1 + math.sin(math.radians(60)))
    cy, rx, cx = g.T - ry + OVERSHOOT / 2, .43 * w, w / 2
    (g.path(clip=(0, g.H + OVERSHOOT)).move(0, g.B).to(cx - rx / 2, g.B)
     .arc(cx, cy, rx, ry, 240, -60).to(w, g.B).done())
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
    w, cy = g.W(.48), .34 * g.H
    (g.path(clip=(-OVERSHOOT, g.H)).move(w, g.H).to(w, cy)
     .arc(w / 2, cy, w / 2, cy - g.B + OVERSHOOT, 0, -165).done())
    return "OS"


def sho(g):
    g.line((0, 0), (0, g.H))
    g.bowl(0, .76 * g.H, .26 * g.H, g.W(.54))
    return "SR"


def koppa(g):
    w = g.W(.70)
    bottom = .30 * g.H
    ry = (g.H - bottom - g.s) / 2 + OVERSHOOT
    cy = (g.H + bottom) / 2
    g.ellipse(w / 2, cy, w / 2, ry)
    g.line((w / 2, 0), (w / 2, cy - ry))
    return "RR"


# Latin letters whose shapes the Greek ones do not already give

def latin_C(g):
    w = g.W(.80)
    g.path().move(*on_ellipse(w / 2, g.M, w / 2, g.M - g.B + OVERSHOOT, 48)) \
        .arc(w / 2, g.M, w / 2, g.M - g.B + OVERSHOOT, 48, 312).done()
    return "RO"


def latin_D(g):
    g.line((0, 0), (0, g.H))
    g.bowl(0, g.T, g.B, g.W(.74))
    return "SR"


def latin_G(g):
    w, ry = g.W(.80), g.M - g.B + OVERSHOOT
    y = .44 * g.H
    (g.path().move(*on_ellipse(w / 2, g.M, w / 2, ry, 48))
     .arc(w / 2, g.M, w / 2, ry, 48, 352).to(w, y).to(.56 * w, y).done())
    return "RO"


def latin_L(g):
    g.line((0, g.H), (0, 0))
    g.line((0, g.B), (g.W(.52), g.B))
    return "SO"


def latin_Q(g):
    w = g.W(.88)
    circle_O(g, w)
    start = on_ellipse(w / 2, g.M, w / 2, g.M - g.B + OVERSHOOT, -80)   # on the bowl, so only the tail end flares
    g.line(start, (1.0 * w, -.16 * g.H), clip=None)
    return "RR"


def latin_R(g):
    w = g.W(.60)
    g.line((0, 0), (0, g.H))
    g.bowl(0, g.T, .44 * g.H, g.W(.54))
    g.line((.34 * w, .44 * g.H), (w, 0))
    return "SD"


def latin_S(g):
    w, m = g.W(.56), .53 * g.H
    r1 = (g.T - m) / 2 + OVERSHOOT / 2
    r2 = (m - g.B) / 2 + OVERSHOOT / 2
    rx1, rx2 = .46 * w, .5 * w
    (g.path().move(*on_ellipse(w / 2, m + r1, rx1, r1, 25))
     .arc(w / 2, m + r1, rx1, r1, 25, 270)
     .arc(w / 2, m - r2, rx2, r2, 90, -155).done())
    return "OO"


def latin_U(g):
    w, cy = g.W(.66), .40 * g.H
    (g.path(clip=(-OVERSHOOT, g.H)).move(0, g.H).to(0, cy)
     .arc(w / 2, cy, w / 2, cy - g.B + OVERSHOOT, 180, 360).to(w, g.H).done())
    return "SS"


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
    ("U", 0x55, "u", [0x75], latin_U),
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

# Precomposed long vowels, Greek and romanized: (name, codes, base glyph)
MACRONS = [
    ("Alphamacron", [0x1FB9, 0x100], "Alpha"), ("alphamacron", [0x1FB1, 0x101], "alpha"),
    ("Upsilonmacron", [0x1FE9], "Upsilon"), ("upsilonmacron", [0x1FE1], "upsilon"),
    ("Epsilonmacron", [0x112], "Epsilon"), ("epsilonmacron", [0x113], "epsilon"),
    ("Iotamacron", [0x12A], "Iota"), ("iotamacron", [0x12B], "iota"),
    ("Omicronmacron", [0x14C], "Omicron"), ("omicronmacron", [0x14D], "omicron"),
    ("Umacron", [0x16A], "U"), ("umacron", [0x16B], "u"),
]
MACRON_GAP = 56


# ---------------------------------------------------------------------------
# Digits (at small-capital height, to sit with running text) and punctuation
# ---------------------------------------------------------------------------

def d0(g):
    circle_O(g, g.W(.62))
    return "RR"


def d1(g):
    g.line((-g.W(.20), .78 * g.H), (0, g.H), (0, 0))
    return "SS"


def d2(g):
    w = g.W(.60)
    ry = .28 * g.H
    cy = g.T - ry + OVERSHOOT
    (g.path(clip=True).move(*on_ellipse(w / 2, cy, w / 2, ry, 160))
     .arc(w / 2, cy, w / 2, ry, 160, -35).to(0, g.B).to(w, g.B).done())
    return "OO"


def d3(g):
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
    w = g.W(.58)
    ry = .32 * g.H
    cy = g.B + ry - OVERSHOOT
    start = on_ellipse(w / 2, cy, w / 2, ry, 135)
    g.line((w * .94, g.T), (w * .08, g.T), (start[0], .56 * g.H), clip=True)
    (g.path(clip=None).move(start[0], .56 * g.H).to(*start)
     .arc(w / 2, cy, w / 2, ry, 135, -150).done())
    return "OR"


def d6(g):
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
    w, m = g.W(.60), .56 * g.H
    r1 = (g.T - m) / 2 + OVERSHOOT / 2
    r2 = (m - g.B) / 2 + OVERSHOOT / 2
    g.ellipse(w / 2, m + r1, .42 * w, r1)
    g.ellipse(w / 2, m - r2, .5 * w, r2)
    return "RR"


def d9(g):
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


def make(fn, height, stroke, width_unit):
    g = Shape(height, stroke, width_unit)
    sides = fn(g)
    scale = (height / CAP) ** .6
    return Glyph(outline(g), sides[0], sides[1], scale)


def draw(glyph, pen):
    glyph.path.draw(TransformPen(pen, (1, 0, 0, 1, glyph.dx, 0)))


def add_macron(glyph, height, stroke):
    """Return a copy of a glyph with a macron bar centred above it."""
    g = Shape(height, stroke * .8, 1)
    y = height + MACRON_GAP + g.s / 2
    half = min(glyph.advance * .3, height * .3)
    c = glyph.advance / 2 - glyph.dx
    g.line((c - half, y), (c + half, y), clip=None)
    bar = outline(g)
    merged = pathops.op(glyph.path, bar, pathops.PathOp.UNION)
    new = Glyph.__new__(Glyph)
    new.path, new.dx, new.advance = merged, glyph.dx, glyph.advance
    return new


def build_glyphs():
    glyphs, cmap = {}, {}
    for cap_name, cap_code, small_name, small_codes, fn in LETTERS:
        glyphs[cap_name] = make(fn, CAP, CAP_STROKE, CAP)
        cmap[cap_code] = cap_name
        glyphs[small_name] = make(fn, SMALL, SMALL_STROKE, SMALL * 1.06)
        for code in small_codes:
            cmap[code] = small_name
    for latin, greek in SAME_AS_GREEK.items():
        cmap[ord(latin)] = greek
        cmap[ord(latin.lower())] = greek.lower()
    for name, codes, base in MACRONS:
        small = base[0].islower()
        glyphs[name] = add_macron(glyphs[base], SMALL if small else CAP, SMALL_STROKE if small else CAP_STROKE)
        for code in codes:
            cmap[code] = name
    for name, code, fn in DIGITS:
        glyphs[name] = make(fn, SMALL, SMALL_STROKE, SMALL * 1.06)
        cmap[code] = name
    for name, codes, fn in PUNCTUATION:
        glyphs[name] = make(fn, CAP, SMALL_STROKE, CAP)
        for code in codes:
            cmap[code] = name
    # The combining macron, for text written with a separate U+0304
    g = Shape(SMALL, SMALL_STROKE * .8, 1)
    y = SMALL + MACRON_GAP + g.s / 2
    g.line((-.15 * SMALL, y), (.15 * SMALL, y), clip=None)
    mark = Glyph.__new__(Glyph)
    mark.path, mark.dx, mark.advance = outline(g), 0, 0
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


def build():
    glyphs, cmap = build_glyphs()
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
    ascent, descent = 900, -260
    fb.setupHorizontalHeader(ascent=ascent, descent=descent)
    fb.setupNameTable({
        "familyName": FAMILY,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{FAMILY.replace(' ', '')}-Regular-{VERSION}",
        "fullName": f"{FAMILY} Regular",
        "psName": f"{FAMILY.replace(' ', '')}-Regular",
        "version": f"Version {VERSION}",
        "description": "An inscriptional typeface for the Tharaic alphabet. Lowercase letters are small capitals.",
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
    fb.font.save(out / "TharaicStele.ttf")
    fb.font.flavor = "woff2"
    fb.font.save(out / "TharaicStele.woff2")
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


def specimen(font):
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
           f'<rect width="100%" height="100%" fill="#f4efe6"/>\n<g fill="#2b2622">\n'
           + "\n".join(body) + "\n</g>\n</svg>\n")
    (ROOT / "docs" / "font-specimen.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    font = build()
    specimen(font)
    print(f"Built font/TharaicStele.ttf and .woff2 ({len(font.getGlyphOrder())} glyphs) and docs/font-specimen.svg")
