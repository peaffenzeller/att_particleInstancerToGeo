import maya.cmds as mc
import maya.OpenMaya as om
from __builtin__ import object

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
    
    #toggle time range start frame texfield depending on selected checkbox
    def _timeRangeStart(self, data):
        mc.textField(self.ui.get("startFrame"), edit=True, enable=data)
    #end def
    
    #toggle time range end frame texfield depending on selected checkbox
    def _timeRangeStartEnd(self, data):
        mc.textField(self.ui.get("startFrame"), edit=True, enable=data)
        mc.textField(self.ui.get("endFrame"), edit=True, enable=data)
    #end def
    
    #main method to convert particle instances to actual geometry
    def _convert(self, data):
        #query user input
        self.data["geoType"] = mc.radioButton(mc.radioCollection(self.ui.get("geoType"), query=True, select=True), query=True, data=True)
        self.data["timeRange"] = mc.radioButton(mc.radioCollection(self.ui.get("timeRange"), query=True, select=True), query=True, data=True)
        self.data["byFrame"] = int(float(mc.textField(self.ui.get("byFrame"), query=True, text=True)))
        
        #set start and end frame depending on time range checkbox
        #time slider
        if self.data["timeRange"] == 0:
            self.data["startFrame"] = int(float(mc.playbackOptions(query=True, minTime=True)))
            self.data["endFrame"] = int(float(mc.playbackOptions(query=True, maxTime=True)))
        #from current
        elif self.data["timeRange"] == 1:
            self.data["startFrame"] = mc.currentTime(query=True)
            self.data["endFrame"] = int(float(mc.playbackOptions(query=True, maxTime=True)))
        #start
        elif self.data["timeRange"] == 2:
            self.data["startFrame"] = int(float(mc.textField(self.ui.get("startFrame"), query=True, text=True)))
            self.data["endFrame"] = int(float(mc.playbackOptions(query=True, maxTime=True)))
        #start/end
        elif self.data["timeRange"] == 3:
            self.data["startFrame"] = int(float(mc.textField(self.ui.get("startFrame"), query=True, text=True)))
            self.data["endFrame"] = int(float(mc.textField(self.ui.get("endFrame"), query=True, text=True)))
        #end if
        
        #query selected objects
        sel = mc.ls(sl=True)
        instancers = []
        
        #check object type
        for obj in sel:
            if mc.objectType(obj) == "instancer":
                instancers.append(obj)
            #end if
        #end for
        
        #abort if list of instancers is empty
        if len(instancers) == 0:
            om.MGlobal.displayError("No instancers selected to convert, aborting!")
            return
        #end if
        
        tmp_instancers = instancers
        instancers = []
        for instancer in tmp_instancers:
            #check instancer for connected input geometry
            instancedObjs = mc.listConnections(instancer + ".inputHierarchy", source=True)
            
            if instancedObjs == None:
                om.MGlobal.displayWarning("No instanced objects found for instancer: {}".format(instancer))
                instancers.remove(instancer)
                continue
            #end if
            
            #check instancer for connected particle system
            inputParticles = mc.listConnections(instancer + ".inputPoints", source=True, plugs=True)
            
            if inputParticles == None:
                om.MGlobal.displayWarning("No connected particle systems found for instancer: {}".format(instancer))
                instancers.remove(instancer)
                continue
            #end if
            
            #get particle system and per particle attributes
            inputParts = inputParticles[0].split(".")
            particleSys = inputParts[0]
            #get per particle attributes
            particleAttrs = mc.getAttr("{}.{}.instanceAttributeMapping".format(inputParts[0], inputParts[1]))
            
            #store data in dictionary and append to instancers list
            instancerData = {
                "instancer": instancer,
                "obj": instancedObjs,
                "particleSys": particleSys,
                "attrs": particleAttrs
            }
            instancers.append(instancerData)
        #end for
        
        #if list of checked instancers is empty - abort
        if len(instancers) == 0:
            om.MGlobal.displayError("Not able to convert selected particle instancer(s), aborting!")
            return
        #end if
        
        for instancer in instancers:
            #get correct rotation order
            instancerRoo = mc.getAttr("{}.rotationOrder".format(instancer["instancer"]))
            rooConversion = {0:0, 1:3, 2:4, 3:1, 4:2, 5:5}
            roo = rooConversion[instancerRoo]
            
            #for every frame in time range
            particles = {}
            for frame in range(self.data.get("startFrame"), self.data.get("endFrame") + 1, self.data.get("byFrame")):
                mc.currentTime(frame, update=True)
                
                #get count of all existing instances
                numInstances = mc.getAttr("{}.instanceCount".format(instancer["instancer"]))
                
                for i in range(0, numInstances):
                    particleId = int(mc.particle(instancer["particleSys"], query=True, attribute="particleId", order=i)[0])
                    particlePos = [0, 0, 0]
                    particleScale = [1, 1, 1]
                    particleShear = [0, 0, 0]
                    particleVis = True
                    particleIndex = 0
                    particleRot = [0, 0, 0]
                    particleAimDir = [0, 0, 0]
                    
                    if "position" in instancer["attrs"]:
                        particlePos = mc.particle(instancer["particleSys"], query=True, attribute=instancer["attrs"][instancer["attrs"].index("position") + 1], id=particleId)
                    #end if
                    if "scale" in instancer["attrs"]:
                        particleScale = mc.particle(instancer["particleSys"], query=True, attribute=instancer["attrs"][instancer["attrs"].index("scale") + 1], id=particleId)
                    #end if
                    if "shear" in instancer["attrs"]:
                        particleShear = mc.particle(instancer["particleSys"], query=True, attribute=instancer["attrs"][instancer["attrs"].index("shear") + 1], id=particleId)
                    #end if
                    if "visibility" in instancer["attrs"]: 
                        particleVis = mc.particle(instancer["particleSys"], query=True, attribute=instancer["attrs"][instancer["attrs"].index("visibility") + 1], id=particleId)
                    #end if
                    if "objectIndex" in instancer["attrs"]:
                        particleIndex = int(mc.particle(instancer["particleSys"], query=True, attribute=instancer["attrs"][instancer["attrs"].index("objectIndex") + 1], id=particleId)[0])
                    #end if
                    
                    if "rotation" in instancer["attrs"]:
                        particleRot = mc.particle(instancer["particleSys"], query=True, attribute=instancer["attrs"][instancer["attrs"].index("rotation") + 1], id=particleId)
                    #end if
                    if "aimDirection" in instancer["attrs"]:
                        particleAimDir = mc.particle(instancer["particleSys"], query=True, attribute=instancer["attrs"][instancer["attrs"].index("aimDirection") + 1], id=particleId)
                    #end if
                    '''
                    # MISSING
                    #    - rotation type
                    #    - aim position
                    #    - aim axis
                    #    - aim up axis
                    #    - aim world up
                    '''
                    
                    #append particle to particles list if it doesn't already exist
                    #create duplicate of instanced object
                    if particleId not in particles:
                        dupName = "{}_particleId{}".format(instancer["obj"][particleIndex], particleId)
                        #depending on selected geo type create duplicate or instance
                        dupObj = ""
                        if self.data.get("geoType") == 0:
                            print "copy object"
                            #duplicate with input connections
                            dupObj = mc.duplicate(instancer["obj"][particleIndex], returnRootsOnly=True, upstreamNodes=True, name=dupName)
                        else:
                            print "instance object"
                            dupObj = mc.instance(instancer["obj"][particleIndex], name=dupName)
                        #end if
                        
                        #group duplicated object, transfer particle values to group
                        dupGrp = mc.group(empty=True, name="{}_grp".format(dupName))
                        mc.parent(dupGrp, dupObj)
                        mc.xform(dupGrp, t=(0, 0, 0))
                        mc.parent(dupGrp, world=True)
                        mc.parent(dupObj, dupGrp)
                        
                        particles[particleId] = dupGrp
                    #end if
                    
                    #translate duplicated object to particle position
                    mc.xform(particles[particleId], t=particlePos, ws=True)
                    #set scale to match particle scale
                    mc.xform(particles[particleId], s=particleScale, ws=True)
                    #set rotation order to match instancer roo
                    mc.setAttr("{}.rotateOrder".format(particles[particleId]), instancerRoo)
                    #create tmp locator to aim duplicated object
                    locAim = mc.spaceLocator()
                    mc.xform(locAim, t=(particlePos[0] + particleAimDir[0], particlePos[1] + particleAimDir[1], particlePos[2] + particleAimDir[2]), ws=True)
                    aimCnst = mc.aimConstraint(locAim, particles[particleId], mo=False)
                    
                    #key duplicated object on current frame
                    mc.setKeyframe(particles[particleId], attribute=("translate", "rotate", "scale", "visibility"))
                    
                    #delete aim constraint and aim locator
                    mc.delete(aimCnst, locAim)
                #end for
            #end for
        #end for
    #end def
#end class

Att_particleInstancerToGeo()