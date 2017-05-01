using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;
using System.Xml;
using System.Xml.Serialization;

namespace Core.Pipeline
{
    public class XmlCsv
    {
        private String values = "0";

        [XmlAttribute]
        public String Values
        {
            get
            {
                return values.Trim();
            }
            set
            {
                values = value;
            }
        }

        [XmlIgnore]
        public static XmlCsv Zero = new XmlCsv("0");

        [XmlIgnore]
        public static XmlCsv One = new XmlCsv("1");

        [XmlIgnore]
        public static XmlCsv Empty = new XmlCsv("");

        public XmlCsv() { }

        public XmlCsv(String values)
        {
            Values = values;
        }

        public Int32[] ToInt32Array()
        {
            String[] splitCsv = Values.Split(new char[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
            Int32[] resultArray = new Int32[splitCsv.Length];

            for (int i = 0; i < splitCsv.Length; ++i)
            {
                resultArray[i] = Int32.Parse(splitCsv[i].Trim());
            }

            return resultArray;
        }

        public UInt32[] ToUInt32Array()
        {
            String[] splitCsv = Values.Split(new char[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
            UInt32[] resultArray = new UInt32[splitCsv.Length];

            for (int i = 0; i < splitCsv.Length; ++i)
            {
                resultArray[i] = UInt32.Parse(splitCsv[i].Trim());
            }

            return resultArray;
        }
    }
}
