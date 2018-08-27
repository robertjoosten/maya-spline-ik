from __future__ import absolute_import
from math import *
from maya import OpenMaya


def remap(value, oldMin, oldMax, newMin, newMax):
    """
    Remap a value based on input and output minimin and maximum.

    :param float value: Value to remap
    :param float oldMin: Original minimum
    :param float oldMax: Original maximum
    :param float newMin: New minimum
    :param float newMax: New maximum
    :return: remapped value
    :rtype: float
    """
    return (((value - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) + newMin


def remapWeighting(values1, values2):
    """
    Get a weighting list how to blend values1 and values2, this math
    function is usefull to get the parenting weights, between lists with
    different parameters.

    :param list values1:
    :param list values2:
    :return: list of dictionaries with blend weighting values
    :rtype: list
    """
    tWeighting = []
    for j, tP in enumerate(values1):
        for i, mP in enumerate(values2):
            if tP == mP:
                tWeighting.append({i: 1})
                continue

            # handle lists that dont start with 0 ( closed curves )
            if mP == 0:
                mP = 1

            pP = values2[i - 1]
            if pP < tP < mP:
                weight = remap(tP, pP, mP, 0, 1)
                tWeighting.append({i - 1: 1 - weight, i: weight})
                continue

    return tWeighting


# ----------------------------------------------------------------------------


def convertAxisToVector(axis):
    """
    Convert an axis to a normalized vector.

    :param str axis: options are x, y, z.
    :return: vector
    :rtype: list
    """
    return [1 if a == axis.lower() else 0 for a in ["x", "y", "z"]]


# ----------------------------------------------------------------------------


def lookRotation(forward, up):
    """
    Get a quaternion based on the forward and up vector, this util can
    be used to easilty get rotational values to input into the rotation
    of a node, based on just two vectors.

    :param list/OpenMaya.MVector forward:
    :param list/OpenMaya.MVector up:
    :return: Quaternion with the orientation of the 2 vectors.
    :rtype: OpenMaya.MQuaternion
    """
    # variable
    _next = [1, 2, 0]

    # to api
    if not type(forward) == OpenMaya.MVector:
        forward = OpenMaya.MVector(*forward)
    if not type(up) == OpenMaya.MVector:
        up = OpenMaya.MVector(*up)

    # get 3 axis
    right = up ^ forward
    up = forward ^ right
    right = up ^ forward

    # normalize
    forward.normalize()
    up.normalize()
    right.normalize()

    # get t
    t = right.x + up.y + forward.z

    if t > 0:
        t = t + 1
        s = 0.5 / sqrt(t)
        w = s * t
        x = (up.z - forward.y) * s
        y = (forward.x - right.z) * s
        z = (right.y - up.x) * s

        q = OpenMaya.MQuaternion(x, y, z, w)
        q.normalizeIt()
        return q
    else:
        rot = [
            [right.x, up.x, forward.x],
            [right.y, up.y, forward.y],
            [right.z, up.z, forward.z],
        ]

        q = [0, 0, 0]
        i = 0

        if up.y > right.x:
            i = 1

        if forward.z > rot[i][i]:
            i = 2

        j = _next[i]
        k = _next[j]

        t = rot[i][i] - rot[j][j] - rot[k][k] + 1
        s = 0.5 / sqrt(t)
        q[i] = s * t
        w = (rot[k][j] - rot[j][k]) * s
        q[j] = (rot[j][i] + rot[i][j]) * s
        q[k] = (rot[k][i] + rot[i][k]) * s

        q = OpenMaya.MQuaternion(q[0], q[1], q[2], w)
        q.normalizeIt()
        return q
