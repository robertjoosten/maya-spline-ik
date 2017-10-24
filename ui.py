import os
from maya import OpenMaya, OpenMayaUI, cmds

# import pyside, do qt version check for maya 2017 >
qtVersion = cmds.about(qtVersion=True)
if qtVersion.startswith("4") or type(qtVersion) not in [str, unicode]:
    from PySide.QtGui import *
    from PySide.QtCore import *
    import shiboken
else:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    import shiboken2 as shiboken

from .create import SplineIK

from .utils.controlShape import CONTROL_SHAPES
from .utils.colour import COLOURS_FROM_STRING

# ----------------------------------------------------------------------------

FONT = QFont()
FONT.setFamily("Consolas")

BOLT_FONT = QFont()
BOLT_FONT.setFamily("Consolas")
BOLT_FONT.setWeight(100)  

# ----------------------------------------------------------------------------

def mayaWindow():
    """
    Get Maya's main window.
    
    :rtype: QMainWindow
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = shiboken.wrapInstance(long(window), QMainWindow)
    
    return window  
    
# ----------------------------------------------------------------------------
    
def divider(parent):
    """
    Create divider ui widget.
    
    :param QWidget parent:
    :rtype: QFrame
    """
    line = QFrame(parent)
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line
    
# ----------------------------------------------------------------------------
    
def findIcon(icon):
    """
    Loop over all icon paths registered in the XBMLANGPATH environment 
    variable ( appending the tools icon path to that list ). If the 
    icon exist a full path will be returned.

    :param str icon: icon name including extention
    :return: icon path
    :rtype: str or None
    """
    paths = []

    # get maya icon paths
    if os.environ.get("XBMLANGPATH"):     
        paths = os.environ.get("XBMLANGPATH").split(os.pathsep)                                 

    # append tool icon path
    paths.insert(
        0,
        os.path.join(
            os.path.split(__file__)[0], 
            "icons" 
        ) 
    )

    # loop all potential paths
    for path in paths:
        filepath = os.path.join(path, icon)
        if os.path.exists(filepath):
            return filepath
    
# ----------------------------------------------------------------------------

class LabelWidget(QWidget):
    def __init__(self, parent, label, widget):
        QWidget.__init__(self, parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        # create label
        self.label = QLabel(self)
        self.label.setText(label)
        self.label.setFont(FONT)
        layout.addWidget(self.label)
        
        # create line edit
        self.widget = widget(self)
        self.widget.setFont(FONT)
        layout.addWidget(self.widget)

class InputWidget(LabelWidget):
    def __init__(self, parent, label):
        LabelWidget.__init__(self, parent, label, QLineEdit)
  
    def text(self):
        return self.widget.text()
        
class ComboBoxWidget(LabelWidget):
    def __init__(self, parent, label, items, defaultItem=None):
        LabelWidget.__init__(self, parent, label, QComboBox)
        
        # add items
        self.widget.addItems(items)
        
        # set default
        index = items.index(defaultItem)
        self.widget.setCurrentIndex(index)
  
    def currentText(self):
        return self.widget.currentText()
        
class SpinBoxWidget(LabelWidget):
    def __init__(self, parent, label, defaultValue, minValue, maxValue):
        LabelWidget.__init__(self, parent, label, QSpinBox)
        self.widget.setMinimum(minValue)
        self.widget.setMaximum(maxValue)
        self.widget.setValue(defaultValue)
  
    def value(self):
        return self.widget.value()
        
# ----------------------------------------------------------------------------

class SelectWidget(QWidget):
    released = Signal()
    def __init__(self, parent, label, button):
        QWidget.__init__(self, parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        # create label
        self.label = QLabel(self)
        self.label.setText(label)
        self.label.setFont(FONT)
        self.label.setFixedWidth(75)
        layout.addWidget(self.label)
        
        # create line edit
        self.edit = QLineEdit(self)
        self.edit.setFont(FONT)
        layout.addWidget(self.edit)
        
        # create label
        self.button = QPushButton(self)
        self.button.setText(button)
        self.button.setFont(FONT)
        self.button.setFixedWidth(100)
        self.button.released.connect(self.released.emit)
        layout.addWidget(self.button)
        
    # ------------------------------------------------------------------------
        
    def setText(self, text):
        self.edit.setText(text)
        
    def text(self):
        return self.edit.text()
        
# ----------------------------------------------------------------------------

class ControlWidget(QWidget):
    def __init__(self, parent, label, defaultShape, defaultColour):
        QWidget.__init__(self, parent)

        # variables
        shapes = CONTROL_SHAPES.keys()
        shapes.sort()
        
        colours = COLOURS_FROM_STRING.keys()
        colours.sort()
        
        # create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # create label
        self.label = QLabel(self)
        self.label.setText(label)
        self.label.setFont(FONT)
        layout.addWidget(self.label)

        # create shape
        self.shape = ComboBoxWidget(
            self,
            "Shape:", 
            shapes, 
            defaultShape
        )
        self.shape.label.setFixedWidth(50)
        layout.addWidget(self.shape)
        
        # create colour
        self.colour = ComboBoxWidget(
            self,
            "Colour:", 
            colours, 
            defaultColour
        )
        self.colour.label.setFixedWidth(50)
        layout.addWidget(self.colour)

    # ------------------------------------------------------------------------

    def getShape(self):
        return self.shape.currentText()

    def getColour(self):
        return self.colour.currentText()

# ----------------------------------------------------------------------------

class SplineIKWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        
        # set ui
        self.setParent(parent)        
        self.setWindowFlags(Qt.Window)  

        self.setWindowTitle("Spline IK")      
        self.setWindowIcon(QIcon(findIcon("rjSplineIK.png")))           
        self.resize(475, 250)
        
        # create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # create name input
        self.name = InputWidget(self, "Name")
        self.name.label.setFixedWidth(75)
        layout.addWidget(self.name)
        
        # create curve selector
        self.curve = SelectWidget(self, "Curve", "Select Curve")
        self.curve.released.connect(self.getSelection)
        layout.addWidget(self.curve)
        
        # add divider
        div = divider(self)
        layout.addWidget(div)
        
        # add num joints
        self.joint = SpinBoxWidget(self, "Num Joints", 20, 3, 500)
        layout.addWidget(self.joint)
        
        # add divider
        div = divider(self)
        layout.addWidget(div)
        
        # create vectors
        axis = ["x", "y", "z"]
        
        self.forward = ComboBoxWidget(self, "Forward Axis", axis, "x")
        layout.addWidget(self.forward)
        
        self.up = ComboBoxWidget(self, "Up Axis", axis, "y")
        layout.addWidget(self.up)
        
        self.worldUp = ComboBoxWidget(self, "World Up Axis", axis, "y")
        layout.addWidget(self.worldUp)

        # add divider
        div = divider(self)
        layout.addWidget(div)
        
        self.root = ControlWidget(self, "Root Control", "triangle", "light blue")
        layout.addWidget(self.root)
        
        self.slide = ControlWidget(self, "Slide Control", "sphere", "red")
        layout.addWidget(self.slide)
        
        self.tweak = ControlWidget(self, "Tweak Control", "sphere", "yellow")
        layout.addWidget(self.tweak)
        
        self.tangent = ControlWidget(self, "Tangent Control", "cube", "white")
        layout.addWidget(self.tangent)
        
        # add divider
        div = divider(self)
        layout.addWidget(div)
        
        # create orient
        option = ["Yes", "No"]
        self.orientRoot = ComboBoxWidget(self, "Orient Root to Curve", option, "No")
        layout.addWidget(self.orientRoot)
        
        self.orient = ComboBoxWidget(self, "Orient to Curve", option, "Yes")
        layout.addWidget(self.orient)
        
        # add divider
        div = divider(self)
        layout.addWidget(div)
        
        # create button
        create = QPushButton(self)
        create.pressed.connect(self.doCreate)
        create.setText("Create")
        create.setFont(FONT)
        layout.addWidget(create)
        
    # ------------------------------------------------------------------------    
        
    def getSelection(self):
        """
        Get the current selection and see if the shapes of the first instance
        of the selection are of type 'nurbsCurve' or 'bezierCurve', if the
        criteria are met the line edit of the curve selection widget is 
        updated. If the criteria are not met a ValueError will be raised.
        
        :raises ValueError: if the selection criteria are not met.
        """
        # get selection
        selection = cmds.ls(sl=True)
        if not selection:
            raise ValueError("No selection found!")
         
        # check shapes ( exist )
        shapes = cmds.listRelatives(selection[0], s=True) or []
        if not shapes:
            raise ValueError("No shapes found in selection!")
        
        # check shapes
        for shape in shapes:
            if cmds.nodeType(shape) not in ["nurbsCurve", "bezierCurve"]:
                raise ValueError(
                    "Shapes are not of type 'nurbsCurve' or 'bezierCurve'!"
                )

        # set text
        self.curve.setText(selection[0])
        
    # ------------------------------------------------------------------------
        
    def doCreate(self):
        """
        Read the values of the ui and create a spline ik, if the creation is 
        succesfull the root control of the setup will be created. A ValueError
        will be raised if the input field is empty or no curve is selected.
        
        :raises ValueError: if the input or curve field are empty
        """
        # validate name
        name = self.name.text()
        if not name:
            raise ValueError("No name specified!")

        # validate curve
        curve = self.curve.text()
        if not curve:
            raise ValueError("No curve specified!")

        # create spline ik object
        ik = SplineIK()

        # set control shape and colour
        ik.rootControlShape = self.root.getShape()
        ik.rootControlColour = self.root.getColour()
        ik.slideControlShape = self.slide.getShape()
        ik.slideControlColour = self.slide.getColour()
        ik.controlShape = self.tweak.getShape()
        ik.controlColour = self.tweak.getColour()
        ik.tangentControlShape = self.tangent.getShape()
        ik.tangentControlColour = self.tangent.getColour()
        
        # set orientation
        orient = True if self.orientRoot.currentText() == "Yes" else False
        ik.orientRootToCurve = orient
        
        orient = True if self.orient.currentText() == "Yes" else False
        ik.orientToCurve = orient

        # create spline ik
        control = ik.create(
            name,
            curve,
            self.joint.value(),
            forwardDirection=self.forward.currentText(),
            upDirection=self.up.currentText(),
            worldUpDirection=self.worldUp.currentText(),
        )
        
        # select root
        cmds.select(control)

def show():
    dialog = SplineIKWidget(mayaWindow())
    dialog.show()