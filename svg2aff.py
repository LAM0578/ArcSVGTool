# NCat 20240905
import numpy as np
from math import (
    tau as _tau,
    sqrt as _sqrt,
    sin as _sin,
    cos as _cos,
    acos as _acos,
    radians as _rad,
    fmod as _fmod
)
from mathHelper import *
import struct

_MIN_CURVE_COUNT = 3
_LENGTH_SCALE = 30

class helper:

    @staticmethod
    def genArc(t, pa, pb, p):
        if pa.y > pb.y:
            (pa, pb) = (pb, pa)
        return f'arc({t},{t},{pa.x:{p}},{pb.x:{p}},s,{pa.y:{p}},{pb.y:{p}},0,none,true);'
        # return 'arc({},{},{:.2f},{:.2f},s,{:.2f},{:.2f},0,none,true);'.format(
        #     t,
        #     t,
        #     pa.x,
        #     pb.x,
        #     pa.y,
        #     pb.y
        # )
    
def castToInt(f):
    return struct.unpack('i', struct.pack('f', f))[0]

def autoCalculateCount(length):
    oLength = length
    length *= _LENGTH_SCALE
    count = length / 3
    count /= oLength
    return min(max(_MIN_CURVE_COUNT, int(count)), 32)

def calcQuadBezierCount(p0, p1, p2, count, interval, useInterval, autoCurveCount):
    if autoCurveCount or useInterval:
        length = quad_bezier_length(p0.toNpArray(), p1.toNpArray(), p2.toNpArray())
    if autoCurveCount:
        return autoCalculateCount(length)
    if useInterval:
        count = length / interval
        return max(_MIN_CURVE_COUNT, int(count))
    return count

def calcCubicBezierCount(p0, p1, p2, p3, count, interval, useInterval, autoCurveCount):
    if autoCurveCount or useInterval:
        length = cubic_bezier_length(p0.toNpArray(), p1.toNpArray(), p2.toNpArray(), p3.toNpArray())
    if autoCurveCount:
        return autoCalculateCount(length)
    if useInterval:
        count = length / interval
        return max(_MIN_CURVE_COUNT, int(count))
    return count

def calcEllipticalArcCount(p0, rx, ry, xAxisRotation, largeArcFlag, sweepFlag, p1, count, interval, useInterval, autoCurveCount):
    if autoCurveCount or useInterval:
        length = elliptical_arc_length(p0.toNpArray(), rx, ry, xAxisRotation, largeArcFlag, sweepFlag, p1.toNpArray())
    if autoCurveCount:
        return autoCalculateCount(length)
    if useInterval:
        count = length / interval
        return max(_MIN_CURVE_COUNT, int(count))
    return count

def simpleList(l):
    result = []
    for i in l:
        if i is None or i in result:
            continue
        result.append(i)
    return result

def lengthOfTwoPoints(p0, p1):
    return _sqrt(_pow2(p1.x - p0.x) + _pow2(p1.y - p0.y))

def _dot(p0, p1):
    return p0.x * p1.x + p0.y * p1.y

def _angleBetween(p0, p1):
    p = _dot(p0, p1)
    n = _sqrt(_dot(p0, p0) * _dot(p1, p1))
    if p0.x * p1.y - p0.y * p1.x < 0:
        sign = -1.
    else:
        sign = 1.

    return sign * _acos(p / n)

def _pointOnLine(p0, p1, t):
    return p0 + (p1 - p0) * t

def _pow2(x):
    return x ** 2.

class point:
    def __init__(self, x, y=None):
        self.x = x
        self.y = y
        if y is None:
            self.y = x

    def trans(self, offset, scale, scaleFirst):
        if scaleFirst:
            return self * scale + offset
        return (self + offset) * scale

    def __add__(self, other):
        return point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return point(self.x - other.x, self.y - other.y)
    
    def __truediv__(self, other):
        if isinstance(other, (float, int)):
            return point(self.x / other, self.y / other)
        
        return point(self.x / other.x, self.y / other.y)
    
    def __mul__(self, other):
        if isinstance(other, (float, int)):
            return point(self.x * other, self.y * other)
        
        return point(self.x * other.x, self.y * other.y)
    
    def __eq__(self, other):
        if not isinstance(other, point):
            return False
        return self.x == other.x and self.y == other.y
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    @staticmethod
    def fromArgs(*args):
        return point(args[0], args[1])
    
    def modifyValue(self, idx, val):
        if idx == 0:
            self.x = val
        elif idx == 1:
            self.y = val

    def toIntPoint(self):
        return point(int(self.x), int(self.y))

    def clone(self):
        return point(self.x, self.y)
    
    def toNpArray(self):
        return np.array([self.x, self.y])
    
    def roundNdigits(self, n):
        return point(round(self.x, n), round(self.y, n))
    
    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

class svgCommand:
    def __init__(self, commandType, isAbs, args):
        self.__commandType = commandType
        self.__isAbs = isAbs
        self.__args = args

    @property
    def commandType(self):
        return self.__commandType
    
    @property
    def lowerCommandType(self):
        return self.__commandType.lower()
    
    @property 
    def isAbs(self):
        return self.__isAbs
    
    @property
    def args(self):
        return self.__args
        
    @staticmethod
    def __tryParseNumber(raw):
        try:
            return int(raw)
        except:
            try:
                return float(raw)
            except:
                return

    @staticmethod
    def parseCommand(cmd):
        cmd = cmd.strip()
        splits = cmd.split(' ')

        commandType = splits[0]
        isAbs = commandType.isupper()
        args = []

        for item in splits[1:]:
            arg = svgCommand.__tryParseNumber(item)

            if arg != None:
                args.append(arg)

        return svgCommand(commandType, isAbs, args)
    
    def __str__(self):
        commandType = self.__commandType

        if self.__isAbs:
            commandType = commandType.upper()

        args = ' '.join([str(a) for a in self.__args])

        return commandType + ' ' + args
    

class svgGroups:
    def __init__(self, groups):
        self.__groups = groups

    @staticmethod
    def __genArc(t, pa, pb):
        if pa == pb:
            return None
        return 'arc({},{},{:.2f},{:.2f},s,{:.2f},{:.2f},0,none,true);'.format(
            t,
            t,
            pa.x,
            pb.x,
            pa.y,
            pb.y
        )
    
    @staticmethod
    def __quadraticBezierCurves(p0, p1, p2, t):
        o = 1 - t
        return (
            pow(o, 2) * p0 +
            2 * o * p1 * t +
            pow(t, 2) * p2
        )

    @staticmethod
    def __cubicBezierCurves(p0, p1, p2, p3, t):
        o = 1 - t
        return (
            pow(o, 3) * p0 +
            3 * pow(o, 2) * t * p1 +
            3 * o * pow(t, 2) * p2 +
            pow(t, 3) * p3
        )
    
    @staticmethod
    def __quadBezierCurvesPoint(p0, p1, p2, t):
        return point(
            svgGroups.__quadraticBezierCurves(
                p0.x, p1.x, p2.x, t
            ),
            svgGroups.__quadraticBezierCurves(
                p0.y, p1.y, p2.y, t
            )
        )
    
    @staticmethod
    def __cubicBezierCurvesPoint(p0, p1, p2, p3, t):
        return point(
            svgGroups.__cubicBezierCurves(
                p0.x, p1.x, p2.x, p3.x, t
            ),
            svgGroups.__cubicBezierCurves(
                p0.y, p1.y, p2.y, p3.y, t
            )
        )

    @staticmethod
    def __ellipticalArc(
            p0,
            rx,
            ry,
            xAxisRotation,
            largeArcFlag,
            sweepFlag,
            p1,
            t
        ):
        
        rx = abs(rx)
        ry = abs(ry)
        xAxisRotation = _fmod(xAxisRotation, 360.)
        xAxisRotationRadians = _rad(xAxisRotation)
        # If the endpoints are identical, then this is equivalent to omitting the elliptical arc segment entirely.
        if p0 == p1:
            return p0
        
        # If rx = 0 or ry = 0 then this arc is treated as a straight line segment joining the endpoints.
        if rx == 0 or ry == 0:
            return _pointOnLine(p0, p1, t)
        
        # Following "Conversion from endpoint to center parameterization"
        # http://www.w3.org/TR/SVG/implnote.html#ArcConversionEndpointToCenter

        # Step #1: Compute transformedPoint
        dx = (p0.x - p1.x) / 2.
        dy = (p0.y - p1.y) / 2.
        transformedPoint = point(
            _cos(xAxisRotationRadians) * dx + _sin(xAxisRotationRadians) * dy,
            -_sin(xAxisRotationRadians) * dx + _cos(xAxisRotationRadians) * dy
        )

        # Ensure radii are large enough
        radiiCheck = _pow2(transformedPoint.x) / _pow2(rx) + _pow2(transformedPoint.y) / _pow2(ry)
        if radiiCheck > 1:
            rx = _sqrt(radiiCheck) * rx
            ry = _sqrt(radiiCheck) * ry

        # Step #2: Compute transformedCenter
        cSquareNumerator = _pow2(rx) * _pow2(ry) - _pow2(rx) * _pow2(transformedPoint.y) - _pow2(ry) * _pow2(transformedPoint.x)
        cSquareRootDenom = _pow2(rx) * _pow2(transformedPoint.y) + _pow2(ry) * _pow2(transformedPoint.x)
        cRadicand = cSquareNumerator / cSquareRootDenom
        # Make sure this never drops below zero because of precision
        if cRadicand < 0:
            cRadicand = 0
        if largeArcFlag != sweepFlag:
            cCoefMul = 1
        else:
            cCoefMul = -1
        cCoef = cCoefMul * _sqrt(cRadicand)
        transformedCenter = point(
            cCoef * ((rx * transformedPoint.y) / ry),
            cCoef * (-(ry * transformedPoint.x) / rx)
        )
        
        # Step #3: Compute center
        center = point(
            _cos(xAxisRotationRadians) * transformedCenter.x - _sin(xAxisRotationRadians) * transformedCenter.y + ((p0.x + p1.x) / 2.),
            _sin(xAxisRotationRadians) * transformedCenter.x + _cos(xAxisRotationRadians) * transformedCenter.y + ((p0.y + p1.y) / 2.)
        )
        
        # Step #4: Compute start/sweep angles
        # Start angle of the elliptical arc prior to the stretch and rotate operations.
        # Difference between the start and end angles
        startVector = point(
            (transformedPoint.x - transformedCenter.x) / rx,
            (transformedPoint.y - transformedCenter.y) / ry
        )
        startAngle = _angleBetween(point(1., 0.), startVector)

        endVector = point(
            (-transformedPoint.x - transformedCenter.x) / rx,
            (-transformedPoint.y - transformedCenter.y) / ry
        )
        sweepAngle = _angleBetween(startVector, endVector)

        if (not sweepFlag) and sweepAngle > 0:
            sweepAngle -= _tau
        elif sweepFlag and sweepAngle < 0:
            sweepAngle += _tau
        # We use % instead of `mod(..)` because we want it to be -360deg to 360deg(but actually in radians)
        sweepAngle = _fmod(sweepAngle, _tau)

        # From http://www.w3.org/TR/SVG/implnote.html#ArcParameterizationAlternatives
        angle = startAngle + (sweepAngle * t)
        ellipseComponentX = rx * _cos(angle)
        ellipseComponentY = ry * _sin(angle)

        return point(
            _cos(xAxisRotationRadians) * ellipseComponentX - _sin(xAxisRotationRadians) * ellipseComponentY + center.x,
            _sin(xAxisRotationRadians) * ellipseComponentX + _cos(xAxisRotationRadians) * ellipseComponentY + center.y
        )
    
    def svg2lines(self, offset, scale, scaleFirst, curveCount, curveInterval, curveUseInterval, autoCurveCount, ndigits):
        result = []
        for group in self.__groups:
            
            hasZ = group[1]
            group = group[0]
            lastMovePosition = point(0, 0)
            lastPosition = point(0, 0)
            
            for cmd in group:

                if not isinstance(cmd, svgCommand):
                    continue

                cmdType = cmd.lowerCommandType
                cmdIsAbs = cmd.isAbs
                
                if cmdType == 'm':
                    position = point.fromArgs(*cmd.args)

                    if cmdIsAbs:
                        lastPosition = position.clone()
                    else:
                        lastPosition += position

                    lastMovePosition = lastPosition
                
                elif cmdType == 'l':
                    position = point.fromArgs(*cmd.args)

                    targetPosition = lastPosition.clone()

                    if cmdIsAbs:
                        targetPosition = position.clone()
                    else:
                        targetPosition += position

                    result.append((
                        lastPosition.trans(offset, scale, scaleFirst), 
                        targetPosition.trans(offset, scale, scaleFirst)
                    ))

                    lastPosition = targetPosition

                elif cmdType == 'v':
                    position = point(0, cmd.args[0])

                    targetPosition = lastPosition.clone()

                    if cmdIsAbs:
                        targetPosition.y = position.y
                    else:
                        targetPosition.y += position.y
                    
                    result.append((
                        lastPosition.trans(offset, scale, scaleFirst), 
                        targetPosition.trans(offset, scale, scaleFirst)
                    ))

                    lastPosition = targetPosition

                elif cmdType == 'h':
                    position = point(cmd.args[0], 0)

                    targetPosition = lastPosition.clone()

                    if cmdIsAbs:
                        targetPosition.x = position.x
                    else:
                        targetPosition.x += position.x
                    
                    result.append((
                        lastPosition.trans(offset, scale, scaleFirst), 
                        targetPosition.trans(offset, scale, scaleFirst)
                    ))

                    lastPosition = targetPosition

                elif cmdType == 'q':
                    cp0 = lastPosition.clone()
                    cp1 = point(cmd.args[0], cmd.args[1])
                    cp2 = point(cmd.args[2], cmd.args[3])

                    if not cmdIsAbs:
                        cp1 += lastPosition
                        cp2 += lastPosition

                    lastCurvePosition = lastPosition
                    realCount = calcQuadBezierCount(
                        cp0,
                        cp1,
                        cp2,
                        curveCount,
                        curveInterval,
                        curveUseInterval,
                        autoCurveCount
                    )
                    for i in range(realCount):
                        if realCount <= 1:
                            p = 0
                        else:
                            p = i / (realCount - 1.)
                        position = self.__quadBezierCurvesPoint(
                            cp0,
                            cp1,
                            cp2,
                            p
                        )
                        result.append((
                            lastCurvePosition.trans(offset, scale, scaleFirst), 
                            position.trans(offset, scale, scaleFirst)
                        ))
                        lastCurvePosition = position

                    lastPosition = lastCurvePosition

                elif cmdType == 'c':
                    cp0 = lastPosition.clone()
                    cp1 = point(cmd.args[0], cmd.args[1])
                    cp2 = point(cmd.args[2], cmd.args[3])
                    cp3 = point(cmd.args[4], cmd.args[5])

                    if not cmdIsAbs:
                        cp1 += lastPosition
                        cp2 += lastPosition
                        cp3 += lastPosition

                    lastCurvePosition = lastPosition
                    realCount = calcCubicBezierCount(
                        cp0,
                        cp1,
                        cp2,
                        cp3,
                        curveCount,
                        curveInterval,
                        curveUseInterval,
                        autoCurveCount
                    )
                    for i in range(realCount):
                        if realCount <= 1:
                            p = 0
                        else:
                            p = i / (realCount - 1.)
                        position = self.__cubicBezierCurvesPoint(
                            cp0,
                            cp1,
                            cp2,
                            cp3,
                            p
                        )
                        result.append((
                            lastCurvePosition.trans(offset, scale, scaleFirst), 
                            position.trans(offset, scale, scaleFirst)
                        ))
                        lastCurvePosition = position

                    lastPosition = lastCurvePosition

                elif cmdType == 't':
                    cp0 = lastPosition.clone()
                    cp1 = lastPosition.clone()
                    cp2 = point(cmd.args[0], cmd.args[1])

                    if not cmdIsAbs:
                        cp1 += lastPosition
                        cp2 += lastPosition

                    lastCurvePosition = lastPosition
                    realCount = calcQuadBezierCount(
                        cp0,
                        cp1,
                        cp2,
                        curveCount,
                        curveInterval,
                        curveUseInterval,
                        autoCurveCount
                    )
                    for i in range(realCount):
                        if realCount <= 1:
                            p = 0
                        else:
                            p = i / (realCount - 1.)
                        position = self.__quadBezierCurvesPoint(
                            cp0,
                            cp1,
                            cp2,
                            p
                        )
                        result.append((
                            lastCurvePosition.trans(offset, scale, scaleFirst), 
                            position.trans(offset, scale, scaleFirst)
                        ))
                        lastCurvePosition = position

                    lastPosition = lastCurvePosition

                elif cmdType == 's':
                    cp0 = lastPosition.clone()
                    cp1 = lastPosition.clone()
                    cp2 = point(cmd.args[0], cmd.args[1])
                    cp3 = point(cmd.args[2], cmd.args[3])

                    if not cmdIsAbs:
                        cp2 += lastPosition
                        cp3 += lastPosition

                    lastCurvePosition = lastPosition
                    realCount = calcCubicBezierCount(
                        cp0,
                        cp1,
                        cp2,
                        cp3,
                        curveCount,
                        curveInterval,
                        curveUseInterval,
                        autoCurveCount
                    )
                    for i in range(realCount):
                        if realCount <= 1:
                            p = 0
                        else:
                            p = i / (realCount - 1.)
                        position = self.__cubicBezierCurvesPoint(
                            cp0,
                            cp1,
                            cp2,
                            cp3,
                            p
                        )
                        result.append((
                            lastCurvePosition.trans(offset, scale, scaleFirst), 
                            position.trans(offset, scale, scaleFirst)
                        ))
                        lastCurvePosition = position

                    lastPosition = lastCurvePosition

                elif cmdType == 'a':
                    p0 = lastPosition.clone()

                    (rx,
                    ry,
                    xAxisRotation,
                    largeArcFlag,
                    sweepFlag,
                    p1x,
                    p1y) = cmd.args

                    p1 = point(p1x, p1y)

                    if not cmd.isAbs:
                        p1 += lastPosition
                    
                    lastCurvePosition = lastPosition
                    realCount = calcEllipticalArcCount(
                        p0,
                        rx,
                        ry,
                        xAxisRotation,
                        largeArcFlag,
                        sweepFlag,
                        p1,
                        curveCount,
                        curveInterval,
                        curveUseInterval,
                        autoCurveCount
                    )
                    for i in range(realCount):
                        if realCount <= 1:
                            p = 0
                        else:
                            p = i / (realCount - 1.)
                        position = svgGroups.__ellipticalArc(
                            p0,
                            rx,
                            ry,
                            xAxisRotation,
                            largeArcFlag,
                            sweepFlag,
                            p1,
                            p
                        )
                        result.append((
                            lastCurvePosition.trans(offset, scale, scaleFirst), 
                            position.trans(offset, scale, scaleFirst)
                        ))
                        lastCurvePosition = position

                    lastPosition = lastCurvePosition

            if hasZ:
                result.append((
                    lastPosition.trans(offset, scale, scaleFirst), 
                    lastMovePosition.trans(offset, scale, scaleFirst)
                ))
        
        nResult = []
        nHashCodes = []
        for l in result:
            l = list(map(lambda x: x.roundNdigits(ndigits), l))
            if l[0] == l[1]:
                continue
            h = -120818822
            h = h * -1521134295 + castToInt(l[0].x)
            h = h % (2 ** 63 - 1) - (2 ** 31 - 1)
            h = h * -1521134295 + castToInt(l[0].y)
            h = h % (2 ** 63 - 1) - (2 ** 31 - 1)
            h = h * -1521134295 + castToInt(l[1].x)
            h = h % (2 ** 63 - 1) - (2 ** 31 - 1)
            h = h * -1521134295 + castToInt(l[1].y)
            h = h % (2 ** 63 - 1) - (2 ** 31 - 1)
            if h in nHashCodes:
                # print('!', h)
                continue
            nHashCodes.append(h)
            length = lengthOfTwoPoints(*l)
            if length < (10 ** (-ndigits)):
                continue
            nResult.append(l)
        
        result = nResult
        return result

def parseCommands(raw: str):

    strLen = len(raw)
    i = 0
    
    commands = []
    lastCommand = ''

    commandIdentifier = [
        'm', # Move to
        'l', # Line to
        'q', # Quad Curve to
        't', # Shorthand Quad Curve to
        'c', # Cubic Curve to
        's', # Shorthand Cubic Curve to
        'v', # Vertical Line to
        'h', # Horizontal Line to
        'a', # Elliptical Arc
        'z'  # Close path
    ]
    
    numberChars = '1234567890-+.'

    commandTypeHasSpace = False
    
    while i < strLen:
        c = raw[i]

        if c.lower() in commandIdentifier:

            if lastCommand != '':
                commands.append(lastCommand)
                
            lastCommand = c + ' '

            commandTypeHasSpace = True

            i += 1
            continue
        
        elif c in numberChars:
            if c in [ '+', '-' ] and lastCommand[-1] != ' ':
                lastCommand += ' '
            lastCommand += c

        elif (c == ' ' or c == ',') and (not commandTypeHasSpace):
            lastCommand += ' '
        
        if commandTypeHasSpace:
            commandTypeHasSpace = False

        i += 1

    if lastCommand != '':
        commands.append(lastCommand)

    return commands

def svgPath2Aff(raw, tick, offset, scale, scaleFirst, curveCount, curveInterval, curveUseInterval, autoCurveCount, format_):
    if format_[0] == 'f':
        ndigits = int(format_[1:])
        format_ = f'.{format_[1:]}f'
    
    lines = svgPath2Lines(raw, offset, scale, scaleFirst, curveCount, curveInterval, curveUseInterval, autoCurveCount, ndigits)
    result = []

    for line in lines:
        result.append(helper.genArc(tick, line[0], line[1], format_))

    result = '\n'.join(result)
    return result

def svgPath2Lines(raw, offset, scale, scaleFirst, curveCount, curveInterval, curveUseInterval, autoCurveCount, ndigits):
    global _LENGTH_SCALE

    _LENGTH_SCALE = max(abs(scale.x), abs(scale.y)) * 25

    commands = parseCommands(raw)
    parsedCommands = []

    for cmd in commands:
        parsedCommands.append(svgCommand.parseCommand(cmd))

    groups = []
    lastGroup = []
    hasZ = False

    for cmd in parsedCommands:

        if cmd.lowerCommandType == 'z':
            hasZ = True
            groups.append((lastGroup, hasZ))
            lastGroup = []
            hasZ = False

        lastGroup.append(cmd)

    if lastGroup != []:
        groups.append((lastGroup, hasZ))
    
    groups = svgGroups(groups)
    return groups.svg2lines(offset, scale, scaleFirst, curveCount, curveInterval, curveUseInterval, autoCurveCount, ndigits)


def __main(*args):
    (
        svgRaw,
        tick,
        scale,
        scaleFirst,
        curveCount,
        curveInterval,
        curveUseInterval,
        autoCurveCount,
        writeToFile,
        outputPath
    ) = args
    
    outputStr = svgPath2Aff(svgRaw, tick, offset, scale, scaleFirst, curveCount, curveInterval, curveUseInterval, autoCurveCount, 2)

    if writeToFile:
        with open(outputPath, 'w') as f:
            f.write(outputStr)

    else:
        print(outputStr)


if __name__ == '__main__':
    # 使用时请到 https://yqnn.github.io/svg-path-editor/ 格式化一下 (请不要使用 Minify output 输出) ，因为这个解析器对格式比较严格
    # Please format it at https://yqnn.github.io/svg-path-editor/ (do not use the 'Minify output' output), as this parser is very strict about formatting. (deepl)

    # scaleFirst
    # True: p * scale + offset
    # False: (p + offset) * scale

    svgRaw = '''
    M 0 0 l 1 0 l 0 1 l -1 0 Z
    '''
    tick = 0
    offset = point(0, 0)
    scale = point(1, -2)
    scaleFirst = True
    curveCount = 7
    curveInterval = 0
    curveUseInterval = False
    autoCurveCount = False
    writeToFile = False
    outputPath = ''
    __main(
            svgRaw,
            tick,
            scale,
            scaleFirst,
            curveCount,
            curveInterval,
            curveUseInterval,
            autoCurveCount,
            writeToFile,
            outputPath
        )