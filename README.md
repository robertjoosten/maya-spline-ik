# maya-spline-ik
<p align="center"><img src="icons/SIK_icon.png?raw=true"></p>
Create a Spline IK setup on a curve. The setup features variable stretch and squash, variable rotation and sliding on curve.

<p align="center"><img src="docs/_images/SIK_header.png?raw=true"></p>

## Installation
* Extract the content of the .rar file anywhere on disk.
* Drag the splineIK.mel file in Maya to permanently install the script.

## Usage
A button on the MiscTools shelf will be created that will allow easy access to the ui, this way the user doesn't need to worry about any of the code.
If user wishes to not use the shelf button the following commands can be used.

Command line:
```python
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
```

Display UI:

```python
import rjSplineIK.ui
rjSplineIK.ui.show()  
```

<p align="center"><img src="docs/_images/SIK_uiExample.png?raw=true"></p>
<p align="center"><b>UI example</b></p>

## Note
The Spline IK module works on a curve and generates an joint chain that sticks to it's position on the curve. This means that stretch and squash will only occur in the areas that manipulates as opposed to it scaling as a whole.
     
<p align="center"><img src="docs/_images/SIK_stretchSquashExample.png?raw=true"></p>
<p align="center"><b>Stretch and Squash demo</b></p>

The other benefit of using this module over a regular spline IK is the fact that the twist is divided over the controls that are generated and not just limited to the beginning and end.
 
<p align="center"><img src="docs/_images/SIK_partialTwistExample.png?raw=true"></p>
<p align="center"><b>Partial Twist demo</b></p>

<p align="center"><img src="docs/_images/SIK_shiftExample.png?raw=true"></p>
<p align="center"><b>Shift demo</b></p>
  
Apart from the main settings, the control colour, position and orientation is adjustable. This can be done on the Spline IK class before the create function is called.

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
