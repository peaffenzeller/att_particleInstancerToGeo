import maya.cmds as mc
import maya.OpenMaya as om

class Att_particleInstancerToGeo():
    def __init__(self):
        self.ui = {"windowName": "instancerToGeo", "windowTitle": "Convert Particle Instances to Geo"}
        self.data = {}
        
        if mc.window(self.ui.get("windowName"), query=True, exists=True):
            om.MGlobal.displayWarning("Window already exists, deleting!")
            mc.deleteUI(self.ui.get("windowName"))
        #end if
        
        #create window variable and layout
        self.ui["win_instancerToGeo"] = mc.window(self.ui.get("windowName"), title=self.ui.get("windowTitle"), wh=[500, 150], s=True)
        
        self._buildUI()
        
        #display window
        mc.showWindow(self.ui.get("win_instancerToGeo"))
    #end def
    
    def _buildUI(self):
        self.ui["layout"] = mc.columnLayout(parent=self.ui.get("win_instancerToGeo"), adj=True)
        self.ui["rowCol"] = mc.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 145), (2, 345)], columnAlign=[1, "right"], columnSpacing=(2, 5))
        
        mc.text(label="Geometry type:")
        self.ui["geoType"] = mc.radioCollection()
        copy_rb = mc.radioButton(label="Copy", collection=self.ui.get("geoType"), data=0)
        mc.text(label="")
        instance_rb = mc.radioButton(label="Instance", collection=self.ui.get("geoType"), data=1)
        mc.radioCollection(self.ui.get("geoType"), edit=True, select=copy_rb)
        
        mc.text(label="Time range:")
        self.ui["timeRange"] = mc.radioCollection()
        mc.rowLayout(numberOfColumns=4)
        timeSlider_rb = mc.radioButton(label="Time Slider", collection=self.ui.get("timeRange"), data=0)
        fromCurrent_rb = mc.radioButton(label="From Current", collection=self.ui.get("timeRange"), data=1)
        start_rb = mc.radioButton(label="Start", collection=self.ui.get("timeRange"), onCommand=lambda x: self._timeRangeStart(True), offCommand=lambda x: self._timeRangeStart(False), data=2)
        startEnd_rb = mc.radioButton(label="Start/End", collection=self.ui.get("timeRange"), onCommand=lambda x: self._timeRangeStartEnd(True), offCommand=lambda x: self._timeRangeStartEnd(False), data=3)
        mc.radioCollection(self.ui.get("timeRange"), edit=True, select=timeSlider_rb)
        
        mc.setParent(self.ui["rowCol"])
        
        mc.text(label="Start time:", enable=False)
        mc.columnLayout()
        self.ui["startFrame"] = mc.textField(width=80, text=mc.playbackOptions(query=True, minTime=True), enable=False)
        mc.setParent(self.ui["rowCol"])
        
        mc.text(label="End time:", enable=False)
        mc.columnLayout()
        self.ui["endFrame"] = mc.textField(width=80, text=mc.playbackOptions(query=True, maxTime=True), enable=False)
        mc.setParent(self.ui["rowCol"])
        
        mc.text(label="By frame:", enable=False)
        mc.columnLayout()
        self.ui["byFrame"] = mc.textField(width=80, text="1")
        
        mc.setParent(self.ui["layout"])
        
        mc.button(label="Convert", command=self._convert)
    #end def
    
    def _timeRangeStart(self, data):
        mc.textField(self.ui.get("startFrame"), edit=True, enable=data)
    #end def
    
    def _timeRangeStartEnd(self, data):
        mc.textField(self.ui.get("startFrame"), edit=True, enable=data)
        mc.textField(self.ui.get("endFrame"), edit=True, enable=data)
    #end def
    
    def _convert(self, data):
        self.data["geoType"] = mc.radioButton(mc.radioCollection(self.ui.get("geoType"), query=True, select=True), query=True, data=True)
        self.data["timeRange"] = mc.radioButton(mc.radioCollection(self.ui.get("timeRange"), query=True, select=True), query=True, data=True)
        self.data["startFrame"] = mc.textField(self.ui.get("startFrame"), query=True, text=True)
        self.data["endFrame"] = mc.textField(self.ui.get("endFrame"), query=True, text=True)
        self.data["byFrame"] = mc.textField(self.ui.get("byFrame"), query=True, text=True)
    #end def
#end class

Att_particleInstancerToGeo()
'''
# RUN MAIN PROCEDURE WITH SETTINGS FROM GUI 
def sag_instancerToGeometry_cmd():
    dupOrInst = radioButtonGrp( 'sag_instancerToGeometry_win__dupOrInst_RBG', q = True, select = True ) - 1
    fromCurFrame = checkBox( 'sag_instancerToGeometry_win__fromCurFrame_ChB', q = True, value = True )
    rangeSpecified = radioButtonGrp( 'sag_instancerToGeometry_win__range_RBG', q = True, select = True ) - 1
    start = intFieldGrp( 'sag_instancerToGeometry_win__range_IFG', q = True, value1 = True )
    end = intFieldGrp( 'sag_instancerToGeometry_win__range_IFG', q = True, value2 = True )

    sag_instancerToGeometry_do( dupOrInst, fromCurFrame, rangeSpecified, start, end )


# MAIN PROCEDURE
def sag_instancerToGeometry_do( dupOrInst, fromCurFrame, rangeSpecified, start, end ):

    # RANGE OPTIONS
    currentFrame = currentTime( q = True )
    startFrame = playbackOptions( q = True, min = True )
    endFrame = playbackOptions( q = True, max = True )

    if rangeSpecified > 0:
        startFrame = start
        endFrame = end
    elif fromCurFrame > 0:
        startFrame = currentFrame

    # MAKE A LIST OF ALL SELECTED INSTANCERS
    instList = []

    selList = ls( selection = True )

    for each in selList:
        if objectType( each ) == 'instancer':
            instList.append( each )

    if instList == []:
        print 'No instancers selected!'
        return

    # FIND GEOMETRY, PARTICLE OBJECTS AND MAPPED ATTRIBUTES FOR INSTANCERS
    geoList = []
    ptList = []
    iamList = []

    blankInsts = []
    for each in instList:
        # MAKE A LIST OF INPUT OBJECTS
        instGeo = listConnections( each + '.inputHierarchy', source = True, destination = False, connections = False, plugs = False )

        if instGeo == None:
            print 'No geometry connected to instancer ' + each + '!'
            blankInsts.append( each )

        else:
            # MAKE A LIST OF PARTICLE OBJECTS AND THEIR INSTANCER MAPPED ATTRIBUTES
            conn = listConnections( each + '.inputPoints', source = True, destination = False, connections = False, plugs = True )

            if conn == None:
                print 'No particles connected to instancer ' + each + '!'
                blankInsts.append( each )
            else:
                geoList.append( instGeo )
                ptList.append( conn[0][:conn[0].find( '.' )] )
                iamList.append( getAttr( conn[0][:conn[0].rfind( '.' )] + '.instanceAttributeMapping' ) )

    # REMOVE INSTANCERS WITH NO GEOMETRY OR PARTICLES ATTACHED FROM THE LIST
    for each in blankInsts:
        instList.remove( each )

    # QUIT IF NO REASONABLE INSTANCERS LEFT
    if instList == []:
        return

    # SET UNITS TO CM (SINCE THAT'S WHAT PARTICLE VALUES USING NO MATTER WHAT)
    origUnits = currentUnit( query = True, linear = True )
    currentUnit( linear = 'cm' )

    # LISTS FOR STORING CONVERTED IDS AND CREATED DUPLICATES
    pids = []
    dups = []
    for inst in instList:
        pids.append( [] )
        dups.append( [] )

    # MAIN CONVERSION LOOP
    for t in xrange( int( startFrame ), int( endFrame ) + 1 ):
        currentTime( t, update = True )

        for inst in instList:
            instInd = instList.index( inst )
            instGeo = geoList[instInd]
            instPt = ptList[instInd]
            instIam = iamList[instInd]

            # GET INSTANCER ROTATION ORDER AND CONVERT IT INTO GEOMETRY ROTATION ORDER
            instRodOrig = getAttr( inst + '.rotationOrder' )
            instRodConv = { 0:0, 1:3, 2:4, 3:1, 4:2, 5:5 }
            instRod = instRodConv[ instRodOrig ]

            deadPids = pids[instList.index(inst)][:] 
            instNum = getAttr( inst + '.instanceCount' )
            for i in xrange( 0, instNum ):
                # GET GENERAL OPTIONS VALUES
                pid = int(particle( instPt, q = True, at = 'particleId', order = i )[0])
                pos = particle( instPt, q = True, at = 'worldPosition', order = i )
                scl = (1,1,1)
                shr = (0,0,0)
                vis = 1.0
                idx = 0.0
                if 'scale' in instIam:
                    scl = particle( instPt, q = True, at = instIam[instIam.index( 'scale' )+1], order = i )
                if 'shear' in instIam:
                    shr = particle( instPt, q = True, at = instIam[instIam.index( 'shear' )+1], order = i )
                if 'visibility' in instIam:
                    vis = particle( instPt, q = True, at = instIam[instIam.index( 'visibility' )+1], order = i )[0]
                if 'objectIndex' in instIam:
                    idx = particle( instPt, q = True, at = instIam[instIam.index( 'objectIndex' )+1], order = i )[0]

                # IF OBJECT INDEX IS HIGHER OR LOWER THAN AVAILABLE NUMBER OF INSTANCE OBJECTS - CLAMP TO THE CLOSEST POSSIBLE VALUE
                if idx > (len( instGeo ) - 1):
                    idx = (len( instGeo ) - 1)
                elif idx < 0:
                    idx = 0

                # IF SCALE ATTRIBUTE IS FLOAT INSTEAD OF VECTOR - FORCE VECTOR
                if len( scl ) < 3:
                    scl = [scl[0], scl[0], scl[0]]

                # GET ROTATION OPTIONS VALUES
                rot = (0,0,0)
                if 'rotation' in instIam:
                    rot = particle( instPt, q = True, at = instIam[instIam.index( 'rotation' )+1], order = i )

                # IF THE PARTICLE IS NEWBORN MAKE A DUPLICATE
                newBorn = 0

                dupName = inst.replace( '|', '_' ) + '_' + instGeo[int(idx)].replace( '|', '_' ) + '_id_' + str(pid)

                if pid not in pids[instList.index(inst)]:
                    pids[instList.index(inst)].append( pid )

                    # IF OBJECT WITH THE SAME NAME ALREADY EXISTS, ADD _# SUFFIX
                    if objExists( dupName ):
                        z = 1
                        dupName += '_' + str( z )
                        while objExists( dupName ):
                            z += 1
                            dupName = dupName[:dupName.rfind( '_' )+1] + str( z )

                    if dupOrInst > 0:
                        dup = instance( instGeo[int(idx)], name = dupName )[0]
                        trsConns = listConnections( instGeo[int(idx)], s = True, d = False, c = True, p = True )
                        if trsConns != None:
                            for y in xrange( 0, len( trsConns ), 2 ):
                                if not isConnected( trsConns[y+1], dup + trsConns[y][trsConns[y].rfind( '.' ):] ):
                                    connectAttr( trsConns[y+1], dup + trsConns[y][trsConns[y].rfind( '.' ):] )
                    else:
                        dup = duplicate( instGeo[int(idx)], name = dupName, inputConnections = True )[0]

                    # CREATE A GROUP FOR A DUPLICATE
                    dupGrp = group( em = True, name = dup + '_grp' )
                    parent( dupGrp, dup )
                    setAttr( dupGrp + '.translate', 0, 0, 0, type = 'double3' )
                    parent( dupGrp, world = True )
                    parent( dup, dupGrp )

                    dup = dupGrp

                    dups[instList.index(inst)].append( dup )

                    if t != int( startFrame ):
                        newBorn = 1
                else:
                    # IF OBJECT WITH THE SAME NAME EXISTS FROM PREVIOUS BAKE, FIND THE SUFFIXED NAME FROM THIS BAKE
                    if not dupName + '_grp' in dups[instList.index(inst)]:
                        z = 1
                        dupName += '_' + str( z )
                        while not dupName + '_grp' in dups[instList.index(inst)]:
                            z += 1
                            dupName = dupName[:dupName.rfind( '_' )+1] + str( z )

                    dup = dupName + '_grp'
                    if pid in deadPids:
                        deadPids.remove( pid )

                # TRANSFORM THE DUPLICATE
                setAttr( dup + '.translate', pos[0], pos[1], pos[2], type = 'double3' )
                setAttr( dup + '.scale', scl[0], scl[1], scl[2], type = 'double3' )
                setAttr( dup + '.visibility', vis )

                setAttr( dup + '.rotateOrder', instRod )
                setAttr( dup + '.rotate', rot[0], rot[1], rot[2], type = 'double3' )

                # SET KEYFRAMES
                setKeyframe( dup, inTangentType = 'linear', outTangentType = 'linear', attribute = ( 'translate', 'rotate', 'scale', 'visibility' ) )
                if newBorn > 0:
                    setKeyframe( dup + '.visibility', time = currentTime( q = True ) - 1, value = 0 )
            
            # MAKE DEAD INSTANCES INVISIBLE
            for dead in deadPids:
                setKeyframe( dups[instList.index(inst)][pids[instList.index(inst)].index(dead)] + '.visibility', value = 0 )

    # GROUP DUPLICATES, DELETE STATIC CHANNELS AND APPLY EULER FILTER
    for inst in instList:
        group( dups[instList.index(inst)], name = inst + '_geo_grp', world = True )
        for obj in dups[instList.index(inst)]:
            delete( obj, staticChannels = True, unitlessAnimationCurves = False, hierarchy = 'none', controlPoints = False, shape = False )
            animCurves = listConnections( obj, source = True, destination = False, connections = False, plugs = False )
            filterCurve( animCurves )
    
    # RESTORING ORIGINAL UNITS
    currentUnit( linear = origUnits )
    
sag_instancerToGeometry()'''