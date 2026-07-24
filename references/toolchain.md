# Toolchain And Initial Questions

## First Response

Before conversion, explain that FSX BGLs are not one format: objects, airport records, terrain/CVX, and legacy ground polygons require different tools. Ask for all paths together.

Chinese prompt:

> 开始前请安装或提供以下路径：源地景、独立输出目录、FS2004版 BGLComp SDK、FS2004版 MakeMDL SDK、FS2004 Terrain SDK 的 ImageTool、ModelConverterX、ADE、NewBglAnalyze/BGLAnalyze、SCASM，以及可选的 DXTBmp。请同时确认已安装 MCX 所需的 .NET Desktop Runtime 和 Python 的 Pillow、pywinauto。输出目录不能是原地景目录。

English prompt:

> Before starting, install or provide paths for the source scenery, a separate output directory, the FS2004 BGLComp SDK, FS2004 MakeMDL SDK, ImageTool from the FS2004 Terrain SDK, ModelConverterX, ADE, NewBglAnalyze/BGLAnalyze, SCASM, and optionally DXTBmp. Also confirm the .NET Desktop Runtime required by MCX and Python packages Pillow and pywinauto. The output directory must not be the source directory.

## Paths To Collect

- Source root containing `Scenery` and `Texture`.
- Output root, normally `<source>/convert_test` or another new folder.
- `ModelConverterX.dll` and its containing directory.
- `BGLComp.exe`; verify `bglcomp.xsd` is beside it.
- `MakeMDL.exe` and `modeldef.xml`/parts XML.
- `ImageTool.exe`.
- `scasm.exe`.
- ADE executable or installation directory.
- NewBglAnalyze/BGLAnalyze executable.
- Optional `DXTBmp.exe`.
- `dotnet.exe`, normally `C:\Program Files\dotnet\dotnet.exe`.

Test each path with a read-only existence check before proceeding. Search user-provided SDK roots for expected filenames when only a directory is supplied. Do not silently substitute FSX SDK executables for FS2004 executables.

## Tool Roles And Limits

- MCX reads FSX object/placement BGLs and writes FS2004 `BGL_9`; it does not reliably recover airport or terrain/CVX records.
- BGLComp compiles FS2004 airport XML.
- MakeMDL is required by MCX for FS2004 model output.
- ImageTool writes FS2004 extended BMP and mipmaps.
- NewBglAnalyze may produce syntactically valid but incomplete airport XML.
- ADE is the authoritative fallback for recovering a complete airport definition.
- SCASM compiles FS2002-style ground polygons that FS2004 can display.
- DXTBmp is for manual inspection/correction, not required for batch conversion.

## Texture Rules

Decode DDS with Pillow, convert to RGBA, flip vertically, resize dimensions above 1024 with aspect ratio preserved, then call ImageTool with mipmap generation. Use DXT1 for opaque/binary-alpha textures and DXT3 for variable alpha. A full 1024x1024 DXT1 extended BMP data payload is about 699,048 bytes and demonstrates mip levels down to 4x4; do not diagnose missing mipmaps from distant disappearance without checking both file size and SCA visibility.
