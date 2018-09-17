"""			
Create a Spline IK setup on a curve. The setup features variable stretch and 
squash, variable rotation and sliding on curve.

.. figure:: /_images/SIK_header.png
   :align: center

Installation
============
* Extract the content of the .rar file anywhere on disk.
* Drag the splineIK.mel file in Maya to permanently install the script.

Usage
=====
A button on the MiscTools shelf will be created that will allow easy access
to the ui, this way the user doesn't need to worry about any of the code. If
user wishes to not use the shelf button the following commands can be used.

Command line:
::
    from splineIK import SplineIK
    
    sik = SplineIK()
    sik.create(
        name,
        curve,
        numJoints,
        upDirection="y", 
        worldUpDirection="y", 
        forwardDirection="x"
    )

Display UI:
::
    import splineIK.ui
    splineIK.ui.show()

.. figure:: /_images/SIK_uiExample.png
   :align: center
   
   UI example

Note
====
The Spline IK module works on a curve and generates an joint chain that 
sticks to it's position on the curve. This means that stretch and squash will
only occur in the areas that manipulates as opposed to it scaling as a whole.

.. figure:: /_images/SIK_stretchSquashExample.gif
   :align: center
   
   Stretch and Squash demo
   
The other benefit of using this module over a regular spline IK is the fact 
that the twist is divided over the controls that are generated and not just 
limited to the beginning and end.

.. figure:: /_images/SIK_partialTwistExample.gif
   :align: center
   
   Partial Twist demo

.. figure:: /_images/SIK_shiftExample.gif
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
