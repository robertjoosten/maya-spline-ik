from maya import cmds, mel, OpenMaya
from . import api, math


def numCVs(curve):
    """
    Get the number of CVs of a curve.

    :param curve:
    :return: number of cvs
    :rtype: int
    """
    return cmds.getAttr("{0}.cp".format(curve), s=1)


# ----------------------------------------------------------------------------


def parameterLength(curve):
    """
    Return the parameter length of a curve.

    :param str curve:
    :return: parameter length or curve
    :rtype: float
    """
    mFnCurve = api.asMFnNurbsCurve(curve)
    return mFnCurve.findParamFromLength(mFnCurve.length())


# ----------------------------------------------------------------------------


def createCurveShape(name, points):
    """ 
    Create a curve and rename the shapes to be unique.

    :param str name: Name of curve
    :param list points: List of points.
    """
    # create curve
    curve = cmds.curve(p=points, d=1, n=name)

    # rename shapes
    shapes = []
    for shape in cmds.listRelatives(curve, s=True, f=True) or []:
        shape = cmds.rename(shape, "{0}Shape".format(name))
        shapes.append(shape)

    return curve, shapes


def convertToBezierCurve(curve):
    """
    Check if the parsed curve is a bezier curve, if this is not the case
    convert the curve to a bezier curve.
    
    :param str curve: Name of curve
    """
    # get shape
    curveShape = cmds.listRelatives(curve, s=True)[0]

    # convert to bezier curve
    if cmds.nodeType(curveShape) == "bezierCurve":
        return
        
    cmds.select(curve)
    cmds.nurbsCurveToBezier()


# ----------------------------------------------------------------------------


def nearestPointOnCurve(curve, pos):
    """
    Find the nearest point on a curve, the function will return
    the parameter and point. The point is of type OpenMaya.MPoint.
    
    :param str curve:
    :param list pos:
    :return: parameter, point
    :rtype: float, OpenMaya.MPoint
    """
    mFnCurve = api.asMFnNurbsCurve(curve)

    pUtil = OpenMaya.MScriptUtil()
    pPtr = pUtil.asDoublePtr()

    point = mFnCurve.closestPoint(
        OpenMaya.MPoint(*pos),
        pPtr,
        0.001,
        OpenMaya.MSpace.kWorld
    )

    return pUtil.getDouble(pPtr), point


# ----------------------------------------------------------------------------


def splitCurveToParametersByLength(curve, num):
    """
    Get a list of parameters evenly spaced along a curve, based on the
    length of the curve. Ranges are normalizes to be between 0-1.

    :param str curve:
    :param int num:

    :return: parameters
    :rtype: list
    """
    mFnCurve = api.asMFnNurbsCurve(curve)
    increment = 1.0 / (num - 1)

    # get parameters
    parameters = []
    for i in range(num):
        parameter = mFnCurve.findParamFromLength(
            mFnCurve.length() * increment * i
        )
        parameters.append(parameter)

    # normalize
    factor = parameters[-1]
    parameters = [p/factor for p in parameters]

    if cmds.getAttr("{0}.form".format(curve)) == 2:
        parameters.insert(0, parameters[-1])
        parameters.pop(-1)

    return parameters


def splitCurveToParametersByParameter(curve, num):
    """
    Get a list of parameters evenly spaced along a curve, based on the
    division of its parameters. Ranges are normalizes to be between 0-1.

    :param str curve:
    :param int num:

    :return: parameters
    :rtype: list
    """
    increment = 1.0 / (num - 1)
    parameters = [i * increment for i in range(num)]

    if cmds.getAttr("{0}.form".format(curve)) == 2:
        parameters.insert(0, parameters[-1])
        parameters.pop(-1)

    return parameters


# ----------------------------------------------------------------------------


def createFollicle(
        name,
        curve,
        parameter,
        forwardDirection="z",
        upDirection="y",
        overrideNormal=None,
        subtractPositionFromNormal=False
    ):
    """
    Create a follicle on a curve. The name will be used for the
    creation of all of the nodes. The overrideNormal attribute can be
    used if the up vector needs to be any different then what the
    curve can provide, this can be the translation attribute of a
    transform. The subtractPositionFromNormal can be used of the
    normal parsed is in world space, this means that the normal will
    be converted to local space.

    :param str name:
    :param str curve: curve to attach follicle too
    :param float parameter: parameter on curve between 0-1
    :param str forwardDirection: ("x", "y", "z"), default "z"
    :param str upDirection: ("x", "y", "z"), default "y"
    :param str overrideNormal: override normal connection, (eg. translate)
    :param bool subtractPositionFromNormal: subtract the position from the normal
    :return: locator, pointOnCurve, aimConstraint
    :rtype: tuple
    """
    # catch numbered naming
    suffix = ""
    sections = name.rsplit("_", 1)
    if sections[-1].isdigit():
        name = sections[0]
        suffix = "_{0}".format(sections[-1])

    # create follicle
    loc = cmds.spaceLocator(n="{0}_loc{1}".format(name, suffix))[0]
    cmds.setAttr("{0}.inheritsTransform".format(loc), 0)
    cmds.setAttr("{0}.localScale".format(loc), 0.1, 0.1, 0.1)

    # create point on curve node
    poc = cmds.createNode(
        "pointOnCurveInfo",
        n="{0}_poc{1}".format(name, suffix)
    )
    
    # connect to curve
    cmds.setAttr("{0}.parameter".format(poc), parameter)
    cmds.setAttr("{0}.turnOnPercentage".format(poc), 1)
    cmds.connectAttr(
        "{0}.worldSpace".format(curve),
        "{0}.inputCurve".format(poc)
    )

    # catch override normal
    normalAttribute = "{0}.normalizedNormal".format(poc)
    if overrideNormal:
        normalAttribute = overrideNormal

    # catch subtract position from normal
    if subtractPositionFromNormal:
        pma = cmds.createNode(
            "plusMinusAverage",
            n="{0}_pma{1}".format(name, suffix)
        )

        cmds.setAttr("{0}.operation".format(pma), 2)
        cmds.connectAttr(
            normalAttribute, 
            "{0}.input3D[0]".format(pma)
        )
        cmds.connectAttr(
            "{0}.result.position".format(poc),
            "{0}.input3D[1]".format(pma)
        )

        normalAttribute = "{0}.output3D".format(pma)

    # create vectors
    forwardVector = math.convertAxisToVector(forwardDirection)
    upVector = math.convertAxisToVector(upDirection)

    # create aim constraint
    aim = cmds.createNode(
        "aimConstraint",
        n="{0}_aim{1}".format(name, suffix)
    )
    cmds.parent(aim, loc)

    # set aim constraint
    cmds.setAttr("{0}.tg[0].tw".format(aim), 1)
    cmds.setAttr("{0}.worldUpType".format(aim), 3)
    cmds.setAttr("{0}.aimVector".format(aim), *forwardVector)
    cmds.setAttr("{0}.upVector".format(aim), *upVector)
    
    cmds.connectAttr(
        "{0}.tangent".format(poc), 
        "{0}.tg[0].tt".format(aim)
    )
    cmds.connectAttr(
        normalAttribute, 
        "{0}.worldUpVector".format(aim)
    )

    # connect to locator
    cmds.connectAttr(
        "{0}.result.position".format(poc),
        "{0}.translate".format(loc)
    )
    cmds.connectAttr(
        "{0}.constraintRotate".format(aim), 
        "{0}.rotate".format(loc)
    )

    return loc, poc, aim
