from maya import cmds
from . import controlShape, curve, colour


def createControlShape(name, shape, colour_, num=None):
    """ 
    Create a control with offset group.

    :param str name: Name of the control ( _ctrl will be appended )
    :param str shape: Shape of the control.
    :param str colour_: Colour of the control.
    :param int num: Number of control ( padding of 3 ).
    :return: name of offset and control
    :rtype: tuple
    """
    # handle number
    numSuffix = "_{0:03d}".format(num) if num != None else ""

    # get names
    ctrlName = "{0}_ctrl{1}".format(name, numSuffix)
    offsetName = "{0}_ctrl_offset{1}".format(name, numSuffix)

    # validate ctrl name
    if cmds.objExists(ctrlName):
        raise ValueError("createControlShape: name already exists!")

    # get shape position
    shapePoints = controlShape.getControlShape(shape)

    # create
    ctrl, shapes = curve.createCurveShape(ctrlName, shapePoints)
    offset = cmds.group(w=True, em=True, n=offsetName)

    # set colour
    colourString = colour.getColourFromString(colour_)
    for s in shapes:
        cmds.setAttr("{0}.overrideEnabled".format(s), 1)
        cmds.setAttr("{0}.overrideColor".format(s), colourString)
        
    # parent ctrl to offset
    ctrl = cmds.parent(ctrl, offset)[0]

    return offset, ctrl
