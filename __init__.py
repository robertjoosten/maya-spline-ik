"""			
Create a Spline IK setup on a curve. The setup features variable stretch and 
squash, variable rotation and sliding on curve.

.. figure:: https://github.com/robertjoosten/rjSplineIK/raw/master/data/header.png
   :align: center

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

.. figure:: https://github.com/robertjoosten/rjSplineIK/raw/master/data/ui.png
   :align: center
   
::
    import rjSplineIK.ui
    rjSplineIK.ui.show()    

Note
====
The Spline IK module works on a curve and generates an joint chain that 
sticks to it's position on the curve. This means that stretch and squash will
only occur in the areas that manipulates as opposed to it scaling as a whole.

.. figure:: https://github.com/robertjoosten/rjSplineIK/raw/master/data/stretchSquash.gif
   :align: center
   
   Stretch and Squash demo
   
The other benefit of using this module over a regular spline IK is the fact 
that the twist is divided over the controls that are generated and not just 
limited to the beginning and end.

.. figure:: https://github.com/robertjoosten/rjSplineIK/raw/master/data/partialTwist.gif
   :align: center
   
   Partial Twist demo

.. figure:: https://github.com/robertjoosten/rjSplineIK/raw/master/data/shift.gif
   :align: center
   
   Shift demo
      
Apart from the main settings, the control colour, position and orientation is 
adjustable. This can be done on the Spline IK class before the create function
is called.

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
"""

from .create import SplineIK

__author__  = "Robert Joosten"
__version__ = "0.7.0"
__email__   = "rwm.joosten@gmail.com"