class Settings(object):
    """
    The Spline IK module is flexible for creation, this class holds all
    of the attributes the user is allowed to change before creation.

    * controlShape
    * rootControlShape
    * slideControlShape
    * tangentControlShape

    * controlColour
    * rootControlColour
    * slideControlColour
    * tangentControlColour

    * orientToCurve
    * orientRootToCurve

    Available shapes and colours can be found in the following module.
    :mod:`rjSplineIK.utils.controlShape`
    :mod:`rjSplineIK.utils.colour`
    """
    def __init__(self):
        # default control variables
        self._controlShape = "circle"
        self._controlColour = "yellow"
        self._tangentControlShape = "cube"
        self._tangentControlColour = "white"
        self._rootControlShape = "triangle"
        self._rootControlColour = "red"
        self._slideControlShape = "sphere"
        self._slideControlColour = "red"

        # default orient variables
        self._orientToCurve = True
        self._orientRootToCurve = False

    # --------------------------------------------------------------------

    def getRootControlShape(self):
        return self._rootControlShape

    def setRootControlShape(self, shape):
        self._rootControlShape = shape

    def getRootControlColour(self):
        return self._rootControlColour

    def setRootControlColour(self, colour):
        self._rootControlColour = colour

    rootControlShape = property(getRootControlShape, setRootControlShape)
    rootControlColour = property(getRootControlColour, setRootControlColour)

    # --------------------------------------------------------------------

    def getControlShape(self):
        return self._controlShape

    def setControlShape(self, shape):
        self._controlShape = shape

    def getControlColour(self):
        return self._controlColour

    def setControlColour(self, colour):
        self._controlColour = colour

    controlShape = property(getControlShape, setControlShape)
    controlColour = property(getControlColour, setControlColour)

    # --------------------------------------------------------------------

    def getTangentControlShape(self):
        return self._tangentControlShape

    def setTangentControlShape(self, shape):
        self._tangentControlShape = shape

    def getTangentControlColour(self):
        return self._tangentControlColour

    def setTangentControlColour(self, colour):
        self._tangentControlColour = colour

    tangentControlShape = property(getTangentControlShape, setTangentControlShape)
    tangentControlColour = property(getTangentControlColour, setTangentControlColour)

    # --------------------------------------------------------------------

    def getSlideControlShape(self):
        return self._slideControlShape

    def setSlideControlShape(self, shape):
        self._slideControlShape = shape

    def getSlideControlColour(self):
        return self._slideControlColour

    def setSlideControlColour(self, colour):
        self._slideControlColour = colour

    slideControlShape = property(getSlideControlShape, setSlideControlShape)
    slideControlColour = property(getSlideControlColour, setSlideControlColour)

    # --------------------------------------------------------------------

    @property
    def orientRootToCurve(self):
        return self._orientRootToCurve

    @orientRootToCurve.setter
    def orientRootToCurve(self, value):
        self._orientRootToCurve = value

    @property
    def orientToCurve(self):
        return self._orientToCurve

    @orientToCurve.setter
    def orientToCurve(self, value):
        self._orientToCurve = value