'''
ModelDef Exporter for Maya

(c) 2009 - 2011
    Balakrishnan Ranganathan (balki_live_com)
    All Rights Reserved.
'''

import Common as Com
reload(Com)

from Common import *

global defFile
global MaxWeights

class Keyframe:
    JointIndex = -1
    Frame = -1
    Time = -1
    Position = OpenMaya.MVector()
    Rotation = OpenMaya.MQuaternion()
    AbsolutePosition = OpenMaya.MVector()
    AbsoluteRotation = OpenMaya.MQuaternion()
    
class Material:
    Name = ""
    DiffuseColor = OpenMaya.MColor()
    DiffuseCoeff = 0
    SpecularColor = OpenMaya.MColor()
    CosinePower = 0
    Transparency = 0
    DiffuseMapFilename = ""
    NormalMapFilename = ""
    SpecularMapFilename = ""
    LightmapFilename = ""
    UseAlpha = False
    DrawBackfaces = False
    Reflectivity = 0
    RepeatUV = []

class Joint:
    Name = ""
    Index = -1
    ParentIndex = -1
    Position = OpenMaya.MVector()
    Rotation = OpenMaya.MQuaternion()
    AbsolutePosition = OpenMaya.MVector()
    AbsoluteRotation = OpenMaya.MQuaternion()
    
    DagPath = OpenMaya.MDagPath()

class WeightedVertex:
    Index = -1
    Position = OpenMaya.MVector()
    Weights = []
    Joints = []
    
class UVSet:
    Name = ""
    Us = {}
    Vs = {}
    
    def __init__(self, name):
        self.Name = name
        
        self.Us = {}
        self.Vs = {}
    
class ModelMesh:
    Name = ""
    Material = None
    Indices = []
    Points = {}
    Normals = {}
    Tangents = {}
    Binormals = {}
    UVSets = {}
    WeightedVertexIndices = []

class Model:
    WeightedVertices = []
    Joints = []
    ModelMeshes = []
    Keyframes = {}

    Materials = {}
    JointIndexByName = {}
    WeightedVertexIndexByPosition = {}
    HasSkinningData = False

def ProcessModelMesh(dagPath, component, material, model):
    mesh = OpenMaya.MFnMesh(dagPath)
    
    # Setup model mesh storage variables
    modelMesh = ModelMesh()
    modelMesh.Material = material
    modelMesh.Name = mesh.name()
    modelMesh.Indices = []
    modelMesh.Points = {}
    modelMesh.Normals = {}
    modelMesh.Tangents = {}
    modelMesh.Binormals = {}
    modelMesh.UVSets = {}
    modelMesh.WeightedVertexIndices = {}
    uniqueIndex = -1
    
    # Get the model mesh's tangent and binormal vectors for all face vertices
    meshTangents = OpenMaya.MFloatVectorArray()
    meshBinormals = OpenMaya.MFloatVectorArray()
    mesh.getTangents(meshTangents, OpenMaya.MSpace.kObject)
    mesh.getBinormals(meshBinormals, OpenMaya.MSpace.kObject)
    
    meshPolygonIter = OpenMaya.MItMeshPolygon(dagPath, component)
    while not meshPolygonIter.isDone():
        # Setup polygon storage variables
        polygonVertexIndices = OpenMaya.MIntArray()
        polygonVertexPoints = OpenMaya.MPointArray()
        polygonVertexNormals = OpenMaya.MVectorArray()
        uvSetNames = []
        uvSets = {}
        
        # Get polygon information
        meshPolygonIter.getVertices(polygonVertexIndices)
        meshPolygonIter.getPoints(polygonVertexPoints, OpenMaya.MSpace.kObject)
        meshPolygonIter.getNormals(polygonVertexNormals, OpenMaya.MSpace.kObject)
        meshPolygonIter.getUVSetNames(uvSetNames)
        
        # Get UV sets
        for uvSetName in uvSetNames:
            uvSets[uvSetName] = UVSet(uvSetName)
            uvSet = uvSets[uvSetName]
            uvSet.Us = OpenMaya.MFloatArray()
            uvSet.Vs = OpenMaya.MFloatArray()
            
            meshPolygonIter.getUVs(uvSet.Us, uvSet.Vs, uvSetName)
            if uvSetName not in modelMesh.UVSets:
                modelMesh.UVSets[uvSetName] = UVSet(uvSetName)

        # Prepare unique indices and reverse index lookup
        reverseIndexLookup = {}
        uniqueVertexIndices = {}
        for i in range(len(polygonVertexIndices)):
            uniqueIndex += 1
            uniqueVertexIndices[polygonVertexIndices[i]] = uniqueIndex
            reverseIndexLookup[polygonVertexIndices[i]] = i
            
            modelMesh.Points[uniqueIndex] = OpenMaya.MPoint(polygonVertexPoints[i] / 100);
            modelMesh.Normals[uniqueIndex] = OpenMaya.MVector(polygonVertexNormals[i])
            
            tangentIndex = meshPolygonIter.tangentIndex(i)
            modelMesh.Tangents[uniqueIndex] = OpenMaya.MFloatVector(meshTangents[tangentIndex])
            modelMesh.Binormals[uniqueIndex] = OpenMaya.MFloatVector(meshBinormals[tangentIndex])
            
            for uvSetName in uvSetNames:
                uvSetSource = uvSets[uvSetName]
                uvSetTarget = modelMesh.UVSets[uvSetName]
                if uvSetSource.Us.length() > 0:
                    uvSetTarget.Us[uniqueIndex] = uvSetSource.Us[i]
                    uvSetTarget.Vs[uniqueIndex] = -uvSetSource.Vs[i]
                else:
                    uvSetTarget.Us[uniqueIndex] = 0
                    uvSetTarget.Vs[uniqueIndex] = 0
        
        # Get info about the triangles that make up this polygon
        vertexPoints = OpenMaya.MPointArray()
        vertexIndices = OpenMaya.MIntArray()
        meshPolygonIter.getTriangles(vertexPoints, vertexIndices, OpenMaya.MSpace.kObject)
        
        # Prepare the unique indices list
        for i in range(vertexIndices.length()):
            modelMesh.Indices.append(uniqueVertexIndices[vertexIndices[i]])
        
        # If draw backfaces is on, prepare the unique indices again, but backwards this time
        if material.DrawBackfaces == True:
            for i in range(vertexIndices.length() - 1, -1, -1):
                modelMesh.Indices.append(uniqueVertexIndices[vertexIndices[i]])
            
        # Move on to the next polygon
        meshPolygonIter.next()

    model.ModelMeshes.append(modelMesh)

def GetFileTextureName(plug):
    connectedPlugs = OpenMaya.MPlugArray()
    plug.connectedTo(connectedPlugs, True, False)
    for k in range(connectedPlugs.length()):
        if (connectedPlugs[k].node().apiType() == OpenMaya.MFn.kFileTexture):
            depNode = OpenMaya.MFnDependencyNode(connectedPlugs[k].node())
            ftn = depNode.findPlug("ftn")
            textureFilename = ftn.asString()
            
            # Check if the texture exists in the same directory, if not copy it over
            textureDirectoryName = os.path.dirname(textureFilename)
            newTextureFilename = os.path.basename(textureFilename)
            newTextureDirectoryName = os.path.dirname(Cmds.file(q=True, sn=True))
            if not IsNoneOrEmpty(textureDirectoryName) and not textureDirectoryName == newTextureDirectoryName:
                sys.__stdout__.write("\nDirectories: %s | %s" % (textureDirectoryName, newTextureDirectoryName))
                newTextureFilename = "%s/%s" % (newTextureDirectoryName, newTextureFilename)
                sys.__stdout__.write("\nCopying texture file: %s => %s" % (textureFilename, newTextureFilename))
                shutil.copy(textureFilename, newTextureFilename)
                ftn.setString(newTextureFilename)
                textureFilename = newTextureFilename
            return os.path.basename(ftn.asString())
    
    return ""
    
def ProcessModel(dagPath):
    model = Model()
    model.Materials = {}
    model.ModelMeshes = []
    
    # Setup model representation
    instanceNumber = dagPath.instanceNumber()
    mesh = OpenMaya.MFnMesh(dagPath)
    modelMeshIndex = 0
    
    # Process the materials
    sets = OpenMaya.MObjectArray()
    components = OpenMaya.MObjectArray()
    mesh.getConnectedSetsAndMembers(instanceNumber, sets, components, True)
    for i in range(sets.length()):
        # Setup storage material storage variables
        material = Material()
        
        # Current set and component
        set = sets[i]
        component = components[i]
        
        # Maya handles
        fnSet = OpenMaya.MFnSet(set)
        dependencyNode = OpenMaya.MFnDependencyNode(set)
        
        # Get the shaders
        surfaceShaderAttribute = dependencyNode.attribute("surfaceShader");
        surfaceShaderPlug = OpenMaya.MPlug(set, surfaceShaderAttribute)
        
        # Get the connections
        sourcePlugArray = OpenMaya.MPlugArray()
        surfaceShaderPlug.connectedTo(sourcePlugArray, True, False)
        
        if sourcePlugArray.length() == 0:
            continue
        
        # Get the relevant material connection
        sourceNode = sourcePlugArray[0].node()
        materialDepNode = OpenMaya.MFnDependencyNode(sourceNode)
        material.Name = materialDepNode.name()
        
        if material.Name in ["lambert1"]:
            print "[Warning] Material %s found. Is this intentional?" % (material.Name)
        
        # Process basic material (lambert) parameters
        if sourceNode.hasFn(OpenMaya.MFn.kLambert):
            lambertShader = OpenMaya.MFnLambertShader(sourceNode)
            material.DiffuseColor = lambertShader.color()
            material.DiffuseCoeff = lambertShader.diffuseCoeff()
            material.Transparency = lambertShader.transparency()[0]
            
            try:
                lambertShader.findPlug("UseAlpha", True)
            except RuntimeError:
                useAlphaAttribute = OpenMaya.MFnNumericAttribute().create("UseAlpha", "UseAlpha", OpenMaya.MFnNumericData.kBoolean)
                lambertShader.addAttribute(useAlphaAttribute)
            finally:
                useAlphaPlug = lambertShader.findPlug("UseAlpha", True)
                material.UseAlpha = useAlphaPlug.asBool()
                
            try:
                lambertShader.findPlug("DrawBackfaces", True)
            except RuntimeError:
                drawBackfacesAttribute = OpenMaya.MFnNumericAttribute().create("DrawBackfaces", "DrawBackfaces", OpenMaya.MFnNumericData.kBoolean)
                lambertShader.addAttribute(drawBackfacesAttribute)
            finally:
                drawBackfacesPlug = lambertShader.findPlug("DrawBackfaces", True)
                material.DrawBackfaces = drawBackfacesPlug.asBool()
                
            try:
                color = lambertShader.findPlug("color", True)
                material.DiffuseMapFilename = GetFileTextureName(color)
                
                # If there is a texture and my diffuse color is zero, make it one
                if IsZero(material.DiffuseColor) == True and not IsNoneOrEmpty(material.DiffuseMapFilename):
                    material.DiffuseColor.r = material.DiffuseColor.g = material.DiffuseColor.b = 1
                
                try:
                    texturePlug = GetConnectedPlug(color, "outColor", OpenMaya.MFn.kFileTexture)
                    textureNode = OpenMaya.MFnDependencyNode(texturePlug.node())
                    repeatUV = textureNode.findPlug("repeatUV", True)
                    material.RepeatUV = [repeatUV.child(0).asFloat(), repeatUV.child(0).asFloat()]
                except RuntimeError:
                    material.RepeatUV = [1, 1]
                
            except RuntimeError:
                Nop()
            
            try:
                normalCamera = lambertShader.findPlug("normalCamera", True)
                outNormal = GetConnectedPlug(normalCamera, "outNormal", OpenMaya.MFn.kBump)
                if not outNormal.isNull():
                    bumpValue = OpenMaya.MFnDependencyNode(outNormal.node()).findPlug("bumpValue", True)
                    material.NormalMapFilename = GetFileTextureName(bumpValue)
            except RuntimeError:
                Nop()
        
        # Process phong shader parameters
        if sourceNode.hasFn(OpenMaya.MFn.kPhong):
            phongShader = OpenMaya.MFnPhongShader(sourceNode)
            material.SpecularColor = phongShader.specularColor()
            material.CosinePower = phongShader.cosPower()
            
            try:
                phongShader.findPlug("Reflectivity", True)
            except RuntimeError:
                reflectivityAttributeNumeric = OpenMaya.MFnNumericAttribute()
                reflectivityAttribute = reflectivityAttributeNumeric.create("Reflectivity", "Reflectivity", OpenMaya.MFnNumericData.kFloat)
                reflectivityAttributeNumeric.setMin(0.0)
                reflectivityAttributeNumeric.setMax(1.0)
                reflectivityAttributeNumeric.setDefault(0.0)
                phongShader.addAttribute(reflectivityAttribute)
            finally:
                reflectivityPlug = phongShader.findPlug("Reflectivity", True)
                material.Reflectivity = reflectivityPlug.asFloat()
            
            try:
                specularColor = lambertShader.findPlug("specularColor", True)
                material.SpecularMapFilename = GetFileTextureName(specularColor)
                
                # If there is a texture and my specular color is zero, make it one
                if IsZero(material.SpecularColor) == True and not IsNoneOrEmpty(material.SpecularMapFilename):
                    material.SpecularColor.r = material.SpecularColor.g = material.SpecularColor.b = 1
            except RuntimeError:
                Nop
        
        model.Materials[material.Name] = material;

        # Process the polygons with this material
        ProcessModelMesh(dagPath, component, material, model)
    
    return model

def Run(suppressYayDialog = False, export = True):
    global defFile
    global fileIndentLevel
    global MaxWeights
    
    # Constants
    MaxWeights = 4
    
    # Derived settings
    exportSkinning = export
    exportAnimation = export
    exportModelMeshes = export
    
    # Debug overrides
    if False:
        exportSkinning = True
        exportAnimation = True
        exportModelMeshes = True
    
    # Ensure we are working in the units we want to work in
    Cmds.currentUnit(linear="meter", angle="degree", time="ntsc")
    
    # Get the selection list
    selectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selectionList);
    selectionListDagIter = OpenMaya.MItSelectionList(selectionList, OpenMaya.MFn.kGeometric);

    while not selectionListDagIter.isDone():
        models = []
        fileIndentLevel = 0
        
        # Get the item
        dagPath = OpenMaya.MDagPath()
        mayaObject = OpenMaya.MObject()
        selectionListDagIter.getDagPath(dagPath)
        selectionListDagIter.getDependNode(mayaObject)
        dagNode = OpenMaya.MFnDagNode(dagPath)
        
        inMeshPlug = dagNode.findPlug("inMesh")
        if inMeshPlug.isConnected() == True:
            dgIt = OpenMaya.MItDependencyGraph(inMeshPlug, OpenMaya.MFn.kInvalid, OpenMaya.MItDependencyGraph.kUpstream, OpenMaya.MItDependencyGraph.kDepthFirst, OpenMaya.MItDependencyGraph.kPlugLevel)
            dgIt.disablePruningOnFilter()
            while not dgIt.isDone():
                thisNode = dgIt.thisNode()
                
                if thisNode.apiType() == OpenMaya.MFn.kSkinClusterFilter:
                    skinCluster = OpenMayaAnim.MFnSkinCluster(thisNode)
                    influenceObjects = OpenMaya.MDagPathArray()
                    
                    numInfluenceObjects = skinCluster.influenceObjects(influenceObjects)
                    numOutputGeometries = skinCluster.numOutputConnections()
                    
                    for g in range(numOutputGeometries):
                        index = skinCluster.indexForOutputConnection(g)
                        skinPath = OpenMaya.MDagPath()
                        skinCluster.getPathAtIndex(index, skinPath)
                        gIter = OpenMaya.MItGeometry(skinPath)
                        numVertices = gIter.count()
                        
                        # Process the geometry and materials
                        sys.__stdout__.write("\n\nProcessing geometry and materials ...")
                        
                        model = ProcessModel(skinPath)
                        
                        # Compute weighting information
                        sys.__stdout__.write("\nComputing weighting information ...")
                        
                        model.WeightedVertices = []
                        model.WeightedVertexIndexByPosition = {}
                        
                        for wv in range(numVertices):
                            weightedVertex = WeightedVertex()
                            weightedVertex.Weights = []
                            weightedVertex.Joints = []
                            for mw in range(MaxWeights):
                                weightedVertex.Weights.append(0)
                                weightedVertex.Joints.append(-1)
                            
                            model.WeightedVertices.append(weightedVertex)
                        
                        count = 0
                        while not gIter.isDone():
                            component = gIter.currentItem()
                            weights = OpenMaya.MFloatArray()
                            influenceCount = OpenMaya.MScriptUtil().asUintPtr()
                            skinCluster.getWeights(skinPath, component, weights, influenceCount)
                            influenceCount = OpenMaya.MScriptUtil(influenceCount).asUint()
                            
                            totalCount = 0
                            totalWeight = 0
                            weightedVertex = model.WeightedVertices[count]
                            weightedVertex.Position = OpenMaya.MVector(gIter.position() / 100)
                            weightedVertex.Index = count
                            
                            model.WeightedVertexIndexByPosition[CreateXYZKey(weightedVertex.Position)] = weightedVertex.Index
                            
                            for i in range(influenceCount):
                                weight = weights[i]
                                
                                if weight > -0.0001 and weight < 0.0001:
                                    weight = 0
                                
                                if weight > 1:
                                    weight = 1
                                    
                                if weight < 0:
                                    weight = 0
                                    
                                if totalCount >= MaxWeights:
                                    min = 0
                                    for x in range(totalCount):
                                        if weightedVertex.Weights[min] > weightedVertex.Weights[x]:
                                            mix = x
                                    
                                    if weight > weightedVertex.Weights[min]:
                                        totalWeight = totalWeight - weightedVertex.Weights[min]
                                        totalWeight += weight
                                        weightedVertex.Weights[min] = weight
                                        weightedVertex.Joints[min] = i
                                else:
                                    totalWeight += weight
                                    weightedVertex.Weights[totalCount] = weight
                                    weightedVertex.Joints[totalCount] = i
                                    totalCount = totalCount + 1
                                    
                            if totalWeight > 0:
                                for w in range(totalCount):
                                    weightedVertex.Weights[w] /= totalWeight
                            else:
                                print "OMG! Weight total is zero!"
                            
                            count = count + 1
                            gIter.next()
                        
                        # Check weighting information
                        for modelMeshIndex in range(len(model.ModelMeshes)):
                            modelMesh = model.ModelMeshes[modelMeshIndex]
                            for i in range(len(modelMesh.Points)):
                                key = CreateXYZKey(modelMesh.Points[i])
                                if key in model.WeightedVertexIndexByPosition.keys():
                                    modelMesh.WeightedVertexIndices[i] = model.WeightedVertexIndexByPosition[key]
                                else:
                                    print "Missing weighted vertex reference for %s" % key
                                    modelMesh.WeightedVertexIndices[i] = 0
                                
                        # Compute bind pose
                        sys.__stdout__.write("\nComputing bind pose ...")
                        
                        model.Joints = []
                        model.JointIndexByName = {}
                        
                        for i in range(numInfluenceObjects):
                            joint = Joint()
                            joint.Name = influenceObjects[i].partialPathName()
                            joint.Index = i
                            
                            joint.DagPath = influenceObjects[i]
                            jointTransformFunction = OpenMaya.MFnTransform(joint.DagPath)
                            
                            jointDagNode = OpenMaya.MFnDagNode(joint.DagPath)
                            jointOrientPlug = jointDagNode.findPlug("jointOrient")
                            jointOrientRotation = OpenMaya.MEulerRotation(VectorDegreesToRadians(PlugValueAsMVector(jointOrientPlug))).asQuaternion()
                            
                            rotateOrientPlug = jointDagNode.findPlug("rotateAxis")
                            rotateOrientRotation = OpenMaya.MEulerRotation(VectorDegreesToRadians(PlugValueAsMVector(rotateOrientPlug))).asQuaternion()
                            
                            joint.AbsoluteTransform = jointTransformFunction.transformation().asMatrix()

                            joint.Position = jointTransformFunction.getTranslation(OpenMaya.MSpace.kTransform) / 100
                            joint.Rotation = OpenMaya.MQuaternion()
                            jointTransformFunction.getRotation(joint.Rotation, OpenMaya.MSpace.kTransform)
                            joint.Rotation = rotateOrientRotation * joint.Rotation * jointOrientRotation
                            
                            joint.AbsolutePosition = jointTransformFunction.getTranslation(OpenMaya.MSpace.kWorld) / 100
                            joint.AbsoluteRotation = OpenMaya.MQuaternion()
                            jointTransformFunction.getRotation(joint.AbsoluteRotation, OpenMaya.MSpace.kWorld)
                            joint.AbsoluteRotation = rotateOrientRotation * joint.AbsoluteRotation * jointOrientRotation

                            model.Joints.append(joint)
                            model.JointIndexByName[joint.Name] = joint.Index
                        
                        # Compute joint hierarchy
                        sys.__stdout__.write("\nComputing joint hierarchy for %d joints ..." % len(model.Joints))
                        
                        for i in range(numInfluenceObjects):
                            dagNode = OpenMaya.MFnDagNode(influenceObjects[i])
                            if dagNode.parentCount() > 0:
                                parentName = OpenMaya.MFnDagNode(dagNode.parent(0)).name()
                                if parentName in model.JointIndexByName:
                                    model.Joints[i].ParentIndex = model.JointIndexByName[parentName]
                                    
                        # Compute animation keyframes
                        model.Keyframes = {}
                        for j in range(len(model.Joints)):
                            model.Keyframes[j] = []
                        
                        if exportAnimation == True:
                            sys.__stdout__.write("\nComputing animation keyframes ...")
                            
                            startFrameMTime = OpenMayaAnim.MAnimControl.animationStartTime()
                            endFrameMTime = OpenMayaAnim.MAnimControl.animationEndTime()
                            startFrame = int(math.floor(startFrameMTime.as(OpenMaya.MTime.uiUnit())))
                            endFrame = int(math.ceil(endFrameMTime.as(OpenMaya.MTime.uiUnit())))
                            for f in range(startFrame, endFrame + 1):
                                currentTime = OpenMaya.MTime(f, OpenMaya.MTime.uiUnit())
                                OpenMayaAnim.MAnimControl.setCurrentTime(currentTime)
                                for j in range(len(model.Joints)):
                                    joint = model.Joints[j]
                                    jointTransformFunction = OpenMaya.MFnTransform(joint.DagPath)
                                    
                                    jointDagNode = OpenMaya.MFnDagNode(joint.DagPath)
                                    jointOrientPlug = jointDagNode.findPlug("jointOrient")
                                    jointOrientRotation = OpenMaya.MEulerRotation(VectorDegreesToRadians(PlugValueAsMVector(jointOrientPlug))).asQuaternion()
                                    
                                    rotateOrientPlug = jointDagNode.findPlug("rotateAxis")
                                    rotateOrientRotation = OpenMaya.MEulerRotation(VectorDegreesToRadians(PlugValueAsMVector(rotateOrientPlug))).asQuaternion()
                                    
                                    keyframe = Keyframe()
                                    keyframe.JointIndex = j
                                    keyframe.Frame = f
                                    keyframe.Time = currentTime.as(OpenMaya.MTime.kSeconds)
                                    
                                    keyframe.Position = jointTransformFunction.getTranslation(OpenMaya.MSpace.kTransform) / 100
                                    keyframe.Rotation = OpenMaya.MQuaternion()
                                    jointTransformFunction.getRotation(keyframe.Rotation, OpenMaya.MSpace.kTransform)
                                    keyframe.Rotation = rotateOrientRotation * keyframe.Rotation * jointOrientRotation
                                    
                                    keyframe.AbsolutePosition = jointTransformFunction.getTranslation(OpenMaya.MSpace.kWorld) / 100
                                    keyframe.AbsoluteRotation = OpenMaya.MQuaternion()
                                    jointTransformFunction.getRotation(keyframe.AbsoluteRotation, OpenMaya.MSpace.kWorld)
                                    keyframe.AbsoluteRotation = rotateOrientRotation * keyframe.AbsoluteRotation * jointOrientRotation
                                    
                                    model.Keyframes[j].append(keyframe)
                            
                        model.HasSkinningData = True
                        models.append(model)
                    
                dgIt.next()
        
        if len(models) == 0:
            sys.__stdout__.write("\n\nNo skinning data!")
            sys.__stdout__.write("\nProcessing geometry and materials ...")
            model = ProcessModel(dagPath)
            
            # Write up dummy weighting information
            for modelMeshIndex in range(len(model.ModelMeshes)):
                modelMesh = model.ModelMeshes[modelMeshIndex]
                for i in range(len(modelMesh.Points)):
                    modelMesh.WeightedVertexIndices[i] = -1
            
            model.HasSkinningData = False
            models.append(model)
        
        if export == True:
            directoryName = os.path.dirname(Cmds.file(q=True, sn=True))
            filePath = "%s/%s.modeldef" % (directoryName, dagPath.fullPathName().split("|")[-2])
            defFile = open(filePath, "w")
            
            # Xml Writer
            xmlWriter = Com.XmlWriter(defFile)
            
            if (len(models) > 1):
                sys.__stdout__.write("\n[Warning] More than one model in skin cluster. Not quite supported yet due to time constraints.")
            
            for model in models:
                xmlWriter.WriteElementStart("IntermediateModelDef")
                if model.HasSkinningData == True:
                    xmlWriter.WriteAttribute("HasSkinningData", "true")
                else:
                    xmlWriter.WriteAttribute("HasSkinningData", "false")
                xmlWriter.WriteElementEnd()
                
                if exportSkinning == True and model.HasSkinningData == True:
                    # Export bind pose
                    sys.__stdout__.write("\nWriting bind pose ...")
                    
                    xmlWriter.WriteStartElement("BindPose")
                    for joint in model.Joints:
                        xmlWriter.WriteElementStart("IntermediateJoint")
                        xmlWriter.WriteAttribute("Name", joint.Name)
                        xmlWriter.WriteAttribute("Index", joint.Index)
                        xmlWriter.WriteAttribute("ParentIndex", joint.ParentIndex)
                        xmlWriter.WriteElementEnd()
                        xmlWriter.WriteXYZElement("Position", joint.Position)
                        xmlWriter.WriteXYZWElement("Rotation", joint.Rotation)
                        xmlWriter.WriteXYZElement("AbsolutePosition", joint.AbsolutePosition)
                        xmlWriter.WriteXYZWElement("AbsoluteRotation", joint.AbsoluteRotation)
                        xmlWriter.WriteEndElement("IntermediateJoint")
                    xmlWriter.WriteEndElement("BindPose")
                    
                    # Export weights
                    sys.__stdout__.write("\nWriting weights ...")
                    
                    xmlWriter.WriteElementStart("WeightedVertices")
                    xmlWriter.WriteAttribute("Count", len(model.WeightedVertices))
                    xmlWriter.WriteElementEnd()
                    
                    for i in range(len(model.WeightedVertices)):
                        xmlWriter.WriteElementStart("IntermediateWeightedVertex")
                        xmlWriter.WriteAttribute("Index", model.WeightedVertices[i].Index)
                        xmlWriter.WriteElementEnd()
                        xmlWriter.WriteXYZElement("Position", model.WeightedVertices[i].Position)
                        xmlWriter.WriteStartElement("JointWeights")
                        for w in range(len(model.WeightedVertices[i].Weights)):
                            xmlWriter.WriteElementStart("IntermediateJointWeight")
                            xmlWriter.WriteAttribute("JointIndex", model.WeightedVertices[i].Joints[w])
                            xmlWriter.WriteAttribute("Weight", model.WeightedVertices[i].Weights[w])
                            xmlWriter.WriteElementEnd(True)
                        xmlWriter.WriteEndElement("JointWeights")
                        xmlWriter.WriteEndElement("IntermediateWeightedVertex")
                    
                    xmlWriter.WriteEndElement("WeightedVertices")
                
                if exportAnimation == True and model.HasSkinningData == True:
                    # Export animation keyframes
                    sys.__stdout__.write("\nWriting animation keyframes ...")
                    
                    xmlWriter.WriteStartElement("AnimationKeyframes")
                    for jointIndex in model.Keyframes.keys():
                        #sys.__stdout__.write("\nExporting %d keyframes for joint %s (%d/%d) ..." % (len(model.Keyframes[jointIndex]), model.Joints[jointIndex].Name, jointIndex + 1, len(model.Keyframes)))
                        for keyframe in model.Keyframes[jointIndex]:
                            xmlWriter.WriteElementStart("IntermediateKeyframe")
                            xmlWriter.WriteAttribute("JointIndex", keyframe.JointIndex)
                            xmlWriter.WriteAttribute("Frame", keyframe.Frame)
                            xmlWriter.WriteAttribute("Time", keyframe.Time)
                            xmlWriter.WriteElementEnd()
                            xmlWriter.WriteXYZElement("Position", keyframe.Position)
                            xmlWriter.WriteXYZWElement("Rotation", keyframe.Rotation)
                            xmlWriter.WriteXYZElement("AbsolutePosition", keyframe.AbsolutePosition)
                            xmlWriter.WriteXYZWElement("AbsoluteRotation", keyframe.AbsoluteRotation)
                            xmlWriter.WriteEndElement("IntermediateKeyframe")
                    
                    xmlWriter.WriteEndElement("AnimationKeyframes")
                
                if exportModelMeshes == True:
                    # Export model meshes
                    sys.__stdout__.write("\nWriting model meshes ...")
                    
                    xmlWriter.WriteStartElement("ModelMeshes")
                    for modelMeshIndex in range(len(model.ModelMeshes)):
                        modelMesh = model.ModelMeshes[modelMeshIndex]
                        
                        xmlWriter.WriteElementStart("IntermediateModelMeshDef")
                        xmlWriter.WriteAttribute("Name", "%s|%s" % (modelMesh.Name, modelMeshIndex))
                        xmlWriter.WriteElementEnd()
                        
                        # Export material
                        xmlWriter.WriteElementStart("Material")
                        xmlWriter.WriteAttribute("Name", modelMesh.Material.Name)
                        xmlWriter.WriteElementEnd()
                        
                        xmlWriter.WriteXYZElement("DiffuseColor", modelMesh.Material.DiffuseColor)
                        xmlWriter.WriteXYZElement("SpecularColor", modelMesh.Material.SpecularColor)
                        xmlWriter.WriteValueElement("DiffuseCoeff", modelMesh.Material.DiffuseCoeff)
                        xmlWriter.WriteValueElement("CosinePower", modelMesh.Material.CosinePower)
                        xmlWriter.WriteValueElement("Transparency", modelMesh.Material.Transparency)
                        xmlWriter.WriteValueElement("DiffuseMapFilename", modelMesh.Material.DiffuseMapFilename)
                        xmlWriter.WriteValueElement("NormalMapFilename", modelMesh.Material.NormalMapFilename)
                        xmlWriter.WriteValueElement("SpecularMapFilename", modelMesh.Material.SpecularMapFilename)
                        xmlWriter.WriteValueElement("LightmapFilename", modelMesh.Material.LightmapFilename)
                        xmlWriter.WriteValueElement("UseAlpha", modelMesh.Material.UseAlpha)
                        xmlWriter.WriteValueElement("DrawBackfaces", modelMesh.Material.DrawBackfaces)
                        
                        xmlWriter.WriteElementStart("RepeatUV")
                        xmlWriter.WriteAttribute("X", modelMesh.Material.RepeatUV[0])
                        xmlWriter.WriteAttribute("Y", modelMesh.Material.RepeatUV[1])
                        xmlWriter.WriteElementEnd(True)
                        
                        xmlWriter.WriteEndElement("Material")
                        
                        # Export geometry
                        xmlWriter.WriteElementStart("Vertices")
                        xmlWriter.WriteAttribute("Count", len(modelMesh.Points))
                        xmlWriter.WriteElementEnd()

                        for i in range(len(modelMesh.Points)):
                            xmlWriter.WriteElementStart("IntermediateVertex")
                            if model.HasSkinningData == True:
                                xmlWriter.WriteAttribute("WeightedVertexIndex", modelMesh.WeightedVertexIndices[i])
                            xmlWriter.WriteElementEnd()
                            
                            if model.HasSkinningData == False:
                                xmlWriter.WriteXYZElement("Position", modelMesh.Points[i])
                            xmlWriter.WriteXYZElement("Normal", modelMesh.Normals[i])
                            xmlWriter.WriteXYZElement("Tangent", modelMesh.Tangents[i])
                            xmlWriter.WriteXYZElement("Binormal", modelMesh.Binormals[i])
                            
                            uvSetKeys = modelMesh.UVSets.keys()
                            xmlWriter.WriteElementStart("TextureCoordinate0")
                            if len(modelMesh.UVSets) > 0:
                                xmlWriter.WriteAttribute("X", modelMesh.UVSets[uvSetKeys[0]].Us[i] * modelMesh.Material.RepeatUV[0])
                                xmlWriter.WriteAttribute("Y", modelMesh.UVSets[uvSetKeys[0]].Vs[i] * modelMesh.Material.RepeatUV[1])
                            xmlWriter.WriteElementEnd(True)
                            
                            xmlWriter.WriteElementStart("TextureCoordinate1")
                            if len(modelMesh.UVSets) > 1:
                                xmlWriter.WriteAttribute("X", modelMesh.UVSets[uvSetKeys[1]].Us[i] * modelMesh.Material.RepeatUV[0])
                                xmlWriter.WriteAttribute("Y", modelMesh.UVSets[uvSetKeys[1]].Vs[i] * modelMesh.Material.RepeatUV[1])
                            xmlWriter.WriteElementEnd(True)
                            
                            xmlWriter.WriteEndElement("IntermediateVertex")
                        
                        xmlWriter.WriteEndElement("Vertices")
                        
                        indicesCsv = ""
                        for i in range(len(modelMesh.Indices)):
                            indicesCsv += str(modelMesh.Indices[i]) + ", "
                        
                        xmlWriter.WriteElementStart("Indices")
                        xmlWriter.WriteAttribute("Count", len(modelMesh.Indices))
                        xmlWriter.WriteAttribute("Values", indicesCsv);
                        xmlWriter.WriteElementEnd(True)
                        
                        xmlWriter.WriteEndElement("IntermediateModelMeshDef")
                    
                    xmlWriter.WriteEndElement("ModelMeshes")
                
                xmlWriter.WriteEndElement("IntermediateModelDef")
            
            defFile.close()
            sys.__stdout__.write("\nExported to %s successfully!" % (filePath))
        
        # Process next item
        selectionListDagIter.next()
    
    if suppressYayDialog == False:
        Cmds.confirmDialog(title="ModelDef Exporter for Maya", message="Processing complete!", button=["Yay!"])
