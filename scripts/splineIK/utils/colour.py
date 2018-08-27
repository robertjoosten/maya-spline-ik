COLOURS_FROM_STRING = {
    "black":       1,    "grey":          2,
    "light grey":  3,    "dark red":      4,
    "dark blue":   5,    "blue":          6,
    "dark green":  7,    "dark purple":   8,
    "hot pink":    9,    "brown":         10,
    "dark brown":  11,   "apple":         12,
    "red":         13,   "green":         14,
    "cobalt":      15,   "white":         16,
    "yellow":      17,   "light blue":    18,
    "artic":       19,   "pink":          20,
    "orange":      21,   "light yellow":  22,
    "fern":        23,   "dark orange":   24,
    "dark yellow": 25,   "pear":          26,
    "parakeet":    27,   "sky":           29,
    "lapis":       30,   "purple":        31,
}

COLOURS_FROM_INT = {
    v: k for k, v in COLOURS_FROM_STRING.iteritems()
}


def getColourFromString(colour):
    """ 
    Takes a string of a colour and returns mayas number setting for nurbs 
    colour changes.

    :param str colour:
    :raises ValueError: When the colour cannot be converted to an integer
    """
    colourFiltered = colour.lower().replace("_"," ")
    colourInt = COLOURS_FROM_STRING.get(colourFiltered)
    
    if not colourInt:
        raise ValueError(
            "getColourFromString: {0} couldn't be converted to a atring!".format(
                colour
            )
        )
        
    return colourInt


def getColourFromInt(colour):
    """ 
    Takes a integer and convert it into a the string name of that colour.

    :param int colour: The controllers colour to get.
    :raises ValueError: When the colour cannot be converted to an string
    """
    colourString = COLOURS_FROM_INT.get(colour)
    
    if not colourString:
        raise ValueError(
            "getColourFromInt: {0} couldn't be converted to a atring!".format(
                colour
            )
        )

    return colourString
