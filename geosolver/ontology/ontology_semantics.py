import itertools
import numpy as np
from geosolver.diagram.computational_geometry import distance_between_line_and_point, line_length, \
    distance_between_points, angle_in_radian
from geosolver.ontology.instantiator_definitions import instantiators
from geosolver.text2.ontology import FormulaNode, signatures, VariableSignature, issubtype, SetNode, Node
import sys
from geosolver.utils.num import is_number
import operator


this = sys.modules[__name__]

__author__ = 'minjoon'

class TruthValue(object):
    def __init__(self, value, std=1):
        self.norm = value
        self.std = std
        if std == 0:
            self.conf = 0
        else:
            self.conf = 1-min(1, value/std)

    def __and__(self, other):
        if isinstance(other, TruthValue):
            if self.conf > other.conf:
                return other
            return self
        elif other is True:
            return self
        else:
            raise Exception()

    def __or__(self, other):
        if isinstance(other, TruthValue):
            if self.conf > other.conf:
                return self
            return other
        elif other is False:
            return self
        else:
            raise Exception()

    def __rand__(self, other):
        return self.__and__(other)

    def __ror__(self, other):
        return self.__or__(other)

    def __repr__(self):
        return "TV(conf=%.2f)" % self.conf

def Line(p1, p2):
    return instantiators['line'](p1, p2)

def Arc(circle, p1, p2):
    return instantiators['arc'](circle, p1, p2)

def Circle(p, r):
    return instantiators['circle'](p, r)

def Point(x, y):
    return instantiators['point'](x, y)

def Angle(a, b, c):
    return instantiators['angle'](a, b, c)

def Triangle(a, b, c):
    return instantiators['triangle'](a, b, c)

def Quad(a, b, c, d):
    return instantiators['quad'](a, b, c, d)

def Hexagon(a, b, c, d, e, f):
    return instantiators['polygon'](a, b, c, d, e, f)

def Polygon(*p):
    return instantiators['polygon'](*p)

def LengthOf(line):
    return line_length(line)

def RadiusOf(circle):
    return circle.radius

def Equals(a, b):
    std = abs((a+b)/2.0)
    value = abs(a-b)
    out = TruthValue(value, std)
    return out

def Greater(a, b):
    std = abs((a+b)/2.0)
    value = max(b-a, 0)
    return TruthValue(value, std)

def Less(a, b):
    std = abs((a+b)/2.0)
    value = max(a-b, 0)
    return TruthValue(value, std)

def Sqrt(x):
    return np.sqrt(x)

def Add(a, b):
    return a + b

def Sub(a, b):
    return a - b

def Mul(a, b):
    return a * b

def Div(a, b):
    return float(a) / b

def Pow(a, b):
    return a**b

def Or(a, b):
    if a.conf > b.conf:
        return a
    return b

def Tangent(line, circle):
    d = distance_between_line_and_point(line, circle.center)
    return Equals(d, circle.radius)

def IsDiameterLineOf(line, circle):
    return IsChordOf(line, circle) & Equals(LengthOf(line), 2*circle.radius)

def PointLiesOnCircle(point, circle):
    d = distance_between_points(point, circle.center)
    return Equals(d, circle.radius)

def IsChordOf(line, circle):
    return PointLiesOnCircle(line.a, circle) & PointLiesOnCircle(line.b, circle)

def Perpendicular(l1, l2):
    return Equals((l1.b.y-l1.a.y)*(l2.b.y-l2.a.y), (l1.a.x-l1.b.x)*(l2.b.x-l2.a.x))

def Colinear(A, B, C):
    line = instantiators['line'](A, C)
    eq = Equals(LengthOf(line), distance_between_points(line.a, B) + distance_between_points(line.b, B))
    return eq

def PointLiesOnLine(point, line):
    return Colinear(line[0], point, line[1])

def IsMidpointOf(point, line):
    line_a = Line(line.a, point)
    line_b = Line(point, line.b)
    e = Equals(LengthOf(line_a), LengthOf(line_b))
    l = PointLiesOnLine(point, line)
    return e & l

def IsTriangle(triangle):
    if isinstance(triangle, instantiators['triangle']):
        return TruthValue(0)
    else:
        return TruthValue(np.inf)

def IsLine(line):
    if isinstance(line, instantiators['line']):
        return TruthValue(0)
    else:
        return TruthValue(np.inf)

def IsAngle(angle):
    if isinstance(angle, instantiators['angle']):
        return TruthValue(0)
    else:
        return TruthValue(np.inf)

def IsPoint(point):
    if isinstance(point, instantiators['point']):
        return TruthValue(0)
    else:
        return TruthValue(np.inf)

def IsInscribedIn(triangle, circle):
    out = reduce(operator.__and__, (PointLiesOnCircle(point, circle) for point in triangle), True)
    return out

def IsCenterOf(point, circle):
    return Equals(point[0], circle.center[0]) & Equals(point[1], circle.center[1])

def IntersectAt(lines, point):
    assert isinstance(lines, SetNode)
    out = reduce(operator.__and__, (PointLiesOnLine(point, line) for line in lines.children), True)
    return out

def Equilateral(triangle):
    lines = [instantiators['line'](triangle[index-1], point) for index, point in enumerate(triangle)]
    return Equals(LengthOf(lines[0]), LengthOf(lines[1])) & Equals(LengthOf(lines[1]), LengthOf(lines[2]))

def IsSquare(quad):
    lines = [instantiators['line'](quad[index-1], point) for index, point in enumerate(quad)]
    return Equals(LengthOf(lines[0]), LengthOf(lines[1])) & \
           Equals(LengthOf(lines[1]), LengthOf(lines[2])) & Equals(LengthOf(lines[2]), LengthOf(lines[3]))

def AreaOf(twod):
    name = twod.__class__.__name__
    assert issubtype(name, 'twod')
    if name == "circle":
        center, radius = twod
        area = np.pi * radius ** 2
    elif issubtype(name, 'polygon'):
        # http://mathworld.wolfram.com/PolygonArea.html
        area = sum(twod[index-1][0]*p[1]-p[0]*twod[index-1][1] for index, p in enumerate(twod))
    else:
        raise Exception()
    return area

def MeasureOf(angle):
    return angle_in_radian(angle)

def IsAreaOf(number, twod):
    return Equals(number, AreaOf(twod))

def IsLengthOf(number, line):
    return Equals(number, LengthOf(line))

def IsPolygon(polygon):
    return TruthValue(0)

def Isosceles(triangle):
    sides = [distance_between_points(triangle[index-1], point) for index, point in enumerate(triangle)]
    combs = itertools.combinations(sides, 2)

    out = reduce(operator.__or__, (Equals(a, b) for a, b in combs), False)
    return out

def BisectsAngle(line, angle):
    on = PointLiesOnLine(angle[1], line)
    distant_point = line[0]
    if distant_point == angle[1]:
        distant_point = line[1]
    a0 = instantiators['angle'](angle[0], angle[1], distant_point)
    a1 = instantiators['angle'](distant_point, angle[1], angle[2])
    eq = Equals(MeasureOf(a0), MeasureOf(a1))
    return on & eq

def Three(entities):
    if len(entities.children) == 3:
        return TruthValue(0)
    return TruthValue(np.inf)

def Two(entities):
    if len(entities.children) == 2:
        return TruthValue(0)
    return TruthValue(np.inf)

def evaluate(function_node, assignment):
    if isinstance(function_node, SetNode):
        assert function_node.head.return_type == 'truth'
        out = reduce(operator.__and__, (evaluate(child, assignment) for child in function_node.children), True)
        return out

    if isinstance(function_node.signature, VariableSignature):
        return assignment[function_node.signature.id]
    elif is_number(function_node.signature.id):
        return float(function_node.signature.id)
    else:
        evaluated_args = []
        for arg in function_node.children:
            if isinstance(arg, FormulaNode):
                evaluated_args.append(evaluate(arg, assignment))
            elif isinstance(arg, SetNode):
                evaluated_args.append(SetNode([evaluate(arg_arg, assignment) for arg_arg in arg.children]))
            else:
                evaluated_args.append(arg)
        return getattr(this, function_node.signature.id)(*evaluated_args)
