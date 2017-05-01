using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework.Content.Pipeline;
using Microsoft.Xna.Framework.Content.Pipeline.Graphics;
using System.Diagnostics;
using Microsoft.Xna.Framework;
using System.IO;
using Core.Graphics.Primitives;
using System.ComponentModel;
using Core.Content;
using Core.Animation;

namespace Core.Pipeline
{
    [ContentImporter(".modeldef", CacheImportedData = true, DefaultProcessor = "ModelDefProcessor", DisplayName = "ModelDef - Cosmopolis Framework")]
    public class ModelDefImporter : ContentImporter<IntermediateModelDef>
    {
        #region Debug

        static bool debugged = false;

        private static void DebugNow()
        {
            if (!debugged)
            {
                Debugger.Launch();
            }

            debugged = true;
        }

        #endregion

        String sourceFilename;
        ContentImporterContext importerContext;

        public override IntermediateModelDef Import(string filename, ContentImporterContext context)
        {
            sourceFilename = filename;
            importerContext = context;

            //DebugNow();

            IntermediateModelDef imd = new IntermediateModelDef();
            imd.Path = Path.Combine(context.IntermediateDirectory, filename);
            IntermediateModelDef.Load(ref imd);

            return imd;
        }
    }

    [ContentProcessor(DisplayName = "ModelDef - Greymind Framework")]
    class ModelDefProcessor : ContentProcessor<IntermediateModelDef, IntermediateModel>
    {
        #region Debug

        static bool debugged = false;

        private static void DebugNow()
        {
            if (!debugged)
            {
                Debugger.Launch();
            }

            debugged = true;
        }

        #endregion

        #region Properties

        [DisplayName("Scale")]
        [DefaultValue(1.0f)]
        [Description("Model Scale")]
        public float Scale { get; set; }

        #endregion

        IntermediateModel model;

        public override IntermediateModel Process(IntermediateModelDef input, ContentProcessorContext context)
        {
            Scale = Scale == 0.0f ? 1.0f : Scale;

            model = new IntermediateModel();

            String prefix = context.OutputDirectory;
            String wholeName = context.OutputFilename;
            String partialName = wholeName.Substring(prefix.Length);
            String modelName = partialName.Replace("\\\\", "\\");
            modelName = modelName.Replace(".xnb", "").Replace(".XNB", "");

            // Get the custom data associated with the model
            model.CustomData = ProcessCustomData(context);

            var scaleCustomData = model.CustomData["Scale"];
            if (scaleCustomData != null)
            {
                Scale = Convert.ToSingle(scaleCustomData.Value);
            }

            List<IntermediateModelMesh> imms = new List<IntermediateModelMesh>();
            for (int i = 0; i < input.ModelMeshes.Count; ++i)
            {
                var modelMesh = input.ModelMeshes[i];

                IntermediateModelMesh imm = new IntermediateModelMesh();
                ModelMeshVertex[] vertices = new ModelMeshVertex[modelMesh.Vertices.Length];
                WeightedVertex[] origVertices = new WeightedVertex[modelMesh.Vertices.Length];

                //DebugNow();

                for (int j = 0; j < modelMesh.Vertices.Length; ++j)
                {
                    if (input.HasSkinningData)
                    {
                        var intermediateWeightedVertex = input.WeightedVertices[modelMesh.Vertices[j].WeightedVertexIndex];
                        vertices[j].Position = Vector3.Transform(intermediateWeightedVertex.Position.ToVector3(), Matrix.CreateScale(Scale));

                        origVertices[j].Weight0 = new Core.Graphics.Primitives.BoneWeight();
                        origVertices[j].Weight0.BoneIndex = intermediateWeightedVertex.JointWeights[0].JointIndex;
                        origVertices[j].Weight0.Weight = intermediateWeightedVertex.JointWeights[0].Weight;

                        origVertices[j].Weight1 = new Core.Graphics.Primitives.BoneWeight();
                        origVertices[j].Weight1.BoneIndex = intermediateWeightedVertex.JointWeights[1].JointIndex;
                        origVertices[j].Weight1.Weight = intermediateWeightedVertex.JointWeights[1].Weight;

                        origVertices[j].Weight2 = new Core.Graphics.Primitives.BoneWeight();
                        origVertices[j].Weight2.BoneIndex = intermediateWeightedVertex.JointWeights[2].JointIndex;
                        origVertices[j].Weight2.Weight = intermediateWeightedVertex.JointWeights[2].Weight;

                        origVertices[j].Weight3 = new Core.Graphics.Primitives.BoneWeight();
                        origVertices[j].Weight3.BoneIndex = intermediateWeightedVertex.JointWeights[3].JointIndex;
                        origVertices[j].Weight3.Weight = intermediateWeightedVertex.JointWeights[3].Weight;
                    }
                    else
                    {
                        vertices[j].Position = Vector3.Transform(modelMesh.Vertices[j].Position.ToVector3(), Matrix.CreateScale(Scale));
                    }

                    vertices[j].Normal = Vector3.TransformNormal(modelMesh.Vertices[j].Normal.ToVector3(), Matrix.CreateScale(Scale));
                    vertices[j].TextureCoordinate0 = modelMesh.Vertices[j].TextureCoordinate0.ToVector2();
                    vertices[j].Tangent = modelMesh.Vertices[j].Tangent.ToVector3();
                    vertices[j].Binormal = modelMesh.Vertices[j].Binormal.ToVector3();
                }

                OpaqueDataDictionary settings = new OpaqueDataDictionary();
                settings["GenerateMipmaps"] = true;

                IntermediateMaterial im = new IntermediateMaterial();
                im.Name = modelMesh.Material.Name;
                im.DiffuseColor = modelMesh.Material.DiffuseColor.ToVector3();
                im.SpecularColor = modelMesh.Material.SpecularColor.ToVector3();
                im.SpecularExp = modelMesh.Material.CosinePower.AsSingle();
                im.Transparency = modelMesh.Material.Transparency.AsSingle();
                im.UseAlpha = modelMesh.Material.UseAlpha.AsBoolean();
                im.DrawBackfaces = modelMesh.Material.DrawBackfaces.AsBoolean();
                im.Reflectivity = modelMesh.Material.Reflectivity.AsSingle();

                //DebugNow();

                im.DiffuseMapName = modelMesh.Material.DiffuseMapFilename.AsString();
                if (!String.IsNullOrEmpty(im.DiffuseMapName))
                {
                    //im.DiffuseMapReference = context.BuildAsset<TextureContent, TextureContent>(
                    //    new ExternalReference<TextureContent>(
                    //        Path.Combine(Path.GetDirectoryName(input.Path), im.DiffuseMapName)), "TextureProcessor", settings, null, null);
                }

                im.NormalMapName = modelMesh.Material.NormalMapFilename.AsString();
                if (!String.IsNullOrEmpty(im.NormalMapName))
                {
                    //im.BumpMapReference = context.BuildAsset<TextureContent, TextureContent>(
                    //    new ExternalReference<TextureContent>(
                    //        Path.Combine(Path.GetDirectoryName(input.Path), im.BumpMapName)), "TextureProcessor", settings, null, null);
                }

                im.SpecularMapName = modelMesh.Material.SpecularMapFilename.AsString();
                if (!String.IsNullOrEmpty(im.SpecularMapName))
                {
                    //im.SpecularMapReference = context.BuildAsset<TextureContent, TextureContent>(
                    //    new ExternalReference<TextureContent>(
                    //        Path.Combine(Path.GetDirectoryName(input.Path), im.SpecularMapName)), "TextureProcessor", settings, null, null);
                }

                imm.Indices = modelMesh.Indices.ToInt32Array();
                for (int k = 0; k <= imm.Indices.Length - 3; k += 3)
                {
                    var temp = imm.Indices[k];
                    imm.Indices[k] = imm.Indices[k + 2];
                    imm.Indices[k + 2] = temp;
                }

                imm.Vertices = vertices;
                imm.OriginalVertices = origVertices;
                imm.BoundingSphere = BoundingSphere.CreateFromPoints(vertices.Select(v => v.Position));
                imm.BoundingBox = BoundingBox.CreateFromPoints(vertices.Select(v => v.Position));
                imm.Material = im;

                imms.Add(imm);
            }

            // Animation stuff
            List<Matrix> bindPose = new List<Matrix>();
            List<Matrix> inverseBindPose = new List<Matrix>();
            List<int> skeletonHierarchy = new List<int>();
            IDictionary<string, int> boneMap = new Dictionary<string, int>();
            IList<String> boneNames = new List<String>(input.BindPose.Count);

            for (int i = 0; i < input.BindPose.Count; boneNames.Add(String.Empty), ++i) ;

            //DebugNow();

            foreach (var joint in input.BindPose)
            {
                Matrix transform = Matrix.CreateFromQuaternion(joint.Rotation.ToQuaternion()) * joint.Position.ToTranslationMatrix();
                transform.Translation *= Scale;

                Matrix absoluteTransform = Matrix.CreateFromQuaternion(joint.AbsoluteRotation.ToQuaternion()) *
                    joint.AbsolutePosition.ToTranslationMatrix();
                absoluteTransform.Translation *= Scale;

                bindPose.Add(transform);
                inverseBindPose.Add(Matrix.Invert(absoluteTransform));
                skeletonHierarchy.Add(joint.ParentIndex);
                boneNames[joint.Index] = joint.Name;
                boneMap.Add(joint.Name, joint.Index);
            }

            var animationClips = ProcessAnimations(input.AnimationKeyframes, input.BindPose, boneNames);
            var skinningData = new SkinningData(bindPose, inverseBindPose, skeletonHierarchy, boneMap, boneNames, modelName);
            var animations = PrepareAnimations(animationClips, skinningData, context);

            model.ModelMeshes = imms.ToArray();
            model.AnimationMap = animations;
            model.SkinningData = skinningData;
            model.BoundingSphere = BoundingSphere.CreateFromPoints(imms.SelectMany(m => m.Vertices.Select(v => v.Position)));
            model.BoundingBox = BoundingBox.CreateFromPoints(imms.SelectMany(m => m.Vertices.Select(v => v.Position)));

            return model;
        }

        private CustomData ProcessCustomData(ContentProcessorContext context)
        {
            String sourceDir = SourceDirFromContext(context);
            String assetName = Path.GetFileNameWithoutExtension(context.OutputFilename);

            CustomData customData = new CustomData();
            customData.Path = Path.Combine(sourceDir, "CustomData.xml");
            CustomData.Load(ref customData);

            return customData;
        }

        private String SourceDirFromContext(ContentProcessorContext context)
        {
            String intermediate = context.IntermediateDirectory;
            String fileName = Path.GetFileNameWithoutExtension(context.OutputFilename);
            String assetPath = context.OutputFilename.Substring(context.OutputDirectory.Length);
            int lastContentIndex = intermediate.LastIndexOf("Content");
            String contentDir = intermediate.Substring(0, lastContentIndex + ("Content").Length);

            String sourceFile = Path.Combine(contentDir, assetPath);
            String sourceDir = Path.GetFullPath(sourceFile).Replace(Path.GetFileName(sourceFile), "");

            return sourceDir;
        }

        private TimeSpan FrameNumberToTimeSpan(int frameNumber)
        {
            // Assumes NTSC (30fps) mode in Maya
            const float frameRate = 1f / 30f;
            return TimeSpan.FromSeconds(frameNumber * frameRate);
        }

        private Dictionary<string, AnimationClip> ProcessAnimations(List<IntermediateKeyframe> animations,
            List<IntermediateJoint> joints, IList<string> boneNames)
        {
            var animationClips = new Dictionary<string, AnimationClip>();

            List<Keyframe> keyframes = new List<Keyframe>();
            for (int i = 0; i < animations.Count; ++i)
            {
                var keyframe = animations[i];
                var transform = Matrix.CreateFromQuaternion(keyframe.Rotation.ToQuaternion()) * keyframe.Position.ToTranslationMatrix();
                transform.Translation *= Scale;

                keyframes.Add(new Keyframe(keyframe.JointIndex, boneNames[keyframe.JointIndex], TimeSpan.FromSeconds(keyframe.Time),
                    transform));
            }
            keyframes.Sort();

            CustomData moveLister = model.CustomData["MoveLister"];

            if (moveLister != null)
            {
                int totalMoves = int.Parse(moveLister["MoveLister.totalMoves"].Value);
                for (int a = 0; a < totalMoves; ++a)
                {
                    String moveName = moveLister["MoveLister.move" + a + "Name"].Value;
                    int moveMin = int.Parse(moveLister["MoveLister.move" + a + "Min"].Value);
                    int moveMax = int.Parse(moveLister["MoveLister.move" + a + "Max"].Value);
                    TimeSpan moveMinTime = FrameNumberToTimeSpan(moveMin);
                    TimeSpan moveMaxTime = FrameNumberToTimeSpan(moveMax);

                    List<Keyframe> clipKeyframes = new List<Keyframe>();
                    foreach (Keyframe keyframe in keyframes)
                    {
                        if (keyframe.Time >= moveMinTime && keyframe.Time <= moveMaxTime)
                        {
                            clipKeyframes.Add(keyframe);
                        }
                    }
                    animationClips.Add(moveName, new AnimationClip(moveMaxTime - moveMinTime, clipKeyframes));
                }
            }

            return animationClips;
        }

        /// <summary>
        /// Export the animation clip meta data and spit to xml
        /// </summary>
        private Dictionary<String, AnimationData> PrepareAnimations(Dictionary<string, AnimationClip> animationClips,
            SkinningData skinningData, ContentProcessorContext context)
        {
            Dictionary<String, AnimationData> animationMap = new Dictionary<String, AnimationData>();
            String sourceDir = SourceDirFromContext(context);
            String assetName = Path.GetFileNameWithoutExtension(context.OutputFilename);

            AnimationGroupType groupType = AnimationGroupType.Base;
            ChannelBlendOperation blendOp = ChannelBlendOperation.Exclusive;
            TimeSpan blendIn = TimeSpan.FromSeconds(0.3571);
            TimeSpan blendOut = TimeSpan.FromSeconds(0.3571);

            float[] defaultWeights = new float[skinningData.BindPose.Count];
            for (int i = 0; i < defaultWeights.Length; defaultWeights[i] = 1.0f, ++i) ;

            //DebugNow();

            foreach (var keyValue in animationClips)
            {
                String name = keyValue.Key;
                AnimationClip clip = keyValue.Value;

                String xmlFile = Path.Combine(sourceDir, assetName + "_" + name + ".xml");
                AnimationData animData = AnimationHelpers.DeserializeAnimationData(xmlFile);

                if (animData == null || animData.NumBones != skinningData.BindPose.Count)
                {
                    animData = new Core.Animation.AnimationData(name, Scale, clip,
                        skinningData.BindPose.Count, skinningData.BoneMap, defaultWeights, groupType, blendOp, blendIn, blendOut);
                    AnimationHelpers.SerializeAnimationData(animData, xmlFile);
                }

                // Overrides, not stored in Xml right now
                animData.BoneMap = (Dictionary<String, Int32>)skinningData.BoneMap;
                animData.AnimationClip = clip;

                animationMap.Add(animData.Name, animData);
            }

            return animationMap;
        }
    }
}
