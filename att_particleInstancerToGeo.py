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
        self.data["byFrame"] = int(float(mc.textField(self.ui.get("byFrame"), query=True, text=True)))
        
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
        
        sel = mc.ls(sl=True)
        instancers = []
        
        for obj in sel:
            if mc.objectType(obj) == "instancer":
                instancers.append(obj)
            #end if
        #end for
        
        if len(instancers) == 0:
            om.MGlobal.displayError("No instancers selected to convert, aborting!")
            return
        #end if
        
        tmp_instancers = instancers
        instancers = []
        for instancer in tmp_instancers:
            instancedObjs = mc.listConnections(instancer + ".inputHierarchy", source=True)
            
            if instancedObjs == None:
                om.MGlobal.displayWarning("No instanced objects found for instancer: {}".format(instancer))
                instancers.remove(instancer)
                continue
            #end if
            
            inputParticles = mc.listConnections(instancer + ".inputPoints", source=True, plugs=True)
            
            if inputParticles == None:
                om.MGlobal.displayWarning("No connected particle systems found for instancer: {}".format(instancer))
                instancers.remove(instancer)
                continue
            #end if
            
            inputParts = inputParticles[0].split(".")
            particleSys = inputParts[0]
            #get per particle attributes
            particleAttrs = mc.getAttr("{}.{}.instanceAttributeMapping".format(inputParts[0], inputParts[1]))
            
            instancerData = {
                "instancer": instancer,
                "obj": instancedObjs,
                "particleSys": particleSys,
                "attrs": particleAttrs
            }
            instancers.append(instancerData)
        #end for
        
        if len(instancers) == 0:
            return
        #end if
        
        '''
        for instancer in instancers:
            instancerRoo = mc.getAttr("{}.rotationOrder".format(instancer["instancer"]))
            rooConversion = {0:0, 1:3, 2:4, 3:1, 4:2, 5:5}
            roo = rooConversion[instancerRoo]
            
            numInstances = mc.getAttr("{}.instanceCount".format(instancer["instancer"]))
            
            particles = []
            for i in range(0, numInstances):
                particleId = mc.particle(instancer["particleSys"], query=True, attribute="particleId", order=i)
                particlePos = mc.particle(instancer["particleSys"], query=True, attribute="worldPosition", order=i)
                particleScale = (1, 1, 1)
                particleRot = (0, 0, 0)
                particleShear = (0, 0, 0)
                particleVel = (0, 0, 0)
                particleVis = 1
                particleIndex = 0
                
                if "scale" in instancer["attrs"]:
                    particleScale = mc.particle(instancer["particleSys"], query=True, attribute="scale", order=i)
                #end if
                if "rotation" in instancer["attrs"]:
                    particleRot = mc.particle(instancer["particleSys"], query=True, attribute="rotation", order=i)
                #end if
                if "shear" in instancer["attrs"]:
                    particleShear = mc.particle(instancer["particleSys"], query=True, attribute="shear", order=i)
                #end if
                if "velocity" in instancer["attrs"]:
                    particleVel = mc.particle(instancer["particleSys"], query=True, attribute="velocity", order=i)
                #end if
                if "visibility" in instancer["attrs"]: 
                    particleVis = mc.particle(instancer["particleSys"], query=True, attribute="visibility", order=i)
                #end if
                if "objectIndex" in instancer["attrs"]:
                    particleIndex = mc.particle(instancer["particleSys"], query=True, attribute="objectIndex", order=i)
                #end if
                
                instanceExists = 0
                if particleIndex not in particles:
                    particles.append(particleIndex)
                    
                    duplicateName = "{}_particleId{}".format(instancer["obj"], particleId)
                    print duplicateName
                #end if
            #end for
        #end for'''
    #end def
#end class

Att_particleInstancerToGeo()