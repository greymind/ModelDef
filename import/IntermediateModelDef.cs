using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Core.Animation;
using System.Xml.Serialization;
using System.IO;
using Core.Utilities;

namespace Core.Pipeline
{
    public class IntermediateModelDef : LoadSaver<IntermediateModelDef>
    {
        public List<IntermediateModelMeshDef> ModelMeshes = new List<IntermediateModelMeshDef>();
        public List<IntermediateJoint> BindPose = new List<IntermediateJoint>();
        public List<IntermediateWeightedVertex> WeightedVertices = new List<IntermediateWeightedVertex>();
        public List<IntermediateKeyframe> AnimationKeyframes = new List<IntermediateKeyframe>();

        [XmlAttribute]
        public Boolean HasSkinningData = false;

        public IntermediateModelDef()
        {
            CreateOnFileNotExists = false;
        }
    }
}
