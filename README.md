# Greymind ModelDef
Skeletal animation file format with Maya exporter and XNA importer

# Format
ModelDef is a simple, easy to use file format that supports:
* Polygons
* Lambert and phong shaders
* Textures and UV Maps
* Skeletal animations
* Skinning

# Installation
Place the `ModelDefExporter.py` and `Common.py` files in `Documents\maya\<maya version>\scripts` folder.

# Usage

## Export
To invoke this script, use the following commands in the python mode of the script editor:
```
import ModelDefExporter as Mde
reload(Mde)
Mde.Run()
```
You may middle-mouse drag these lines to the shelf to create a shortcut toolbar button.

## Import
Copy all the files to your project and use the `ModelDef - Greymind Framework` processor for your `.modeldef` files via the properties window.

# Custom Data
You might also want the custom data importer and exporter to manage additional information. You can get it from [https://github.com/greymind/CustomData](https://github.com/greymind/CustomData)

# Team
* [Balakrishnan (Balki) Ranganathan](http://greymind.com)

# License
* MIT
