from maya import cmds

from rigging.utils import attribute

def attachToMotionPath(
        curve,
        target,
        name=None,
        bank=False,
        bankScale=1.0,
        bankThreshold=90.0,
        follow=False,
        followAxis="Y",
        fractionMode=False,
        inverseFront=False,
        inverseUp=False,
        upAxis="Z",
        worldUpObject=None,
        worldUpType="vector",
        worldUpVector=[0.0, 1.0, 0.0],
    ):
    """
    Attach to motion path util, that will create a clean setup by creating 
    the motion path node from scratch and connecting all of the attributes. 
    
    :param str curve:
    :param str target:
    :param str/None name:
    :param bool bank:
    :param float bankScale:
    :param float bankThreshold:
    :param bool follow:
    :param str followAxis:
    :param bool fractionMode:
    :param bool inverseFront:
    :param bool inverseUp:
    :param str upAxis:
    :param str/None worldUpObject:
    :param str worldUpType:
    :param list worldUpVector:
    :return: motion path node
    :rtype: str
    """
    # generate name
    if not name:
        name = "{0}_mp_001".format(curve)

    # create
    mp = cmds.createNode("motionPath", n=name)
    
    # create mappers
    forwardMapper = attribute.enumStringToValue("{0}.frontAxis".format(mp))
    upMapper = attribute.enumStringToValue("{0}.upAxis".format(mp))
    worldMapper = attribute.enumStringToValue("{0}.worldUpType".format(mp))

    # set bank
    cmds.setAttr("{0}.bank".format(mp), bank)
    cmds.setAttr("{0}.bankScale".format(mp), bankScale)
    cmds.setAttr("{0}.bankLimit".format(mp), bankThreshold)

    # set follow
    cmds.setAttr("{0}.follow".format(mp), follow)
    
    cmds.setAttr("{0}.frontAxis".format(mp), forwardMapper.get(followAxis))

    # set fraction
    cmds.setAttr("{0}.fractionMode".format(mp), fractionMode)

    # set inverse
    cmds.setAttr("{0}.inverseFront".format(mp), inverseFront)
    cmds.setAttr("{0}.inverseUp".format(mp), inverseUp)

    # set up
    cmds.setAttr("{0}.upAxis".format(mp), upMapper.get(upAxis))
    cmds.setAttr("{0}.worldUpType".format(mp), worldMapper.get(worldUpType))
    cmds.setAttr("{0}.worldUpVector".format(mp), *worldUpVector)

    # connect to motion path
    cmds.connectAttr(
        "{0}.worldSpace[0]".format(curve), 
        "{0}.geometryPath".format(mp)
    )
    
    if worldUpObject:
        cmds.connectAttr(
            "{0}.worldMatrix[0]".format(worldUpObject), 
            "{0}.worldUpMatrix".format(mp)
        )

    # connect to target
    cmds.setAttr("{0}.inheritsTransform".format(target), 0)
    cmds.connectAttr(
        "{0}.allCoordinates".format(mp), 
        "{0}.translate".format(target)
    )
    cmds.connectAttr(
        "{0}.rotate".format(mp), 
        "{0}.rotate".format(target)
    )
    cmds.connectAttr(
        "{0}.rotateOrder".format(mp), 
        "{0}.rotateOrder".format(target)
    )

    return mp