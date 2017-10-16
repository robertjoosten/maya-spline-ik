"""			
Create a Spline IK from any curve in Maya.

Installation
============
Copy the **rjSplineIK** folder to your Maya scripts directory
::
    C:/Users/<USER>/Documents/maya/scripts

Usage
=====
Command line
::
    from rjSplineIK import SplineIK
    
    splineIK = SplineIK()
    splineIK.create(
        name,
        curve,
        numJoints,
        upDirection="y", 
        worldUpDirection="y", 
        forwardDirection="x"
    )

Display UI
::
    import rjSplineIK.ui
    rjSplineIK.ui.show()    

Note
====
The Spline IK module works on a curve and generates an joint chain that 
sticks to it's position on the curve. This means that stretch and squash will
only occur in the areas that manipulates as opposed to it scaling as a whole.

The other benefit of using this module over a regular spline IK is the fact 
that the twist is divided over the controls that are generated and not just 
limited to the beginning and end.
        
The Spline IK class is flexible for creation, before the create function
is called some other attributes can be changed as well.

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

Code
====
"""

from .create import SplineIK

__author__ = "Robert Joosten"
__version__ = "0.7.0"
__email__ = "rwm.joosten@gmail.com"