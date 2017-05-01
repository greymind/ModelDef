using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;
using System.Xml;
using System.Xml.Serialization;

namespace Core.Pipeline
{
    public struct XmlVector2
    {
        [XmlAttribute]
        public Single X;

        [XmlAttribute]
        public Single Y;

        [XmlIgnore]
        public static XmlVector2 Zero = new XmlVector2(0, 0);

        [XmlIgnore]
        public static XmlVector2 One = new XmlVector2(1, 1);

        public XmlVector2(Single x, Single y)
        {
            X = x; Y = y;
        }

        public XmlVector2(Vector2 vector)
        {
            X = vector.X;
            Y = vector.Y;
        }

        public void SetZero()
        {
            X = Y = 0;
        }

        public Boolean IsZero()
        {
            return X == 0 && Y == 0;
        }

        public void SetOne()
        {
            X = Y = 1;
        }

        public Boolean IsOne()
        {
            return X == 1 && Y == 1;
        }

        public static Vector2 operator +(Vector2 vector2, XmlVector2 xmlVector2)
        {
            return new Vector2(vector2.X + xmlVector2.X, vector2.Y + xmlVector2.Y);
        }

        public Vector2 ToVector2()
        {
            return new Vector2(X, Y);
        }

        public override string ToString()
        {
            return ToVector2().ToString();
        }
    }
}
