from maya import cmds, OpenMaya

from .utils import (
    attribute,
    curve, 
    cluster, 
    undo, 
    math, 
    colour, 
    control, 
    controlShape,
    motionPath
)

from .settings import (
    Settings
)

MATRIX_PLUGIN = "matrixNodes.mll"

class SplineIK(Settings):
    """
    The Spline IK module works on a curve and generates an joint chain
    that sticks to it's position on the curve. This means that stretch
    and squash will only occur in the areas that manipulates as opposed
    to it scaling as a whole.

    The other benefit of using this module over a regular spline IK is
    the fact that the twist is divided over the controls that are
    generated and not just limited to the beginning and end.

    Once the class is initialized the user can change attributes that
    are defined in the :class:`rjSplineIK.settings.Settings` class that 
    gets inherited.

    Once the user parameters are set the :func:`SplineIK.create` 
    can be ran.
    """
    def __init__(self):
        Settings.__init__(self)
        
        # variables
        self._name = None
        self._curve = None
        
        # control variables
        self._controls = []
        self._rootControl = None
        self._tangentControls = None
        
        # slide control variables
        self._slideControl = None
        self._slideMinControl = None
        self._slideMaxControl = None
        
        # joints variables
        self._joints = []
        self._rootJoint = None
        
        # load matrix nodes plugin
        if not cmds.pluginInfo(MATRIX_PLUGIN, query=True, loaded=True):
            cmds.loadPlugin(MATRIX_PLUGIN)
        
    # ------------------------------------------------------------------------

    @property
    def name(self):
        """
        :return: name to use while creating the spline ik
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    # ------------------------------------------------------------------------

    @property
    def curve(self):
        """
        :return: name of the curve to attach the ik to
        :rtype: str
        """
        return self._curve

    @curve.setter
    def curve(self, curve):
        self._curve = curve

    @property
    def curveShape(self):
        """
        :return: first shape of the curve
        :rtype: str
        """
        return cmds.listRelatives(self.curve, s=True)[0]
        
    # ------------------------------------------------------------------------
        
    @property
    def rootControl(self):
        """
        :return: name of root control
        :rtype: str
        """
        return self._rootControl

    @property
    def controls(self):
        """
        :return: list of all tweak controls
        :rtype: list
        """
        return self._controls

    @property
    def tangentControls(self):
        """
        :return: list of all tangent controls
        :rtype: list
        """
        return self._tangentControls

    # --------------------------------------------------------------------

    @property
    def slideControl(self):
        """
        :return: name of slide control
        :rtype: str
        """
        return self._slideControl

    @property
    def slideMinControl(self):
        """
        :return: name of slide control ( min )
        :rtype: str
        """
        return self._slideMinControl

    @property
    def slideMaxControl(self):
        """
        :return: name of slide control ( max )
        :rtype: str
        """
        return self._slideMaxControl

    # --------------------------------------------------------------------

    @property
    def rootJoint(self):
        """
        :return: name of root joint
        :rtype: str
        """
        return self._rootJoint

    @property
    def joints(self):
        """
        :return: list of joints that are attached to the curve
        :rtype: list
        """
        return self._joints
        
    # ------------------------------------------------------------------------
    
    def __orientControl(self, offset):
        # get position
        pos = cmds.xform(offset, q=True, ws=True, t=True)

        # get closest parameter on curve
        parameter, _ = curve.nearestPointOnCurve(self.curveShape, pos)

        # get tangent
        forward = cmds.pointOnCurve(
            self.curveShape,
            pr=parameter,
            normalizedTangent=True
        )

        # get up
        forward = OpenMaya.MVector(*forward)
        up = OpenMaya.MVector(*self.upVector)

        right = up^forward
        right.normalize()

        up = right^forward
        up.normalize()

        orient = up*OpenMaya.MVector(*self.upVector)
        if orient <= 0:
            up = up * -1

        # construct quaternion
        quaternion = math.lookRotation(up, forward)

        # convert to euler
        euler = quaternion.asEulerRotation()

        rot = [
            math.degrees(euler.x),
            math.degrees(euler.y),
            math.degrees(euler.z),
        ]

        # set euler
        cmds.xform(offset, ws=True, ro=rot)
    
    def __createControl(self, cls, shape, clr, i=None, suffix=""):
        # create root control
        offset, ctrl = control.createControlShape(
            "{0}{1}".format(self.name, suffix),
            shape,
            clr,
            i
        )
        
        # position control
        pos = cluster.getClusterPosition(cls)
        cmds.setAttr("{0}.translate".format(offset), *pos)

        # parent cluster
        cmds.parent(cls, ctrl)

        return offset, ctrl
        
    # ------------------------------------------------------------------------

    def __createTangentControl(self, cls, i, side, parent):
        # create tangent control
        ctrlOffset, ctrl = self.__createControl(
            cls,
            self.tangentControlShape,
            self.tangentControlColour,
            i,
            side,
        )

        # connect vis
        cmds.connectAttr(
            "{0}.tangent_vis".format(parent),
            "{0}.visibility".format(ctrlOffset),
        )

        # create line
        name = "{0}_line".format(ctrl.replace("ctrl", "line"))
        line, _ = curve.createCurveShape(name, [(0,0,0),(0,0,0)])

        cmds.setAttr("{0}.overrideEnabled".format(line), 1)
        cmds.setAttr("{0}.overrideDisplayType".format(line), 1)
        cmds.setAttr("{0}.inheritsTransform".format(line), 0)

        cmds.parent(line, ctrl, relative=True)

        # connect line
        for i, driver in enumerate([ctrl, parent]):
            dm = cmds.createNode(
                "decomposeMatrix",
                n="{0}_line_dm_{1:03d}".format(name, i+1)
            )

            cmds.connectAttr(
                "{0}.worldMatrix".format(driver),
                "{0}.inputMatrix".format(dm)
            )
            cmds.connectAttr(
                "{0}.outputTranslate".format(dm),
                "{0}.controlPoints[{1}]".format(line, i)
            )

        return ctrlOffset, ctrl
        
    # ------------------------------------------------------------------------

    def __createControls(self):
        # create root control
        rootOffset, root = control.createControlShape(
            "{0}_root".format(self.name),
            self.rootControlShape,
            self.rootControlColour
        )

        # position root control
        pos = cluster.getClusterPosition(self.controlClusters[0])
        cmds.setAttr("{0}.translate".format(rootOffset), *pos)
        
        # orient root controls
        if self.orientRootToCurve:
            self.__orientControl(rootOffset)
        
        # create controls
        controls = []
        tangentControls = []
        
        for i, cls in enumerate(self.controlClusters):
            # before and after
            before = i*3-1
            after = i*3+1
            
            # create control
            ctrlOffset, ctrl = self.__createControl(
                cls,
                self.controlShape,
                self.controlColour,
                i,
            )
            
            # add to list
            controls.append(ctrl)
            
            # add tangent vis attribute
            attribute.addSpacerAttr(ctrl)
            attribute.addAttr(
                ctrl, 
                "tangent_vis", 
                at="long", 
                minValue=0, 
                maxValue=1
            )
            
            # orient root controls
            if self.orientToCurve:
                self.__orientControl(ctrlOffset)
                
            # create read group
            grp = cmds.group(
                world=True,
                empty=True,
                n="{0}_read_{1:03d}".format(self.name, i+1)
            )
            
            pos = cluster.getClusterPosition(cls)
            cmds.setAttr("{0}.translate".format(grp), *pos)
            
            # parent control
            cmds.parent(grp, ctrl)
            cmds.parent(ctrlOffset, root)  

            # create tangent controls
            for side, j, rot in zip(["a", "b"], [before, after], [180, 0]):
                if j <= 0 or j >= len(self.clusters):
                    continue
 
                # create tangent control
                tCtrlOffset, tCtrl = self.__createTangentControl(
                    self.clusters[j],
                    i,
                    "_{0}".format(side),
                    ctrl
                )
                
                # parent tangent control
                cmds.parent(tCtrlOffset, ctrl)
                
                # rotate tangent control
                rotate = [a*rot for a in self.aimVector]
                cmds.setAttr("{0}.rotate".format(tCtrlOffset), *rotate)
                
                # add to list
                tangentControls.append(tCtrl)

        return root, controls, tangentControls
        
    # ------------------------------------------------------------------------

    def __getParameters(self):
        # cluster parameters
        num = len(self.controlClusters)
        p1 = curve.splitCurveToParametersByParameter(
            self.curveShape, 
            num
        )

        # locator parameters
        p2 = curve.splitCurveToParametersByLength(
            self.curveShape,
            self.numJoints
        )

        return p1, p2

    def __getWeighting(self):
        return math.remapWeighting(
            self.jParameters,
            self.cParameters
        )
        
    # ------------------------------------------------------------------------
        
    def __createUpVectors(self):
        # variables
        ups = []
        blends = []

        # loop weights
        for i, weight in enumerate(self.weights):
            # create blend matrix
            bm = cmds.createNode(
                "wtAddMatrix",
                n="{0}_bm_{1:03d}".format(self.name, i+1)
            )
            
            # blend cluster weights
            for j, k in enumerate(weight.keys()):
                # get control
                control = self.controls[k]

                # get read group
                children = cmds.listRelatives(control, c=True, f=True)
                group = [c for c in children if c.count("_read_")][0]
                
                # set blend weight
                cmds.setAttr(
                    "{0}.wtMatrix[{1}].weightIn".format(bm, j), 
                    weight[k]
                )
                
                # connect to control
                cmds.connectAttr(
                    "{0}.worldMatrix[0]".format(group), 
                    "{0}.wtMatrix[{1}].matrixIn".format(bm, j)
                )

            # multiply up vector
            pmm = cmds.createNode(
                "pointMatrixMult",
                n="{0}_up_pmm_{1:03d}".format(self.name, i+1)
            )
            
            cmds.setAttr("{0}.vectorMultiply".format(pmm), 1)
            cmds.setAttr("{0}.inPoint{1}".format(pmm, self.upDirection.upper()), 100)
            cmds.connectAttr(
                "{0}.matrixSum".format(bm),
                "{0}.inMatrix".format(pmm),
            )

            # decompose blend matrix
            dm = cmds.createNode(
                "decomposeMatrix",
                n="{0}_up_dm_{1:03d}".format(self.name, i+1)
            )
            
            cmds.connectAttr(
                "{0}.matrixSum".format(bm),
                "{0}.inputMatrix".format(dm),
            )

            # add up with blend
            pma = cmds.createNode(
                "plusMinusAverage",
                n="{0}_up_pma_{1:03d}".format(self.name, i+1)
            )
            
            cmds.connectAttr(
                "{0}.output".format(pmm),
                "{0}.input3D[0]".format(pma),
            )
            
            cmds.connectAttr(
                "{0}.outputTranslate".format(dm),
                "{0}.input3D[1]".format(pma),
            )
            
            # store nodes
            blends.append(bm)
            ups.append(pma)

        return blends, ups
        
    # ------------------------------------------------------------------------
        
    def __createPointOnCurves(self):
        pocs = []
        aims = []

        for i, parameter in enumerate(self.jParameters):
            # create follicle
            loc, poc, aim = curve.createFollicle(
                "{0}_{1:03d}".format(self.name, i + 1),
                self.curve,
                parameter=parameter,
                upDirection=self.upDirection,
                forwardDirection=self.forwardDirection,
                overrideNormal="{0}.output3D".format(self.ups[i]),
                subtractPositionFromNormal=True
            )

            aims.append(aim)
            pocs.append(poc)

            cmds.parent(aim, world=True)

            # remove locator, will be replaced with joint later
            cmds.delete(loc)

        return pocs, aims
        
    # ------------------------------------------------------------------------
        
    def __createJoints(self):
        # variables
        joints = []
        
        # clear selection
        cmds.select(clear=True)

        # create root joint
        root = cmds.joint(n="{0}_root_jnt".format(self.name))
        cmds.setAttr("{0}.drawStyle".format(root), 2)

        # position root joint
        pos = cmds.getAttr("{0}.result.position".format(self.pointOnCurves[0]))
        cmds.setAttr("{0}.translate".format(root), *pos[0])

        # create curve joints
        for i, _ in enumerate(self.pointOnCurves):
            cmds.select(root)

            jnt = cmds.joint(n="{0}_jnt_{1:03d}".format(self.name, i + 1))
            #cmds.setAttr("{0}.displayLocalAxis".format(jnt), 1)
            cmds.setAttr("{0}.inheritsTransform".format(jnt), 0)
            cmds.setAttr("{0}.segmentScaleCompensate".format(jnt), 0)
            cmds.setAttr("{0}.radius".format(jnt), 0.1)

            joints.append(jnt)
            
        return root, joints
        
    # ------------------------------------------------------------------------
        
    def __connectTranslateJoints(self):
        # connect translate of joint
        for poc, jnt in zip(self.pointOnCurves, self.joints):
            cmds.connectAttr(
                "{0}.result.position".format(poc), 
                "{0}.translate".format(jnt)
            )

    def __connectRotateJoints(self):
        # connect rotation of joint
        for aim, jnt in zip(self.aimOnCurves, self.joints):
            cmds.parent(aim, jnt)
            cmds.connectAttr(
                "{0}.constraintRotate".format(aim), 
                "{0}.rotate".format(jnt)
            )
            
    def __scaleConstraintJoints(self):
        # variable
        constraints = []
        
        # loop clusters
        for i, weight in enumerate(self.weights):
            # get cluster drivers
            drivers = [self.controlClusters[k] for k, v in weight.iteritems()]

            # constraint grp to clusters
            c = cmds.scaleConstraint(
                drivers, 
                self.joints[i],
                n="{0}_scale_{1:03d}".format(self.name, i+1),
                mo=False
            )[0]

            # set weighting
            aliases = cmds.scaleConstraint(
                c, 
                query=True, 
                weightAliasList=True
            )
            aliasesData = [
                (aliases[i], weight.values()[i]) 
                for i in range(len(weight.keys()))
            ]

            # set scale constraint
            for attr, value in aliasesData:
                cmds.setAttr("{0}.{1}".format(c, attr), value)

            constraints.append(c)

        return constraints
            
    # ------------------------------------------------------------------------
        
    def __connectJoints(self):
        # constraint root
        cmds.parentConstraint(self.rootControl, self.rootJoint, mo=False)
        cmds.scaleConstraint(self.rootControl, self.rootJoint, mo=False)

        # constraint joints
        self.__connectTranslateJoints()
        self.__connectRotateJoints()

        return self.__scaleConstraintJoints()
        
    # ------------------------------------------------------------------------
        
    def __createScaleReaders(self):
        readers = []

        # get root offset position
        rootPos = cmds.getAttr("{0}.translate".format(self.rootJoint))[0]

        # loop locators
        for i, poc in enumerate(self.pointOnCurves):
            # multiply up vector
            pmm = cmds.createNode(
                "pointMatrixMult",
                n="{0}_scale_pmm_{1:03d}".format(self.name, i+1)
            )
            
            locPos = cmds.getAttr("{0}.result.position".format(poc))[0]
            pos = [
                locPos[0] - rootPos[0],
                locPos[1] - rootPos[1],
                locPos[2] - rootPos[2],
            ]

            cmds.setAttr("{0}.inPoint".format(pmm), *pos)
            cmds.connectAttr(
                "{0}.worldMatrix[0]".format(self.rootJoint), 
                "{0}.inMatrix".format(pmm), 
            )

            readers.append(pmm)
        
        return readers
        
    # ------------------------------------------------------------------------
    
    def __createDistanceBetween(self, nodes, suffix, attr):
        num = len(nodes)
        distances = []

        for i in range(num-1):
            # create node
            db = cmds.createNode(
                "distanceBetween",
                n="{0}_scale_{1}_db_{2:03d}".format(
                    self.name,
                    suffix,
                    i
                )
            )

            # connect input
            cmds.connectAttr(
                "{0}.{1}".format(nodes[i], attr),
                "{0}.point1".format(db)
            )
            cmds.connectAttr(
                "{0}.{1}".format(nodes[i + 1], attr),
                "{0}.point2".format(db)
            )

            # append attribute
            distances.append("{0}.distance".format(db))

        return distances
        
    def __createDistanceBetweenConnection(self, base, scale, i):
        # get scale average from distances
        mult = cmds.createNode(
            "multiplyDivide",
            n="{0}_scale_md_{1:03d}".format(self.name, i)
        )

        cmds.setAttr("{0}.operation".format(mult), 2)
        cmds.connectAttr(scale, "{0}.input1X".format(mult))
        cmds.connectAttr(base, "{0}.input2X".format(mult))

        # bring value down by one
        adl01 = cmds.createNode(
            "addDoubleLinear",
            n="{0}_scale_adl_a_{1:03d}".format(self.name, i)
        )
        
        cmds.setAttr("{0}.input2".format(adl01), -1)
        cmds.connectAttr(
            "{0}.outputX".format(mult), 
            "{0}.input1".format(adl01)
        )

        # multiply by user value
        mdl = cmds.createNode(
            "multDoubleLinear",
            n="{0}_scale_mdl_{1:03d}".format(self.name, i)
        )

        cmds.connectAttr(
            "{0}.output".format(adl01),
            "{0}.input1".format(mdl)
        )
        cmds.connectAttr(
            "{0}.scale_multiplier".format(self.rootControl),
            "{0}.input2".format(mdl)
        )

        # bring value up by one
        adl02 = cmds.createNode(
            "addDoubleLinear",
            n="{0}_scale_adl_b_{1:03d}".format(self.name, i)
        )
        
        cmds.setAttr("{0}.input2".format(adl02), 1)
        cmds.connectAttr(
            "{0}.output".format(mdl),
            "{0}.input1".format(adl02)
        )

        # clamp by user value
        clamp = cmds.createNode(
            "clamp",
            n="{0}_scale_clamp_{1:03d}".format(self.name, i)
        )

        cmds.connectAttr(
            "{0}.scale_clamp_min".format(self.rootControl),
            "{0}.minR".format(clamp)
        )
        cmds.connectAttr(
            "{0}.scale_clamp_max".format(self.rootControl),
            "{0}.maxR".format(clamp)
        )
        cmds.connectAttr(
            "{0}.output".format(adl02),
            "{0}.inputR".format(clamp)
        )

        return "{0}.outputR".format(clamp)
        
    def __createDistanceBetweenConnections(self):
        # connect scales
        connections = []
        indices = range(len(self.bDistances))

        # loop distances
        for i, base, scale in zip(indices, self.bDistances, self.sDistances):
            connections.append(
                self.__createDistanceBetweenConnection(
                    base, scale, i+1
                )
            )

        # duplicate last distance
        connections.append(connections[-1])
        return connections

    # ------------------------------------------------------------------------
        
    def __createStretchAndSquash(self):
        # add spacer attribute
        attribute.addSpacerAttr(self.rootControl)
        
        # add spacer stretch and squash attribute
        attribute.addAttr(
            self.rootControl, "scale_multiplier", defaultValue=1, minValue=0
        )
        attribute.addAttr(
            self.rootControl, "scale_clamp_min", defaultValue=0.1, minValue=0
        )
        attribute.addAttr(
            self.rootControl, "scale_clamp_max", defaultValue=2, minValue=0
        )
        
        # create distance between nodes
        self.bDistances = self.__createDistanceBetween(
            self.pointOnCurves, 
            "base", 
            "result.position"
        )
        self.sDistances = self.__createDistanceBetween(
            self.scaleReaders, 
            "scale", 
            "output"
        )

        # create user input hierarchy
        connections = self.__createDistanceBetweenConnections()

        # determine axis to scale
        axis = ["X", "Y", "Z"]
        axis.remove(self.forwardDirection.upper())

        # connect to scale constraint
        for i, connection in enumerate(connections):
            for a in axis:
                cmds.connectAttr(
                    connection,
                    "{0}.offset{1}".format(
                        self.scaleConstraints[i],
                        a
                    )
                )

    # ------------------------------------------------------------------------
    
    def __createSlideControls(self):
        # variables
        offsets = []
        controls = []
        
        # loop controls
        for suffix in ["slide", "slide_min", "slide_max"]:
            ctrlOffset, ctrl = control.createControlShape(
                "{0}_{1}".format(self.name, suffix),
                self.slideControlShape,
                self.slideControlColour
            )
            
            # scale constraint
            cmds.scaleConstraint(self.rootControl, ctrlOffset)

            # append to list
            offsets.append(ctrlOffset)
            controls.append(ctrl)
            
        # scale controls
        for ctrl in controls[1:]:
            cmds.setAttr("{0}.scale".format(ctrl), 0.5, 0.5, 0.5)
            cmds.makeIdentity(ctrl, apply=True, scale=True)
        
        # parent controls
        cmds.parent(
            offsets,
            self.rootControl
        )

        return controls
        
    def __attachSlideControlsToMotionPath(self):
        # variables
        motionPaths = []
        
        # create motion path
        mpData = {
            "worldUpType":"Object Rotation Up",
            "worldUpObject":self.rootControl,
            "fractionMode":False,
            "worldUpVector":self.worldUpVector,
        }
        
        for ctrl in [
            self.slideControl, 
            self.slideMinControl, 
            self.slideMaxControl
        ]:
            # get control offset
            offset = cmds.listRelatives(ctrl, p=True, f=True)[0]
            
            # attach to motion path
            motionPaths.append(
                motionPath.attachToMotionPath(
                    self.curve, offset, **mpData
                )
            )
        
        return motionPaths
        
    def __normalizeSlideAttributes(self):
        normalized = []
        attributes = [
            "slide_center", 
            "slide_shift", 
            "slide_shift_min", 
            "slide_shift_max"
        ]
        
        # loop attributes
        for attr in attributes:
            mdl = cmds.createNode(
                "multDoubleLinear",
                n="{0}_{1}_norm_mdl".format(self.name, attr)
            )

            cmds.setAttr("{0}.input1".format(mdl), 0.1)
            cmds.connectAttr(
                "{0}.{1}".format(self.slideControl, attr),
                "{0}.input2".format(mdl)
            )

            normalized.append("{0}.output".format(mdl))

        return normalized
        
    def __connectSlideControls(self):
        # variables
        clampAttributes = []
        motionPathAttributes = []
        
        # reverse shift attribute
        mdl = cmds.createNode(
            "multDoubleLinear",
            n="{0}_slide_shift_reverse_mdl".format(self.name)
        )
        
        cmds.setAttr("{0}.input1".format(mdl), -1)
        cmds.connectAttr(self.shiftNorm, "{0}.input2".format(mdl))

        # add to center
        attributes = ["shift", "shift_ctrl", "shift_min", "shift_max"]
        inputs = [
            "{0}.output".format(mdl),
            self.shiftNorm, 
            self.shiftMinNorm, 
            self.shiftMaxNorm
        ]

        # get curve parameter length
        parameterLength = curve.parameterLength(self.curveShape)

        # loop attributes
        for attr, input in zip(attributes,inputs):
            # add value with center
            adl = cmds.createNode(
                "addDoubleLinear",
                n="{0}_slide_{1}_adl".format(self.name, attr)
            )
        
            cmds.connectAttr(self.centerNorm, "{0}.input1".format(adl))
            cmds.connectAttr(input, "{0}.input2".format(adl))

            # clamp value between 0-1
            clamp = cmds.createNode(
                "clamp",
                n="{0}_slide_{1}_clamp".format(self.name, attr)
            )
            
            cmds.setAttr("{0}.minR".format(clamp), 0)
            cmds.setAttr("{0}.maxR".format(clamp), 1)
            cmds.connectAttr(
                "{0}.output".format(adl),
                "{0}.inputR".format(clamp)
            )

            # adjust to parameter length
            mdl = cmds.createNode(
                "multDoubleLinear",
                n="{0}_slide_{1}_mdl".format(self.name, attr)
            )
            
            cmds.setAttr("{0}.input1".format(mdl), parameterLength)
            cmds.connectAttr(
                "{0}.outputR".format(clamp),
                "{0}.input2".format(mdl)
            )

            clampAttributes.append("{0}.outputR".format(clamp))
            motionPathAttributes.append("{0}.output".format(mdl))

        # get motion path attributes
        clamp, clampCtrl, clampMin, clampMax = motionPathAttributes

        # connect clamped values to motion path
        cmds.connectAttr(clampCtrl, "{0}.uValue".format(self.mp))
        cmds.connectAttr(clampMin, "{0}.uValue".format(self.mpMin))
        cmds.connectAttr(clampMax, "{0}.uValue".format(self.mpMax))

        # get clamp attributes
        clamp, clampCtrl, clampMin, clampMax = clampAttributes
        return clamp, clampMin, clampMax
        
    # ------------------------------------------------------------------------
    
    def __connectSlideToJoint(self, poc, i):
        # get parameter
        parameter = cmds.getAttr("{0}.parameter".format(poc))

        # create ramp node
        ramp = cmds.createNode(
            "ramp",
            n="{0}_slide_ramp_{1:03d}".format(self.name, i)
        )
        
        # set default colours and positions
        cmds.setAttr("{0}.colorEntryList[0].color".format(ramp), 0, 0, 0)
        cmds.setAttr("{0}.colorEntryList[0].position".format(ramp), 0)
        cmds.setAttr("{0}.colorEntryList[1].color".format(ramp), 1, 1, 1)
        cmds.setAttr("{0}.colorEntryList[1].position".format(ramp), 1)
        cmds.setAttr("{0}.colorEntryList[2].color".format(ramp), 0.5, 0.5, 0.5)
        cmds.setAttr("{0}.colorEntryList[2].position".format(ramp), 0.5)

        # set default uv parameters
        # connect them to solve maya bug or not setting attributs
        adl = cmds.createNode(
            "addDoubleLinear",
            n="{0}_slide_uv_adl_{1:03d}".format(self.name, i)
        )
        
        cmds.setAttr("{0}.input2".format(adl), parameter)
        cmds.connectAttr(
            "{0}.output".format(adl),
            "{0}.uCoord".format(ramp)
        )
        cmds.connectAttr(
            "{0}.output".format(adl),
            "{0}.vCoord".format(ramp)
        )

        # connect control values
        cmds.connectAttr(
            self.clamp, 
            "{0}.colorEntryList[2].position".format(ramp)
        )
        cmds.connectAttr(
            self.centerNorm, 
            "{0}.colorEntryList[2].colorR".format(ramp)
        )
        cmds.connectAttr(
            self.clampMin, 
            "{0}.colorEntryList[0].position".format(ramp)
        )
        cmds.connectAttr(
            self.clampMin, 
            "{0}.colorEntryList[0].colorR".format(ramp)
        )
        cmds.connectAttr(
            self.clampMax, 
            "{0}.colorEntryList[1].position".format(ramp)
        )
        cmds.connectAttr(
            self.clampMax, 
            "{0}.colorEntryList[1].colorR".format(ramp)
        )

        # check if value is between min and max parameter
        conditions = []
        suffixes = ["a", "b"]
        inputs = [self.clampMin, self.clampMax]
        operations = [5,3]

        for suffix, input, operation in zip(suffixes, inputs, operations):
            cd = cmds.createNode(
                "condition",
                n="{0}_slide_cd_{1}_{2:03d}".format(self.name, suffix, i)
            )

            cmds.setAttr("{0}.operation".format(cd), operation)
            cmds.setAttr("{0}.secondTerm".format(cd), parameter)
            cmds.connectAttr(input, "{0}.firstTerm".format(cd))
            
            cmds.setAttr("{0}.colorIfTrueR".format(cd), 1)
            cmds.setAttr("{0}.colorIfFalseR".format(cd), 0)

            conditions.append("{0}.outColorR".format(cd))

        # multiply output to see if value is between min and max parameter
        mdl = cmds.createNode(
            "multDoubleLinear",
            n="{0}_slide_mdl_{1:03d}".format(self.name, i)
        )
        
        cmds.connectAttr(conditions[0], "{0}.input1".format(mdl))
        cmds.connectAttr(conditions[1], "{0}.input2".format(mdl))

        # condition parameter to use ramped or default value
        cd = cmds.createNode(
            "condition",
            n="{0}_slide_cd_c_{1:03d}".format(self.name, i)
        )
        
        cmds.setAttr("{0}.colorIfTrueR".format(cd), parameter)
        cmds.connectAttr(
            "{0}.output".format(mdl), 
            "{0}.firstTerm".format(cd)
        )
        
        cmds.connectAttr(
            "{0}.outColorR".format(ramp),
            "{0}.colorIfFalseR".format(cd)
        )

        # connect result to point on curve node
        cmds.connectAttr(
            "{0}.outColorR".format(cd), 
            "{0}.parameter".format(poc)
        )
    
    def __connectSlideToJoints(self):
        for i, poc in enumerate(self.pointOnCurves[1:-1]):
            self.__connectSlideToJoint(poc, i+1)
    
    # ------------------------------------------------------------------------
    
    def __createSlide(self):
        # create controls
        self._slideControl, \
        self._slideMinControl, \
        self._slideMaxControl = self.__createSlideControls()

        # create attributes
        attribute.addSpacerAttr(self.slideControl)
        
        attribute.addAttr(
            self.slideControl, "slide_center", dv=5, min=0, max=10
        )
        attribute.addAttr(
            self.slideControl, "slide_shift", dv=0, min=-10, max=10
        )
        attribute.addAttr(
            self.slideControl, "slide_shift_min", dv=-10, min=-10, max=0
        )
        attribute.addAttr(
            self.slideControl, "slide_shift_max", dv=10, min=0, max=10
        )
        
        # attach to motionPath
        self.mp, \
        self.mpMin, \
        self.mpMax = self.__attachSlideControlsToMotionPath()
        
        # normalize attributes
        self.centerNorm, \
        self.shiftNorm, \
        self.shiftMinNorm, \
        self.shiftMaxNorm = self.__normalizeSlideAttributes()
        
        # connect controls
        self.clamp, \
        self.clampMin, \
        self.clampMax = self.__connectSlideControls()

        # connect to locators
        self.__connectSlideToJoints()
        
    # ------------------------------------------------------------------------
        
    def create(
            self, 
            name,
            nurbsCurve,
            numJoints, 
            upDirection="y", 
            worldUpDirection="y", 
            forwardDirection="x"
        ):
        """
        Create the spline IK, besides changing attributes from the
        Settings class, the create function itself can also be
        parsed with various variables to customise the result.
        
        :param name: name that is used to prefix all nodes
        :param nurbsCurve: curve to attach the Spline IK to.
        :param numJoints: number of joints to be distributed on the curve
        :param upDirection: "x", "y" or "z", default "y"
        :param worldUpDirection: "x", "y" or "z", default "y"
        :param forwardDirection: "x", "y" or "z", default "x"
        """
        # variables
        self.name = name
        self.curve = nurbsCurve
        self.numJoints = numJoints
        self.upDirection = upDirection
        self.forwardDirection = forwardDirection

        # vector variables
        self.upVector = math.convertAxisToVector(upDirection)
        self.aimVector = math.convertAxisToVector(forwardDirection)
        self.worldUpVector = math.convertAxisToVector(worldUpDirection)
        
        # run the rest of the code in a single undo chunk
        with undo.UndoChunkContext():
            # convert curve to bezier curve
            curve.convertToBezierCurve(self.curve)
            
            # create clusters
            self.clusters = cluster.clusterCurve(self.curve, self.name)
            self.controlClusters = self.clusters[::3]
            
            # create controls
            self._rootControl, \
            self._controls, \
            self._tangentControls = self.__createControls()
            
            # get parameters
            self.cParameters, self.jParameters = self.__getParameters()
            
            # get weight mapping between clusters and locators
            self.weights = self.__getWeighting()
            
            # create up vectors
            self.blends, self.ups = self.__createUpVectors()
            
            # create point on curves
            self.pointOnCurves, \
            self.aimOnCurves = self.__createPointOnCurves()
            
            # create joints
            self._rootJoint, self._joints = self.__createJoints()
            
            # create scale readers
            self.scaleReaders = self.__createScaleReaders()
            self.scaleConstraints = self.__connectJoints()
            
            # create stretch and squash
            self.__createStretchAndSquash()
            
            # create slide
            self.__createSlide()
            
        return self.rootControl