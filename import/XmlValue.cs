using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;
using System.Xml;
using System.Xml.Serialization;

namespace Core.Pipeline
{
    public class XmlValue
    {
        private String value = "0";

        [XmlAttribute]
        public String Value
        {
            get
            {
                return value.Trim();
            }
            set
            {
                this.value = value;
            }
        }

        [XmlIgnore]
        public static XmlValue Zero = new XmlValue("0");

        [XmlIgnore]
        public static XmlValue One = new XmlValue("1");

        [XmlIgnore]
        public static XmlValue Empty = new XmlValue("");

        [XmlIgnore]
        public static XmlValue False = new XmlValue("False");

        [XmlIgnore]
        public static XmlValue True = new XmlValue("True");

        public XmlValue() { }

        public XmlValue(String value)
        {
            Value = value;
        }

        public UInt32 AsUInt32()
        {
            return UInt32.Parse(Value);
        }

        public Single AsSingle()
        {
            return Single.Parse(Value);
        }

        public String AsString()
        {
            return value;
        }

        public Boolean AsBoolean()
        {
            return Boolean.Parse(value.ToLower());
        }
    }
}
