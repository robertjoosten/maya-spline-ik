# rjSplineIK
<img align="right" src="https://github.com/robertjoosten/rjSplineIK/raw/master/icon/rjSplineIK.png">
Create a Spline IK setup on a curve. The setup features variable stretch and squash, variable rotation and sliding on curve.

<p align="center"><img src="https://github.com/robertjoosten/rjSplineIK/raw/master/data/header.png"></p>

## Installation
Copy the **rjSplineIK** folder to your Maya scripts directory:
> C:\Users\<USER>\Documents\maya\scripts

## Usage
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

<p align="center"><img src="https://github.com/robertjoosten/rjSplineIK/raw/master/data/ui.png"></p>
<p align="center"><b>UI example</b></p>

```python
import rjSplineIK.ui
rjSplineIK.ui.show()  
```

## Note
The Spline IK module works on a curve and generates an joint chain that sticks to it's position on the curve. This means that stretch and squash will only occur in the areas that manipulates as opposed to it scaling as a whole.
     
<p align="center"><img src="https://github.com/robertjoosten/rjSplineIK/raw/master/data/stretchSquash.gif"></p>
<p align="center"><b>Stretch and Squash demo</b></p>

The other benefit of using this module over a regular spline IK is the fact that the twist is divided over the controls that are generated and not just limited to the beginning and end.
 
<p align="center"><img src="https://github.com/robertjoosten/rjSplineIK/raw/master/data/partialTwist.gif"></p>
<p align="center"><b>Partial Twist demo</b></p>

<p align="center"><img src="https://github.com/robertjoosten/rjSplineIK/raw/master/data/shift.gif"></p>
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
