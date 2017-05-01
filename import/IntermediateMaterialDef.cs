using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Content.Pipeline.Graphics;
using Microsoft.Xna.Framework.Content.Pipeline;
using System.Xml.Serialization;
using Core.Utilities;

namespace Core.Pipeline
{
	public class IntermediateMaterialDef
	{
        [XmlAttribute]
        public String Name = String.Empty;

        public XmlVector3 DiffuseColor = Color.White.ToXmlVector3();
        public XmlValue DiffuseCoeff = XmlValue.Zero;
        public XmlVector3 SpecularColor = Color.Black.ToXmlVector3();
        public XmlValue CosinePower = XmlValue.Zero;
        public XmlValue Transparency = XmlValue.Zero;
        public XmlValue DiffuseMapFilename = XmlValue.Empty;
        public XmlValue NormalMapFilename = XmlValue.Empty;
        public XmlValue SpecularMapFilename = XmlValue.Empty;
        public XmlValue UseAlpha = XmlValue.False;
        public XmlValue DrawBackfaces = XmlValue.False;
        public XmlValue Reflectivity = XmlValue.Zero;
	}
}
