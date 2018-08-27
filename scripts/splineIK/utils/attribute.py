from maya import cmds


def addAttr(node, attr, **kwargs):
    """
    Add a attribute to a node, it check if the attribute exists and if it 
    does not, then attempt to add the attribute.

    :param str node: 
    :param str attr:
    """
    if cmds.objExists("{0}.{1}".format(node, attr)):
        return

    cmds.addAttr(node, shortName=attr, longName=attr, k=True, **kwargs)


def addSpacerAttr(node, attr="controls"):
    """
    Add a spacer attribute to a node, by default the attribute is called 
    "controls".

    :param str node:
    :param str attr:
    """
    path = "{0}.{1}".format(node, attr)
    if cmds.objExists(path):
        return

    # add attr
    cmds.addAttr(
        node,
        shortName=attr,
        longName=attr,
        at="enum",
        enumName="#",
        k=True
    )

    # lock attr
    cmds.setAttr(path, lock=True)


# ----------------------------------------------------------------------------


def enumStringToValue(attr, lowercase=False):
    """
    Creates a dictionary mapper for enum values. This util can be used
    to set enum attributes with string values.

    :param str attr:
    :param bool lowercase: 
    :return: enumStringToValue
    :rtype: dict
    """
    node, attr = tuple(attr.split(".", 1))

    enumString = cmds.attributeQuery(attr, node=node, listEnum=True)[0]
    enumDict = {}

    for i, str in enumerate(enumString.split(":")):
        if lowercase:
            str = str.lower()

        enumDict[str] = i

    return enumDict
